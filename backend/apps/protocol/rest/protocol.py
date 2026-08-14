"""REST / API protocol implementation.

First-call: single HTTP request per user question.
Multi-step chain support is stubbed in QueryPlan.payload.steps for future extension.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional, Sequence
from urllib.parse import urljoin

import httpx
import orjson

from apps.protocol.base import (
    CAP_CONF_OWNED_RESOURCES,
    CAP_OPENAPI_IMPORT,
    BaseProtocol,
    PromptBundle,
    QueryPlan,
    QueryResult,
    SchemaSnapshot,
)
from apps.protocol.rest.conf import (
    ApiAuthConfig,
    ApiAuthType,
    ApiDatasourceConf,
    ApiEndpointDef,
)
from apps.protocol.rest.ssrf import check_ssrf
from common.core.config import settings
from common.error import SingleMessageError
from common.utils.utils import SQLBotLogUtil

# Envelope keys treated as transport metadata, not row business columns.
_ENVELOPE_META_KEYS = {
    "code",
    "status",
    "statusCode",
    "status_code",
    "errcode",
    "errCode",
    "message",
    "msg",
    "error",
    "errorMessage",
    "error_msg",
    "errorMsg",
    "error_description",
    "success",
    "ok",
    "traceId",
    "trace_id",
    "requestId",
    "request_id",
    "url",
    "timestamp",
    "ts",
    "path",
}


def _parse_conf(ds: Any) -> ApiDatasourceConf:
    from apps.datasource.utils.utils import aes_decrypt

    raw = getattr(ds, "configuration", "") or ""
    if not raw:
        return ApiDatasourceConf()
    try:
        return ApiDatasourceConf(**json.loads(aes_decrypt(raw)))
    except Exception:
        return ApiDatasourceConf(**json.loads(raw))


def _endpoint_table_schema(ep: ApiEndpointDef) -> Any:
    from apps.datasource.models.datasource import TableSchema

    desc = ep.description or f"{ep.method} {ep.path}"
    return TableSchema(ep.name, desc)


def _endpoint_field_schema(ep: ApiEndpointDef) -> List[Any]:
    """Project only response fields as virtual columns.

    Request params belong to ``get_resource_detail`` / extract pipeline UIs.
    ``get_fields`` is remaining for CoreField projection / LLM schema text
    compatibility and must describe output shape only.
    """
    from apps.datasource.models.datasource import ColumnSchema

    return [
        ColumnSchema(f.name, f.type or "string", f.description or "")
        for f in ep.response_fields
    ]


def _resource_detail(ep: ApiEndpointDef) -> Dict[str, Any]:
    """Structured resource contract for management / debug UIs."""
    return {
        "name": ep.name,
        "method": ep.method,
        "path": ep.path,
        "description": ep.description,
        "body_mode": ep.body_mode or "object",
        "data_path": ep.data_path,
        "code_path": ep.code_path,
        "code_success_value": ep.code_success_value,
        "total_path": ep.total_path,
        "params": [p.model_dump() for p in ep.params],
        "response_fields": [f.model_dump() for f in ep.response_fields],
    }


def _coerce_json_value(val: Any) -> Any:
    """If a body_raw value arrives as a JSON string (from form UI), parse it."""
    if isinstance(val, str):
        text = val.strip()
        if text and text[0] in "{[":
            try:
                return json.loads(text)
            except Exception:
                return val
    return val


def _values_equal(actual: Any, expected: Any) -> bool:
    """Loose equality for business status codes (0 == '0', True == 'true')."""
    if actual is None or expected is None:
        return actual is expected
    if actual == expected:
        return True
    # Numeric string / int / float
    try:
        if float(actual) == float(expected):
            return True
    except (TypeError, ValueError):
        pass
    return str(actual).strip().lower() == str(expected).strip().lower()


_PLACEHOLDERS: Dict[str, Any] = {
    "string": "",
    "integer": 0,
    "number": 0,
    "boolean": False,
}


def _default_params(
    ep: ApiEndpointDef, *, allow_placeholder: bool = True
) -> Dict[str, Any]:
    """Resolve param values from default/example/(optional) type placeholder."""
    params: Dict[str, Any] = {}
    for p in ep.params:
        if not p.enabled:
            continue
        if p.default is not None:
            params[p.name] = p.default
        elif p.example is not None:
            params[p.name] = p.example
        elif p.required and allow_placeholder:
            params[p.name] = _PLACEHOLDERS.get(p.type, "")
    return params


def _render_api_schema(
    conf: ApiDatasourceConf, endpoint_names: Optional[Sequence[str]] = None
) -> str:
    """Render endpoint list as API-native schema text (not SQL M-Schema)."""
    endpoints = conf.endpoints
    if endpoint_names is not None:
        allow = set(endpoint_names)
        endpoints = [ep for ep in endpoints if ep.name in allow]

    lines: List[str] = [f"【Base URL】 {conf.base_url}", "【Endpoints】"]
    for ep in endpoints:
        lines.append(f"# Endpoint: {ep.name}")
        lines.append(f"  Method: {ep.method.upper()}")
        lines.append(f"  Path: {ep.path}")
        if ep.description:
            lines.append(f"  Description: {ep.description}")
        if ep.data_path:
            lines.append(f"  Data path: {ep.data_path}")
        if ep.params:
            lines.append("  Params:")
            for p in ep.params:
                if not p.enabled:
                    continue
                req = "required" if p.required else "optional"
                default = f", default={p.default}" if p.default is not None else ""
                desc = f" — {p.description}" if p.description else ""
                lines.append(
                    f"    - {p.name} ({p.location}, {p.type}, {req}{default}){desc}"
                )
        else:
            lines.append("  Params: (none)")
        if ep.response_fields:
            lines.append("  Response fields:")
            for f in ep.response_fields:
                if not f.enabled:
                    continue
                path = f" path={f.path}" if f.path else ""
                desc = f" — {f.description}" if f.description else ""
                lines.append(f"    - {f.name} ({f.type}{path}){desc}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


class RestProtocol(BaseProtocol):
    """Protocol for HTTP/REST datasources (type='api')."""

    capabilities = {CAP_OPENAPI_IMPORT, CAP_CONF_OWNED_RESOURCES}
    training_type = "rest"

    def __init__(self, type_key: str) -> None:
        self.type_key = type_key

    def normalize_configuration(
        self,
        configuration: Mapping[str, Any],
    ) -> Dict[str, Any]:
        unknown = sorted(set(configuration) - set(ApiDatasourceConf.model_fields))
        if unknown:
            raise ValueError(
                "Unsupported API datasource configuration field(s): "
                f"{', '.join(unknown)}"
            )
        return ApiDatasourceConf.model_validate(dict(configuration)).model_dump(
            mode="json"
        )

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def check_connection(
        self, ds: Any, trans: Any = None, is_raise: bool = False
    ) -> bool:
        conf = _parse_conf(ds)
        if not conf.base_url:
            if is_raise:
                raise ValueError("API base_url is empty")
            return False
        try:
            check_ssrf(conf.base_url)
            # Do not follow redirects — SSRF only validates the original URL.
            with httpx.Client(timeout=10, follow_redirects=False) as client:
                resp = client.get(conf.base_url)
                # Any 2xx/3xx/4xx (server reachable) counts as "connected".
                # Only 5xx or transport errors count as failure.
                if resp.status_code >= 500:
                    if is_raise:
                        raise ValueError(f"API server returned {resp.status_code}")
                    return False
                return True
        except ValueError:
            raise
        except Exception as e:
            if is_raise:
                raise ValueError(f"API connection failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Schema discovery
    # ------------------------------------------------------------------

    def get_tables(self, ds: Any) -> List[Any]:
        conf = _parse_conf(ds)
        return [_endpoint_table_schema(ep) for ep in conf.endpoints]

    def get_fields(
        self, ds: Any, table_name: str, database_name: str | None = None
    ) -> List[Any]:
        conf = _parse_conf(ds)
        ep = next((e for e in conf.endpoints if e.name == table_name), None)
        if ep is None:
            return []
        return _endpoint_field_schema(ep)

    def retrieve_schema(
        self,
        session: Any,
        current_user: Any,
        ds: Any,
        question: str,
        *,
        embedding: bool = True,
        out_ds_instance: Any = None,
        resource_names: Optional[Sequence[str]] = None,
        required_resource_names: Sequence[str] = (),
        access_scope: Any = None,
    ) -> SchemaSnapshot:
        conf = _parse_conf(ds)

        # Explicit allow-list (e.g. chart step after plan chose an endpoint).
        if resource_names is not None:
            names = list(resource_names)
            return SchemaSnapshot(
                schema_text=_render_api_schema(conf, names),
                resource_names=names,
                sample_data="",
            )

        if out_ds_instance is not None:
            # External assistant DS may still return a list-like schema; prefer API form when conf has endpoints.
            if conf.endpoints:
                names = [ep.name for ep in conf.endpoints]
                return SchemaSnapshot(
                    schema_text=_render_api_schema(conf, names),
                    resource_names=names,
                    sample_data="",
                )
            schema_text, names = out_ds_instance.get_db_schema(ds.id, question)
            return SchemaSnapshot(
                schema_text=schema_text, resource_names=list(names), sample_data=""
            )

        # Reuse CoreTable selection + optional embedding to choose endpoints,
        # then re-render as API schema (avoid SQL M-Schema shape).
        from apps.datasource.crud.datasource import get_table_schema

        _, names = get_table_schema(
            session=session,
            current_user=current_user,
            ds=ds,
            question=question,
            embedding=embedding,
            required_table_list=list(required_resource_names),
            table_objs=(
                list(access_scope.table_objects) if access_scope is not None else None
            ),
        )
        if not names:
            # Fall back to all conf endpoints when projections not yet synced.
            names = [ep.name for ep in conf.endpoints]

        schema_text = _render_api_schema(conf, names)
        return SchemaSnapshot(
            schema_text=schema_text, resource_names=list(names), sample_data=""
        )

    # ------------------------------------------------------------------
    # Prompt assembly
    # ------------------------------------------------------------------

    def build_prompt_bundle(
        self, chat_question: Any, *, enable_query_limit: bool = True
    ) -> PromptBundle:
        from apps.template.template import get_base_template

        q = chat_question
        base_template = get_base_template()
        tpl = base_template.get("template", {}).get("api", {})

        process_check = tpl.get("process_check", "")
        base_api_rules = tpl.get(
            "base_api_rules",
            "只能使用 <api-schema> 中列出的接口；参数名/类型必须匹配接口定义；"
            "必填参数必须赋值；无法回答时返回 success=false。",
        )

        system = tpl.get("system", "").format(
            lang=q.lang, sqlbot_name=q.sqlbot_name, process_check=process_check
        )
        rules = tpl.get("generate_rules", "").format(
            lang=q.lang, sqlbot_name=q.sqlbot_name, base_api_rules=base_api_rules
        )
        schema = tpl.get("generate_basic_info", "").format(
            engine=q.engine, schema=q.db_schema
        )

        bundle = PromptBundle(
            system=system,
            rules=rules,
            schema_text=schema,
            ack_rules="我已掌握所有规则，包括接口定义、参数规范、安全限制和输出格式，我会严格遵守这些规则。",
            ack_schema="我已确认您提供的API接口信息与参数结构，我生成的请求不会超出您提供的接口范围。",
            ack_data_training="我已确认您提供的查询示例，我会进行参考。",
        )

        if getattr(q, "terminologies", ""):
            bundle.terminologies = tpl.get("generate_terminologies_info", "").format(
                terminologies=q.terminologies
            )
        if getattr(q, "data_training", ""):
            bundle.data_training = tpl.get("generate_data_training_info", "").format(
                data_training=q.data_training
            )
        if getattr(q, "custom_prompt", ""):
            bundle.custom_prompt = tpl.get("generate_custom_prompt_info", "").format(
                custom_prompt=q.custom_prompt
            )

        return bundle

    def build_user_prompt(
        self, chat_question: Any, *, current_time: str, change_title: bool
    ) -> str:
        from apps.template.template import get_base_template

        q = chat_question
        base_template = get_base_template()
        tpl = base_template.get("template", {}).get("api", {})
        user_tpl = tpl.get("user", "Question: {question}\nRule: {rule}")
        question = getattr(q, "generation_question", "") or q.question
        if getattr(q, "regenerate_record_id", None):
            hint = tpl.get("regenerate_hint", "请重新生成请求。")
            question = hint + question
        body = user_tpl.format(
            lang=q.lang,
            engine=q.engine,
            schema=q.db_schema,
            question=question,
            rule=q.rule,
            current_time=current_time,
            error_msg=getattr(q, "error_msg", "") or "",
            change_title=change_title,
        )
        return body

    # ------------------------------------------------------------------
    # Chart prompt overrides (API-centric, protocol-own)
    # ------------------------------------------------------------------

    def build_chart_system_prompt(self, chat_question: Any) -> Dict[str, str]:
        from apps.template.generate_chart.generator import get_chart_api_template

        tpl = get_chart_api_template()
        return {
            "system": tpl["system"].format(
                lang=chat_question.lang, sqlbot_name=chat_question.sqlbot_name
            ),
            "rules": tpl["generate_rules"].format(lang=chat_question.lang),
            "ack": "我已掌握所有规则，我会严格遵守这些规则来生成符合要求的JSON。",
        }

    def build_chart_user_prompt(
        self,
        chat_question: Any,
        chart_type: str,
        schema: str,
    ) -> str:
        from apps.template.generate_chart.generator import get_chart_api_template

        tpl = get_chart_api_template()
        return tpl["user"].format(
            lang=chat_question.lang,
            query_plan=chat_question.sql,
            question=(
                getattr(chat_question, "generation_question", "")
                or getattr(chat_question, "planning_question", "")
                or chat_question.question
            ),
            rule=chat_question.rule,
            chart_type=chart_type,
            schema=schema,
        )

    # ------------------------------------------------------------------
    # Parse / validate / execute
    # ------------------------------------------------------------------

    def _extract_json(self, text: str) -> Optional[str]:
        text = text.strip()
        if text.startswith("```"):
            end = text.find("```", 3)
            if end > 0:
                text = text[3:end].strip()
                if text.startswith("json"):
                    text = text[4:].strip()
        start = text.find("{")
        if start < 0:
            return None
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        return None

    def parse_llm_output(self, text: str) -> QueryPlan:
        json_str = self._extract_json(text)
        if json_str is None:
            return QueryPlan(
                success=False, message="API answer is not a valid json object"
            )
        try:
            data = orjson.loads(json_str)
        except Exception:
            return QueryPlan(success=False, message="Cannot parse API answer")

        if not data.get("success"):
            return QueryPlan(
                success=False, message=data.get("message", "Unknown error")
            )

        endpoint_name = data.get("target") or data.get("endpoint") or ""
        params = data.get("params") or {}
        if not endpoint_name:
            return QueryPlan(success=False, message="API endpoint (target) is empty")

        return QueryPlan(
            success=True,
            statement=f"API: {endpoint_name}",
            payload={"endpoint": endpoint_name, "params": params},
            resources=[endpoint_name],
            chart_type=data.get("chart-type"),
            brief=data.get("brief"),
        )

    def parse_candidate_payload(self, payload: Mapping[str, Any]) -> QueryPlan:
        endpoint_name = str(
            payload.get("endpoint") or payload.get("target") or ""
        ).strip()
        if not endpoint_name:
            return QueryPlan(
                success=False,
                message="API endpoint (target) is empty",
            )
        params = payload.get("params") or {}
        if not isinstance(params, Mapping):
            return QueryPlan(success=False, message="API params must be an object")
        return QueryPlan(
            success=True,
            statement=f"API: {endpoint_name}",
            payload={"endpoint": endpoint_name, "params": dict(params)},
            resources=[endpoint_name],
            chart_type=payload.get("chart-type") or payload.get("chart_type"),
            brief=payload.get("brief"),
        )

    def validate_plan(
        self, ds: Any, plan: QueryPlan, allowed_resources: Sequence[str]
    ) -> QueryPlan:
        conf = _parse_conf(ds)
        endpoint_name = plan.payload.get("endpoint", "")

        ep = next((e for e in conf.endpoints if e.name == endpoint_name), None)
        if ep is None:
            return QueryPlan(
                success=False,
                message=f"Unknown API endpoint: {endpoint_name}",
                payload=plan.payload,
            )

        # SSRF check on the full URL (before substitution of path params use template path with braces).
        # Path params may still contain `{id}` templates — validate base host first, full URL after substitute in execute.
        try:
            check_ssrf(conf.base_url)
        except ValueError as e:
            return QueryPlan(success=False, message=str(e), payload=plan.payload)

        # Allow-list check (checked CoreTable projection / embedding subset)
        if allowed_resources and endpoint_name not in allowed_resources:
            return QueryPlan(
                success=False,
                message=f"Unauthorized API endpoint: {endpoint_name}",
                payload=plan.payload,
            )

        plan.payload["_endpoint"] = ep.model_dump()
        plan.payload["_base_url"] = conf.base_url
        plan.statement = f"{ep.method.upper()} {ep.path}"
        return plan

    def execute(
        self,
        ds: Any,
        plan: QueryPlan,
        *,
        origin_column: bool = False,
        max_rows: Optional[int] = None,
    ) -> QueryResult:
        """Run the plan and return a tabular QueryResult.

        Single path: resolve endpoint → HTTP → extraction → QueryResult.
        Business failures and empty projections that wrap an error payload are
        elevated to ``SingleMessageError`` so the chat pipeline never renders a
        fake success table of null cells.
        """
        conf, ep, params = self._resolve_endpoint(ds, plan)
        try:
            raw_response, _http_status = self._http_execute(conf, ep, params)
        except SingleMessageError:
            raise
        except ValueError as e:
            raise SingleMessageError(str(e))
        except Exception as e:
            SQLBotLogUtil.error(f"API execute failed: {e}")
            raise SingleMessageError(f"API request failed: {e}")

        extracted = self._apply_extraction(raw_response, ep)
        display_stmt = f"{ep.method.upper()} {ep.path}\nparams: {json.dumps(params, ensure_ascii=False)}"

        # Never hand a business failure or pure-null projection back as table data.
        err = extracted.get("error")
        if err or not extracted["is_success"]:
            raise SingleMessageError(
                err or self._format_business_error(extracted, raw_response)
            )

        projected_data = extracted["projected_data"]
        bounded_limit = int(max_rows) if max_rows and max_rows > 0 else None
        truncated = bool(
            bounded_limit is not None
            and (
                len(projected_data) > bounded_limit
                or (
                    extracted["total"] is not None
                    and int(extracted["total"]) > bounded_limit
                )
            )
        )
        if bounded_limit is not None:
            projected_data = projected_data[:bounded_limit]

        return QueryResult(
            fields=extracted["projected_fields"],
            data=projected_data,
            raw=raw_response,
            statement=display_stmt,
            re_exec={
                "endpoint": ep.name,
                "params": params,
                "base_url": conf.base_url,
            },
            code_value=extracted["code_value"],
            total=extracted["total"],
            is_success=True,
            truncated=truncated,
            limit=bounded_limit if truncated else None,
            truncation_reason="query_limit" if truncated else None,
        )

    def plan_from_re_exec(
        self, ds: Any, re_exec: Dict[str, Any]
    ) -> Optional[QueryPlan]:
        """Rebuild an executable plan from stored re_exec payload."""
        if not re_exec:
            return None
        conf = _parse_conf(ds)
        endpoint_name = re_exec.get("endpoint") or ""
        params = re_exec.get("params") or {}
        if not endpoint_name:
            return None
        ep = next((e for e in conf.endpoints if e.name == endpoint_name), None)
        if ep is None:
            return None
        return QueryPlan(
            success=True,
            statement=f"{ep.method.upper()} {ep.path}",
            payload={
                "endpoint": ep.name,
                "params": params,
                "_endpoint": ep.model_dump(),
                "_base_url": re_exec.get("base_url") or conf.base_url,
            },
            resources=[ep.name],
        )

    def preview(
        self,
        session: Any,
        current_user: Any,
        ds: Any,
        table_name: str,
        fields: Sequence[str],
        *,
        where: str = "",
        limit: int = 100,
        database_name: str | None = None,
    ) -> QueryResult:
        conf = _parse_conf(ds)
        ep = next((e for e in conf.endpoints if e.name == table_name), None)
        if ep is None:
            raise SingleMessageError(f"Unknown endpoint: {table_name}")

        plan = QueryPlan(
            success=True,
            statement=f"{ep.method.upper()} {ep.path}",
            payload={
                "endpoint": ep.name,
                "params": _default_params(ep, allow_placeholder=True),
                "_endpoint": ep.model_dump(),
                "_base_url": conf.base_url,
            },
        )
        qr = self.execute(ds, plan, origin_column=True)
        if fields and qr.data:
            kept = [f for f in fields if f in qr.fields]
            if kept:
                qr.fields = kept
                qr.data = [{k: row.get(k) for k in kept} for row in qr.data]
        if limit and qr.data and len(qr.data) > limit:
            qr.data = qr.data[:limit]
        qr.statement = self.format_statement_for_display(plan)
        return qr

    def get_resource_detail(self, ds: Any, table_name: str) -> Optional[Dict[str, Any]]:
        conf = _parse_conf(ds)
        ep = next((e for e in conf.endpoints if e.name == table_name), None)
        if ep is None:
            return None
        return _resource_detail(ep)

    def test_extract(
        self,
        ds: Any,
        table_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute and return the full extraction pipeline view for debug UI.

        Shares ``_http_execute`` + ``_apply_extraction`` with ``execute``.
        Does not invent placeholder values for missing required params —
        required inputs must be supplied by the caller.
        """
        conf = _parse_conf(ds)
        ep = next((e for e in conf.endpoints if e.name == table_name), None)
        if ep is None:
            return {"error": f"Unknown endpoint: {table_name}", "is_success": False}

        # User params win; fill only undeclared keys from defaults/examples (no placeholders).
        exec_params = dict(params or {})
        for p in ep.params:
            if not p.enabled:
                continue
            if p.name in exec_params and exec_params[p.name] not in (None, ""):
                continue
            if p.default is not None:
                exec_params[p.name] = p.default
            elif p.example is not None:
                exec_params[p.name] = p.example

        missing = [
            p.name
            for p in ep.params
            if p.enabled
            and p.required
            and (p.name not in exec_params or exec_params[p.name] in (None, ""))
        ]
        if missing:
            return {
                "error": f"Required param missing: {', '.join(missing)}",
                "is_success": False,
                "resource": _resource_detail(ep),
                "params_used": exec_params,
            }

        try:
            raw_response, http_status = self._http_execute(conf, ep, exec_params)
        except Exception as e:
            return {
                "error": str(e),
                "is_success": False,
                "resource": _resource_detail(ep),
                "params_used": exec_params,
            }

        extracted = self._apply_extraction(raw_response, ep)
        return {
            "raw_response": raw_response,
            "http_status": http_status,
            "data_path": ep.data_path or "",
            "extracted_rows": extracted["extracted_rows"],
            "projected_fields": extracted["projected_fields"],
            "projected_data": extracted["projected_data"],
            "code_value": extracted["code_value"],
            "code_success_value": ep.code_success_value,
            "total": extracted["total"],
            "is_success": extracted["is_success"],
            "error": extracted.get("error"),
            "resource": _resource_detail(ep),
            "params_used": exec_params,
        }

    def format_statement_for_display(self, plan: QueryPlan) -> str:
        ep = plan.payload.get("_endpoint") or {}
        method = (ep.get("method") or "GET").upper()
        path = ep.get("path") or plan.statement or ""
        params = plan.payload.get("params") or {}
        try:
            params_txt = json.dumps(params, ensure_ascii=False)
        except Exception:
            params_txt = str(params)
        return f"{method} {path}\nparams: {params_txt}"

    def engine_display_name(self, ds: Any) -> str:
        return "API"

    def server_version(self, ds: Any) -> str:
        return ""

    def schema_namespace(self, ds: Any) -> str:
        # REST resources live in conf; no SQL schema namespace.
        return ""

    # ------------------------------------------------------------------
    # Shared execution core — single path for execute + test_extract
    # ------------------------------------------------------------------

    def _resolve_endpoint(
        self, ds: Any, plan: QueryPlan
    ) -> tuple[ApiDatasourceConf, ApiEndpointDef, Dict[str, Any]]:
        conf = _parse_conf(ds)
        ep_data = plan.payload.get("_endpoint")
        if ep_data:
            ep = ApiEndpointDef(**ep_data)
        else:
            ep_name = plan.payload.get("endpoint", "")
            ep = next((e for e in conf.endpoints if e.name == ep_name), None)
            if ep is None:
                raise SingleMessageError(f"Unknown endpoint: {ep_name}")
        params = plan.payload.get("params", {}) or {}
        return conf, ep, params

    def _http_execute(
        self,
        conf: ApiDatasourceConf,
        ep: ApiEndpointDef,
        params: Dict[str, Any],
    ) -> tuple[Any, int]:
        """Single HTTP executor. Returns (response_json, http_status)."""
        method = (ep.method or "GET").upper()
        path = ep.path or ""
        base_url = conf.base_url
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))

        headers: Dict[str, str] = dict(conf.headers)
        headers.update(ep.extra_headers or {})
        query_params: Dict[str, Any] = dict(ep.extra_query or {})
        body_params: Dict[str, Any] = {}

        self._apply_auth(conf.auth, headers, query_params)

        # Override with call-time params for keys that are still open-ended (LLM may
        # invent keys). Declared params are preferred routing by location.
        declared = {p.name: p for p in ep.params if p.enabled}
        routed: set[str] = set()
        for pdef in ep.params:
            if not pdef.enabled:
                continue
            pname = pdef.name
            loc = pdef.location or "query"
            val = params.get(pname, pdef.default)
            if val is None:
                if pdef.required:
                    raise SingleMessageError(f"Required param missing: {pname}")
                continue
            routed.add(pname)
            if loc == "query":
                query_params[pname] = val
            elif loc == "header":
                headers[pname] = str(val)
            elif loc == "path":
                url = url.replace(f"{{{pname}}}", str(val))
            elif loc == "body":
                body_params[pname] = val
            else:
                query_params[pname] = val

        # Undeclared extra params from the plan go to query (LLM shape), never body,
        # unless the method carries a body where undeclared body-style is used.
        for pname, val in params.items():
            if pname in routed or val is None:
                continue
            if pname not in declared:
                query_params[pname] = val

        body: Any = None
        if ep.body_template:
            try:
                body = json.loads(ep.body_template.format(**body_params))
            except Exception:
                body = body_params or None
        elif method in ("POST", "PUT", "PATCH") or body_params:
            # object: DTO field keys assemble a JSON object.
            # raw: OpenAPI body schema is the value itself (array / free-form / primitive);
            # parameter name is documentation-only and must not wrap the payload.
            if (ep.body_mode or "object") == "raw":
                if len(body_params) == 1:
                    only = next(iter(body_params.values()))
                    body = _coerce_json_value(only)
                elif body_params:
                    body = body_params
                else:
                    body = None
            else:
                body = body_params or None

        max_bytes = settings.API_MAX_RESPONSE_SIZE_MB * 1024 * 1024
        check_ssrf(url)
        with httpx.Client(timeout=conf.timeout, follow_redirects=False) as client:
            resp = client.request(
                method,
                url,
                headers=headers or None,
                params=query_params or None,
                json=body if body is not None else None,
            )
            if resp.is_redirect:
                raise SingleMessageError(
                    f"API returned redirect {resp.status_code}; redirects are disabled for SSRF safety"
                )
            if resp.status_code >= 400:
                snippet = (resp.text or "")[:300]
                raise SingleMessageError(f"API HTTP {resp.status_code}: {snippet}")
            raw_bytes = len(resp.content)
            if raw_bytes > max_bytes:
                raise SingleMessageError(f"Response too large: {raw_bytes} bytes")
            try:
                response_json = resp.json()
            except Exception:
                raise SingleMessageError("API response is not valid JSON")

        return response_json, resp.status_code

    def _apply_extraction(
        self, response_json: Any, ep: ApiEndpointDef
    ) -> Dict[str, Any]:
        """Single extraction pipeline shared by execute and test_extract.

        Projection contract:
        1. Walk ``data_path`` (or auto list key) to obtain row objects.
        2. Project each ``response_fields`` entry **relative to the row**.
           Legacy absolute paths from older OpenAPI imports (``data[].x`` /
           ``data.x``) are rewritten to the relative form when possible.
        3. Envelope-only rows that wrap a business failure (code/message with
           no real data) are marked ``is_success=False`` with a human error.
        """
        data_path = (ep.data_path or "").strip()
        extracted_rows = self._extract_data(response_json, data_path)
        # Track which path was actually used (auto-inferred when empty).
        # Also recover the array key from legacy absolute field paths
        # (``data[].projectName``) so relative projection still works when the
        # list is null (login failure) and auto-inference finds no list.
        effective_data_path = (
            data_path
            or self._inferred_data_path(response_json)
            or self._data_path_from_field_prefixes(ep.response_fields or [])
            or ""
        )
        # If data_path was empty but we recovered one from field prefixes, and
        # the auto empty-path pass returned the whole envelope as a pseudo-row,
        # re-extract with the recovered path so empty/null data becomes [].
        if (
            not data_path
            and effective_data_path
            and extracted_rows
            and isinstance(response_json, dict)
            and extracted_rows[0] is response_json
        ):
            extracted_rows = self._extract_data(response_json, effective_data_path)

        code_value = None
        is_success = True
        if ep.code_path:
            code_value = self._dot_get(response_json, ep.code_path)
            # Enforce only when success criteria is configured (not None).
            if ep.code_success_value is not None:
                is_success = _values_equal(code_value, ep.code_success_value)
        else:
            # Unconfigured: still surface common envelope codes / login failures
            # so we do not invent empty tables.
            code_value = self._guess_code_value(response_json)

        total: Optional[int] = None
        if ep.total_path:
            raw_total = self._dot_get(response_json, ep.total_path)
            if raw_total is not None:
                try:
                    total = int(raw_total)
                except (ValueError, TypeError):
                    total = None

        field_specs = self._normalize_response_field_specs(
            [f for f in (ep.response_fields or []) if f.enabled],
            effective_data_path=effective_data_path,
        )

        projected_fields: List[str]
        projected_data: List[Dict[str, Any]]
        if field_specs:
            projected_fields = [f["name"] for f in field_specs]
            projected_data = []
            for row in extracted_rows:
                # When data_path failed and the only "row" is the envelope itself,
                # relative field lookup on the envelope would make every business
                # leaf None. Keep that behavior only for real item objects.
                if not isinstance(row, dict):
                    projected_data.append({f["name"]: None for f in field_specs})
                    continue
                flat: Dict[str, Any] = {}
                for f in field_specs:
                    flat[f["name"]] = self._dot_get(row, f["path"])
                projected_data.append(flat)
        elif extracted_rows and isinstance(extracted_rows[0], dict):
            # Drop pure envelope keys when the row is the whole response object.
            first = extracted_rows[0]
            if (
                len(extracted_rows) == 1
                and isinstance(response_json, dict)
                and first is response_json
            ):
                projected_fields = [
                    k for k in first.keys() if k not in _ENVELOPE_META_KEYS
                ] or list(first.keys())
                projected_data = [{k: first.get(k) for k in projected_fields}]
            else:
                projected_fields = list(first.keys())
                projected_data = list(extracted_rows)
        elif isinstance(response_json, dict) and not extracted_rows:
            projected_fields = list(response_json.keys())
            projected_data = [response_json]
        else:
            projected_fields = []
            projected_data = list(extracted_rows) if extracted_rows else []

        error: Optional[str] = None
        if ep.code_path and ep.code_success_value is not None and not is_success:
            error = self._format_business_error(
                {
                    "code_value": code_value,
                    "projected_data": projected_data,
                },
                response_json,
            )
        else:
            # Heuristic: API returned HTTP 200 but data projection is all-null and
            # envelope carries a failure message (login / biz code). Treat as error.
            heur_err = self._detect_envelope_failure(
                response_json=response_json,
                code_value=code_value,
                code_path=ep.code_path,
                code_success_value=ep.code_success_value,
                projected_fields=projected_fields,
                projected_data=projected_data,
                extracted_rows=extracted_rows,
            )
            if heur_err:
                is_success = False
                error = heur_err
                if code_value is None:
                    code_value = self._guess_code_value(response_json)

        return {
            "extracted_rows": extracted_rows,
            "projected_fields": projected_fields,
            "projected_data": projected_data,
            "code_value": code_value,
            "total": total,
            "is_success": is_success,
            "error": error,
        }

    # Common envelope keys for business status / messages. Used both when OpenAPI
    # left code_path empty and when projection yields only null business columns.
    _ENVELOPE_CODE_KEYS = (
        "code",
        "status",
        "statusCode",
        "status_code",
        "errcode",
        "errCode",
    )
    _ENVELOPE_MESSAGE_KEYS = (
        "message",
        "msg",
        "error",
        "errorMessage",
        "error_msg",
        "errorMsg",
        "error_description",
    )

    @staticmethod
    def _apply_auth(
        auth: ApiAuthConfig, headers: Dict[str, str], query: Dict[str, Any]
    ) -> None:
        if auth.type == ApiAuthType.API_KEY:
            if not auth.api_key:
                return
            if auth.api_key_location.value == "header":
                headers[auth.api_key_header] = auth.api_key
            else:
                query[auth.api_key_header] = auth.api_key
        elif auth.type == ApiAuthType.BEARER:
            if not auth.bearer_token:
                return
            headers["Authorization"] = f"Bearer {auth.bearer_token}"
        elif auth.type == ApiAuthType.BASIC:
            if not auth.basic_username and not auth.basic_password:
                return
            import base64

            cred = base64.b64encode(
                f"{auth.basic_username}:{auth.basic_password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {cred}"
        elif auth.type == ApiAuthType.COOKIE:
            pairs = [
                f"{name}={value}"
                for name, value in (auth.cookies or {}).items()
                if name and value is not None and str(name).strip()
            ]
            if not pairs:
                return
            cookie_str = "; ".join(pairs)
            existing = (headers.get("Cookie") or headers.get("cookie") or "").strip()
            headers["Cookie"] = f"{existing}; {cookie_str}" if existing else cookie_str

    @staticmethod
    def _extract_data(response_json: Any, data_path: str) -> List[Dict[str, Any]]:
        """Extract row list from a response.

        When ``data_path`` is set, walk only that path.
        When empty: list body → itself; dict with common list keys → first hit;
        otherwise wrap the dict as a single row. Extraction is intentional — auto
        keys are a documented convenience until path is configured.

        A configured path that resolves to None / empty (e.g. login failure where
        ``data`` is null) returns ``[]`` rather than inventing envelope columns.
        """
        if not data_path:
            if isinstance(response_json, list):
                return list(response_json)
            if isinstance(response_json, dict):
                for key in ("data", "items", "results", "records", "rows", "list"):
                    val = response_json.get(key)
                    if isinstance(val, list):
                        return list(val)
                return [response_json]
            return []

        obj = RestProtocol._dot_get(response_json, data_path)
        if isinstance(obj, list):
            return list(obj)
        if isinstance(obj, dict):
            return [obj]
        return []

    @staticmethod
    def _inferred_data_path(response_json: Any) -> str:
        """Mirror auto-list keys used when data_path is empty."""
        if not isinstance(response_json, dict):
            return ""
        for key in ("data", "items", "results", "records", "rows", "list"):
            if isinstance(response_json.get(key), list):
                return key
        return ""

    @staticmethod
    def _data_path_from_field_prefixes(response_fields: List[Any]) -> str:
        """Recover``data``/list-key from legacy absolute OpenAPI paths.

        Example: most fields named ``data[].projectName`` / path ``data[].x``
        → ``data``. Only returns a key when the majority of non-envelope fields
        share the same first path segment ending with ``[]`` or a dotted root.
        """
        prefixes: Dict[str, int] = {}
        for f in response_fields:
            raw = getattr(f, "path", None) or getattr(f, "name", None)
            if isinstance(f, dict):
                raw = f.get("path") or f.get("name") or raw
            token = str(raw or "")
            if not token:
                continue
            # Prefer segment before [].
            if "[]" in token:
                head = token.split("[]", 1)[0].strip(".")
            else:
                head = token.split(".", 1)[0].strip()
            if not head or head in _ENVELOPE_META_KEYS:
                continue
            prefixes[head] = prefixes.get(head, 0) + 1
        if not prefixes:
            return ""
        best = max(prefixes.items(), key=lambda kv: kv[1])
        # Require at least one business field pointing under that prefix.
        return best[0] if best[1] >= 1 else ""

    @staticmethod
    def _normalize_response_field_specs(
        response_fields: List[Any],
        *,
        effective_data_path: str,
    ) -> List[Dict[str, str]]:
        """Convert saved response_fields into relative ``{name, path}`` specs.

        Handles legacy absolute OpenAPI paths such as ``data[].projectName`` /
        ``data.projectName`` by stripping the data_path / ``[]`` prefixes so the
        resulting path is relative to each extracted row object.
        """
        specs: List[Dict[str, str]] = []
        dp = (effective_data_path or "").strip().strip(".")
        for f in response_fields:
            raw_name = (
                getattr(f, "name", None)
                or (f.get("name") if isinstance(f, dict) else "")
                or ""
            )
            raw_path = (
                getattr(f, "path", None)
                or (f.get("path") if isinstance(f, dict) else "")
                or raw_name
            )
            raw_name = str(raw_name)
            raw_path = str(raw_path) if raw_path else raw_name

            name = RestProtocol._to_relative_leaf(raw_name, dp)
            path = RestProtocol._to_relative_leaf(raw_path, dp) or name
            if not name:
                continue
            # Skip pure envelope keys if a data array is in play — they are not
            # row columns and would force a single null-heavy pseudo-row.
            if dp and name in _ENVELOPE_META_KEYS and path in _ENVELOPE_META_KEYS:
                continue
            specs.append({"name": name, "path": path})
        # De-dup by name preserving order (after relative collapse)
        seen: set[str] = set()
        out: List[Dict[str, str]] = []
        for s in specs:
            if s["name"] in seen:
                continue
            seen.add(s["name"])
            out.append(s)
        return out

    @staticmethod
    def _to_relative_leaf(token: str, data_path: str) -> str:
        """Strip array tokens and optional data_path prefix from a field token."""
        if not token:
            return ""
        s = str(token).replace("[]", "")
        while ".." in s:
            s = s.replace("..", ".")
        s = s.strip(".")
        if not s:
            return ""
        dp = (data_path or "").strip().strip(".")
        if dp:
            prefixes = (f"{dp}.", f"{dp}")
            for p in prefixes:
                if s == p.rstrip("."):
                    return ""
                if s.startswith(p if p.endswith(".") else p + "."):
                    s = s[len(p) :].lstrip(".") if p.endswith(".") else s[len(p) + 1 :]
                    break
            # Also accept "data0" / mis-parse free forms carefully — not needed.
        # Bare leaf retains original casing (projectName etc.).
        return s

    @staticmethod
    def _guess_code_value(response_json: Any) -> Any:
        if not isinstance(response_json, dict):
            return None
        for key in RestProtocol._ENVELOPE_CODE_KEYS:
            if key in response_json:
                return response_json.get(key)
        return None

    @staticmethod
    def _guess_message(response_json: Any) -> str:
        if not isinstance(response_json, dict):
            return ""
        for key in RestProtocol._ENVELOPE_MESSAGE_KEYS:
            val = response_json.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
            if val is not None and not isinstance(val, (dict, list)):
                text = str(val).strip()
                if text:
                    return text
        return ""

    @staticmethod
    def _format_business_error(extracted: Dict[str, Any], response_json: Any) -> str:
        code = extracted.get("code_value")
        if code is None:
            code = RestProtocol._guess_code_value(response_json)
        message = RestProtocol._guess_message(response_json)
        if message and code is not None:
            return f"API business error (code={code}): {message}"
        if message:
            return f"API business error: {message}"
        if code is not None:
            return f"API business error (code={code})"
        return "API returned a business failure with no data"

    @staticmethod
    def _detect_envelope_failure(
        *,
        response_json: Any,
        code_value: Any,
        code_path: str,
        code_success_value: Any,
        projected_fields: List[str],
        projected_data: List[Dict[str, Any]],
        extracted_rows: List[Any],
    ) -> Optional[str]:
        """Return an error string when the payload is an envelope failure, else None.

        Fires only when the projected table would be empty / all-null **and** the
        body carries a non-success business signal. Legitimate empty result sets
        (``data: []`` with success code) are left alone.
        """
        # Configured success criteria are handled upstream — do not double-fire.
        if code_path and code_success_value is not None:
            return None

        message = RestProtocol._guess_message(response_json)
        code = (
            code_value
            if code_value is not None
            else RestProtocol._guess_code_value(response_json)
        )

        rows_empty = not extracted_rows
        all_null = False
        if projected_data:
            business_fields = [
                f for f in projected_fields if f not in _ENVELOPE_META_KEYS
            ]
            check_fields = business_fields or list(projected_fields)
            if check_fields:
                all_null = True
                for row in projected_data:
                    if not isinstance(row, dict):
                        continue
                    for f in check_fields:
                        val = row.get(f)
                        if val is not None and val != "":
                            all_null = False
                            break
                    if not all_null:
                        break
        elif not projected_fields:
            all_null = rows_empty

        if not (rows_empty or all_null):
            # Real cells present — never rewrite as error.
            return None

        success_markers = {
            0,
            "0",
            200,
            "200",
            True,
            "true",
            "success",
            "ok",
            "SUCCESS",
            "OK",
        }
        code_failed = False
        if code is not None and code not in success_markers:
            if str(code).strip().lower() not in {"0", "200", "true", "success", "ok"}:
                code_failed = True

        flag_failed = False
        if isinstance(response_json, dict) and "success" in response_json:
            s = response_json.get("success")
            if s is False or str(s).strip().lower() in {"false", "0", "no"}:
                flag_failed = True

        authish = False
        if message:
            low = message.lower()
            authish = any(
                tok in low
                for tok in (
                    "not logged",
                    "unauthorized",
                    "unauth",
                    "unauthenticated",
                    "login",
                    "token",
                    "forbidden",
                    "未登录",
                    "无权限",
                    "鉴权",
                    "登录",
                )
            )

        if not (code_failed or flag_failed or authish):
            return None
        return RestProtocol._format_business_error({"code_value": code}, response_json)

    @staticmethod
    def _dot_get(obj: Any, path: str) -> Any:
        """Walk a simple dot-path (``a.b.0.c``); strips leftover ``[]`` tokens.

        Not full JSONPath — array wildcards are meaningless once the row object
        is selected via ``data_path``.
        """
        if not path:
            return obj
        normalized = str(path).replace("[]", "")
        while ".." in normalized:
            normalized = normalized.replace("..", ".")
        normalized = normalized.strip(".")
        if not normalized:
            return obj
        cur = obj
        for part in normalized.split("."):
            if part == "":
                continue
            if isinstance(cur, dict):
                cur = cur.get(part)
            elif isinstance(cur, list):
                try:
                    cur = cur[int(part)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
            if cur is None:
                return None
        return cur

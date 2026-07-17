"""Parse OpenAPI 2.0 (Swagger) and 3.x specs into ApiEndpointDef lists.

Accepts raw JSON or YAML string. Pure Python — PyYAML + existing Pydantic models.

Architecture
------------
One pipeline for both OAS2 and OAS3:

    load spec → walk paths/methods → resolve operation params + body + response
        via a single root-aware $ref / allOf schema resolver
        then project object DTOs into flat body params / response fields.

Swagger 2.0 body parameters almost always look like::

    { "name": "xxxInfo", "in": "body", "schema": { "$ref": "#/definitions/XxxDTO" } }

Callers need the **DTO leaf fields**, not the wrapper parameter name. OAS3
``requestBody.content.application/json.schema`` is resolved the same way.

Projection contract (written into ``ApiEndpointDef``):
- object DTO with properties → expand top-level fields, ``body_mode="object"``
- array / free-form / primitive body → single body param, ``body_mode="raw"``
  (HTTP payload is the value itself; OpenAPI parameter name is never an envelope key)
- empty request / empty response → ``params=[]`` / ``response_fields=[]`` (first-class)

Response extraction contract (same model driven by execute()):
- When the 2xx body is an envelope ``{code, data: [...], message, ...}`` where
  ``data`` is array-of-objects (or a nested object list), set::

      data_path = "data"                 # (or the array-of-object property name)
      response_fields[*].name/path       # **relative leaf names** of array items,
                                         # e.g. projectName, NOT data[].projectName
      code_path = "code"                 # when a sibling ``code`` / ``status`` exists

- Paths never use JSONPath ``[]`` tokens. Row projection walks ``data_path`` first,
  then resolves each field path relative to the row object.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from apps.protocol.rest.conf import (
    ApiEndpointDef,
    ApiParamDef,
    ApiResponseFieldDef,
)

_HTTP_METHODS = ("get", "post", "put", "patch", "delete", "head", "options")
_JSON_CONTENT_KEYS = (
    "application/json",
    "application/*+json",
    "*/*",
)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse_openapi(content: str) -> List[ApiEndpointDef]:
    """Parse an OpenAPI 2.0 / 3.x JSON or YAML spec string.

    Returns a list of ``ApiEndpointDef`` ready to merge into
    ``ApiDatasourceConf.endpoints``.
    """
    return parse_openapi_document(content)["endpoints"]


def parse_openapi_document(
    content: str,
    *,
    source_url: str = "",
) -> Dict[str, Any]:
    """Parse OpenAPI/Swagger into endpoints plus document-level hints.

    Returns::

        {
            "endpoints": List[ApiEndpointDef],
            "base_url": str,   # absolute API base when resolvable, else ""
            "title": str,      # info.title (usable as datasource name hint)
        }

    ``source_url`` is the URL the content was fetched from (if any). It is only
    used as a fallback/relativised origin for OAS3 ``servers`` entries or when
    the document itself has no host / servers declaration.
    """
    spec = _load_spec(content)
    version = _detect_version(spec)
    if version == 2:
        endpoints = _walk_paths(spec, oas_version=2)
    else:
        endpoints = _walk_paths(spec, oas_version=3)
    return {
        "endpoints": endpoints,
        "base_url": _extract_base_url(spec, version=version, source_url=source_url or ""),
        "title": _extract_title(spec),
    }


def _extract_title(spec: Dict[str, Any]) -> str:
    info = spec.get("info")
    if not isinstance(info, dict):
        return ""
    title = info.get("title")
    return str(title).strip() if title else ""


def _extract_base_url(
    spec: Dict[str, Any],
    *,
    version: int,
    source_url: str = "",
) -> str:
    """Derive the HTTP base used by the described API.

    Priority
    --------
    OAS3 : first non-empty absolute or relative ``servers[].url``
           (relative entries are joined against ``source_url`` origin)
    OAS2 : ``schemes[0]://host + basePath``
    fallback : origin+parent path of ``source_url`` with common doc suffixes stripped
    """
    if version == 3:
        base = _base_url_from_servers(spec.get("servers") or [], source_url=source_url)
        if base:
            return base
    else:
        base = _base_url_from_swagger2(spec)
        if base:
            return base
    return _base_url_from_source_url(source_url)


def _base_url_from_servers(servers: Any, *, source_url: str = "") -> str:
    if not isinstance(servers, list):
        return ""
    for entry in servers:
        if not isinstance(entry, dict):
            continue
        raw = entry.get("url")
        if not isinstance(raw, str) or not raw.strip():
            continue
        url = raw.strip()
        # OAS3 variables: replace {var} with default or the token itself
        variables = entry.get("variables") if isinstance(entry.get("variables"), dict) else {}
        for name, conf in variables.items():
            default = ""
            if isinstance(conf, dict):
                default = str(conf.get("default") or "")
            token = default if default else name
            url = url.replace("{" + str(name) + "}", token)
        if url.startswith("http://") or url.startswith("https://"):
            return _rstrip_url_slash(url)
        # Relative server URL — resolve against the document origin
        origin = _origin_of(source_url)
        if origin:
            return _rstrip_url_slash(origin.rstrip("/") + "/" + url.lstrip("/"))
        # No origin available; return path-like base as-is (caller can still edit baseUrl)
        if url.startswith("/"):
            return url.rstrip("/") or "/"
    return ""


def _base_url_from_swagger2(spec: Dict[str, Any]) -> str:
    host = spec.get("host")
    if not isinstance(host, str) or not host.strip():
        return ""
    host = host.strip()
    schemes = spec.get("schemes")
    scheme = "https"
    if isinstance(schemes, list):
        for s in schemes:
            if isinstance(s, str) and s.strip():
                scheme = s.strip().lower()
                break
    base_path = spec.get("basePath") or ""
    if not isinstance(base_path, str):
        base_path = ""
    base_path = base_path.strip()
    if base_path and not base_path.startswith("/"):
        base_path = "/" + base_path
    base_path = base_path.rstrip("/")
    return f"{scheme}://{host}{base_path}"


def _base_url_from_source_url(source_url: str) -> str:
    """Best-effort base when the document has no host/servers.

    ``https://api.example.com/v1/swagger.json`` → ``https://api.example.com/v1``
    ``https://api.example.com/swagger-ui/index.html`` → ``https://api.example.com``
    """
    if not source_url or not isinstance(source_url, str):
        return ""
    url = source_url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return ""
    # strip query/fragment
    for sep in ("#", "?"):
        if sep in url:
            url = url.split(sep, 1)[0]
    lower = url.lower()
    doc_suffixes = (
        "/swagger.json",
        "/swagger.yaml",
        "/swagger.yml",
        "/openapi.json",
        "/openapi.yaml",
        "/openapi.yml",
        "/v2/api-docs",
        "/v3/api-docs",
        "/api-docs",
        "/swagger-ui.html",
        "/swagger-ui/index.html",
        "/swagger-ui/",
        "/index.html",
    )
    for suffix in doc_suffixes:
        if lower.endswith(suffix):
            url = url[: -len(suffix)]
            break
    else:
        # strip trailing filename that looks like a document
        parts = url.rstrip("/").rsplit("/", 1)
        if len(parts) == 2 and "." in parts[1]:
            url = parts[0]
    return _rstrip_url_slash(url)


def _origin_of(url: str) -> str:
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return ""
    # scheme://host[:port]
    try:
        # avoid depending on urllib here; simple split is enough for origin
        rest = url.split("://", 1)[1]
        hostpart = rest.split("/", 1)[0]
        scheme = url.split("://", 1)[0]
        return f"{scheme}://{hostpart}"
    except Exception:
        return ""


def _rstrip_url_slash(url: str) -> str:
    if not url:
        return ""
    # keep bare origin with no trailing slash normalized the same way
    return url.rstrip("/")


# ---------------------------------------------------------------------------
# Spec loading & version detection
# ---------------------------------------------------------------------------

def _load_spec(content: str) -> Dict[str, Any]:
    content = content.strip()
    if not content:
        raise ValueError("Empty content")
    try:
        result = json.loads(content)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass
    try:
        result = yaml.safe_load(content)
        if isinstance(result, dict):
            return result
        raise ValueError("Parsed YAML is not a mapping")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid JSON/YAML: {e}") from e


def _detect_version(spec: Dict[str, Any]) -> int:
    if "swagger" in spec:
        return 2
    if "openapi" in spec:
        return 3
    raise ValueError("Missing 'swagger' or 'openapi' key — not a valid spec")


# ---------------------------------------------------------------------------
# Shared schema resolution (root-aware, OAS2 definitions + OAS3 components)
# ---------------------------------------------------------------------------

def _resolve_schema(
    schema: Any,
    root: Dict[str, Any],
    *,
    seen: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Resolve ``$ref`` / shallow ``allOf`` into a concrete schema dict.

    ``root`` is the whole OpenAPI document so both ``#/definitions/X`` and
    ``#/components/schemas/X`` resolve without version-specific forks.
    """
    if not isinstance(schema, dict):
        return {}
    seen = seen if seen is not None else set()

    ref = schema.get("$ref")
    if isinstance(ref, str) and ref:
        if ref in seen:
            return {}
        seen.add(ref)
        resolved = _follow_ref(ref, root)
        # Keep non-ref local keys (rare) over the target; target wins on overlap via update order.
        merged = dict(resolved)
        for k, v in schema.items():
            if k != "$ref":
                merged[k] = v
        return _resolve_schema(merged, root, seen=seen)

    all_of = schema.get("allOf")
    if isinstance(all_of, list) and all_of:
        return _merge_all_of(all_of, root, seen=seen)

    return schema


def _follow_ref(ref: str, root: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return {}
    node: Any = root
    for part in ref.lstrip("#/").split("/"):
        # JSON Pointer ~0 / ~1 escapes
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict):
            return {}
        node = node.get(part)
        if node is None:
            return {}
    return node if isinstance(node, dict) else {}


def _merge_all_of(
    parts: List[Any],
    root: Dict[str, Any],
    *,
    seen: Set[str],
) -> Dict[str, Any]:
    """Merge allOf sub-schemas: properties/required union, first type wins."""
    merged: Dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    required: List[str] = []
    props: Dict[str, Any] = {}
    for part in parts:
        sub = _resolve_schema(part, root, seen=set(seen))
        if not sub:
            continue
        if sub.get("type") and not merged.get("_typed"):
            merged["type"] = sub.get("type")
            merged["_typed"] = True
        for k, v in (sub.get("properties") or {}).items():
            props[k] = v
        for r in sub.get("required") or []:
            if r not in required:
                required.append(r)
        # Copy non-structural keys when useful
        for key in ("description", "title", "example", "default", "items", "format"):
            if key in sub and key not in merged:
                merged[key] = sub[key]
    merged["properties"] = props
    merged["required"] = required
    merged.pop("_typed", None)
    return merged


def _schema_type(schema: Dict[str, Any]) -> str:
    t = schema.get("type")
    if isinstance(t, list):
        # OAS 3.1 nullable unions: pick first non-null
        for item in t:
            if item != "null":
                return str(item)
        return "string"
    if t:
        return str(t)
    if schema.get("properties"):
        return "object"
    if schema.get("items") is not None:
        return "array"
    if "$ref" in schema:
        return "object"
    return "string"


def _schema_desc(schema: Dict[str, Any]) -> str:
    return str(schema.get("description") or schema.get("title") or "")


def _stringify_example(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)
    return str(value)


# ---------------------------------------------------------------------------
# Request parameter projection from body / query schemas
# ---------------------------------------------------------------------------

def _params_from_object_schema(
    schema: Dict[str, Any],
    root: Dict[str, Any],
    *,
    location: str,
    required_fields: Optional[Set[str]] = None,
) -> List[ApiParamDef]:
    """Expand an **object** schema's top-level properties into params.

    Nested object/array properties stay as a single param (type object/array)
    so execution can assemble a flat JSON body matching HTTP conventions:
    ``{ field: value }`` — not dotted fake keys.
    """
    schema = _resolve_schema(schema, root)
    props = schema.get("properties") or {}
    if not isinstance(props, dict) or not props:
        return []

    required = set(required_fields or [])
    required.update(schema.get("required") or [])

    params: List[ApiParamDef] = []
    for name, prop_raw in props.items():
        prop = _resolve_schema(prop_raw, root)
        ptype = _schema_type(prop)
        desc = _schema_desc(prop)
        # Summarize nested object fields in description for UI/LLM.
        if ptype == "object" and prop.get("properties"):
            nested_names = list((prop.get("properties") or {}).keys())
            if nested_names:
                tip = "fields: " + ", ".join(nested_names[:20])
                desc = f"{desc} ({tip})".strip() if desc else tip
        elif ptype == "array":
            items = _resolve_schema(prop.get("items") or {}, root)
            item_props = list((items.get("properties") or {}).keys()) if items else []
            if item_props:
                tip = "item fields: " + ", ".join(item_props[:20])
                desc = f"{desc} ({tip})".strip() if desc else tip

        default = prop.get("default")
        example = prop.get("example")
        if example is None and isinstance(prop.get("examples"), list) and prop["examples"]:
            example = prop["examples"][0]

        params.append(ApiParamDef(
            name=str(name),
            type=ptype or "string",
            required=str(name) in required,
            default=_stringify_example(default),
            description=desc,
            location=location,
            example=_stringify_example(example),
        ))
    return params


def _project_body_schema(
    schema: Any,
    root: Dict[str, Any],
    *,
    body_required: bool,
    fallback_name: str = "body",
    fallback_description: str = "",
) -> Tuple[List[ApiParamDef], str]:
    """Project a request body schema into ``(params, body_mode)``.

    Contract (feeds ``ApiEndpointDef.body_mode`` + HTTP JSON assembly):
    - object DTO with properties → top-level field params, ``body_mode="object"``
      (JSON body keys are field names; OpenAPI parameter name is discarded)
    - free-form object / array / primitive → one body param, ``body_mode="raw"``
      (param value *is* the JSON body; parameter name is documentation-only)
    - empty schema → ``([], "object")``
    """
    if not schema:
        return [], "object"
    resolved = _resolve_schema(schema, root)
    if not resolved:
        return [], "object"

    stype = _schema_type(resolved)

    if stype == "object":
        expanded = _params_from_object_schema(resolved, root, location="body")
        if expanded:
            return expanded, "object"
        # free-form object (no declared properties)
        return [ApiParamDef(
            name=fallback_name,
            type="object",
            required=body_required,
            description=fallback_description or _schema_desc(resolved),
            location="body",
        )], "raw"

    if stype == "array":
        items = _resolve_schema(resolved.get("items") or {}, root)
        item_fields = _params_from_object_schema(items, root, location="body") if items else []
        if item_fields:
            tip = "item fields: " + ", ".join(
                f"{p.name}:{p.type}" for p in item_fields[:30]
            )
            desc = fallback_description or _schema_desc(resolved) or tip
            if fallback_description and tip not in fallback_description:
                desc = f"{fallback_description} ({tip})"
        else:
            item_type = _schema_type(items) if items else "string"
            desc = fallback_description or _schema_desc(resolved) or f"array of {item_type}"
        return [ApiParamDef(
            name=fallback_name,
            type="array",
            required=body_required,
            description=desc,
            location="body",
        )], "raw"

    # primitive body (rare)
    return [ApiParamDef(
        name=fallback_name,
        type=stype or "string",
        required=body_required,
        description=fallback_description or _schema_desc(resolved),
        location="body",
        default=_stringify_example(resolved.get("default")),
        example=_stringify_example(resolved.get("example")),
    )], "raw"


def _param_from_parameter_object(
    p: Dict[str, Any],
    root: Dict[str, Any],
) -> Optional[ApiParamDef]:
    """OAS2/OAS3 non-body parameter (query/header/path/formData/cookie)."""
    if not isinstance(p, dict):
        return None
    # Parameter may itself be a $ref
    p = _resolve_schema(p, root)
    if not p or p.get("in") == "body":
        return None

    location = p.get("in") or "query"
    # formData → body for assembly (send as form-ish JSON body keys)
    if location == "formData":
        location = "body"
    if location == "cookie":
        location = "header"

    schema = p.get("schema")
    if isinstance(schema, dict) and schema:
        schema = _resolve_schema(schema, root)
        ptype = _schema_type(schema) if schema else (p.get("type") or "string")
        default = schema.get("default") if schema else p.get("default")
        example = schema.get("example") if schema else p.get("example")
        desc = p.get("description") or (_schema_desc(schema) if schema else "")
    else:
        # Swagger 2.0 non-body params declare type on the parameter itself
        ptype = p.get("type") or "string"
        default = p.get("default")
        example = p.get("example") or p.get("x-example")
        desc = p.get("description") or ""
        # items for array
        if ptype == "array" and isinstance(p.get("items"), dict):
            item_t = p["items"].get("type") or "string"
            desc = desc or f"array of {item_t}"

    name = p.get("name") or ""
    if not name:
        return None
    return ApiParamDef(
        name=name,
        type=str(ptype or "string"),
        required=bool(p.get("required", location == "path")),
        default=_stringify_example(default),
        description=desc,
        location=str(location),
        example=_stringify_example(example),
    )


# ---------------------------------------------------------------------------
# Response field projection
# ---------------------------------------------------------------------------

def _response_fields_from_schema(
    schema: Any,
    root: Dict[str, Any],
    *,
    prefix: str = "",
    depth: int = 0,
) -> List[ApiResponseFieldDef]:
    """Flatten response object schema into leaf fields (shared OAS2 / OAS3)."""
    if depth > 6 or not schema:
        return []
    schema = _resolve_schema(schema, root)
    if not schema:
        return []

    stype = _schema_type(schema)
    fields: List[ApiResponseFieldDef] = []

    # Envelope arrays: take item shape (row fields)
    if stype == "array":
        items = schema.get("items") or {}
        return _response_fields_from_schema(items, root, prefix=prefix, depth=depth + 1)

    props = schema.get("properties") or {}
    if not props:
        # allOf already merged in _resolve_schema; free-form object → no fields
        return []

    for name, prop_raw in props.items():
        prop = _resolve_schema(prop_raw, root)
        field_path = f"{prefix}{name}" if prefix else str(name)
        ptype = _schema_type(prop)
        desc = _schema_desc(prop)

        if ptype == "object" and (prop.get("properties") or prop.get("allOf")):
            nested = _response_fields_from_schema(
                prop, root, prefix=f"{field_path}.", depth=depth + 1,
            )
            if nested:
                fields.extend(nested)
            else:
                fields.append(ApiResponseFieldDef(
                    name=field_path, type="object", description=desc, path=field_path,
                ))
        elif ptype == "array":
            items = _resolve_schema(prop.get("items") or {}, root)
            if items.get("properties") or items.get("allOf") or items.get("$ref"):
                nested = _response_fields_from_schema(
                    items, root, prefix=f"{field_path}[].", depth=depth + 1,
                )
                if nested:
                    fields.extend(nested)
                else:
                    fields.append(ApiResponseFieldDef(
                        name=field_path, type="array", description=desc, path=field_path,
                    ))
            else:
                fields.append(ApiResponseFieldDef(
                    name=field_path, type="array", description=desc, path=field_path,
                ))
        else:
            fields.append(ApiResponseFieldDef(
                name=field_path, type=ptype or "string", description=desc, path=field_path,
            ))
    return fields


def _pick_json_content(content: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(content, dict):
        return {}
    for key in _JSON_CONTENT_KEYS:
        if key in content and isinstance(content[key], dict):
            return content[key]
    # any +json / java vendor types
    for key, val in content.items():
        if isinstance(key, str) and "json" in key.lower() and isinstance(val, dict):
            return val
    # fallback first entry
    for val in content.values():
        if isinstance(val, dict):
            return val
    return {}


def _success_response(responses: Any) -> Dict[str, Any]:
    if not isinstance(responses, dict):
        return {}
    for code in ("200", "201", "202", "default"):
        if code in responses and isinstance(responses[code], dict):
            return responses[code]
    # first 2xx
    for code, resp in responses.items():
        if isinstance(code, str) and code.startswith("2") and isinstance(resp, dict):
            return resp
    return {}


# ---------------------------------------------------------------------------
# Shared operation projection (OAS2 + OAS3)
# ---------------------------------------------------------------------------

def _merge_parameters(path_level: List[Any], op_level: List[Any]) -> List[Dict[str, Any]]:
    """Merge path-level and operation-level parameters; op wins by (name, in)."""
    merged: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for p in list(path_level or []) + list(op_level or []):
        if not isinstance(p, dict):
            continue
        if "$ref" in p:
            key = ("$ref", p["$ref"])
        else:
            key = (str(p.get("name", "")), str(p.get("in", "")))
        merged[key] = p
    return list(merged.values())


def _params_from_non_body(
    parameters: List[Any],
    root: Dict[str, Any],
) -> List[ApiParamDef]:
    params: List[ApiParamDef] = []
    for raw in parameters:
        p = raw if isinstance(raw, dict) else {}
        p = _resolve_schema(p, root)
        if not p or p.get("in") == "body":
            continue
        param = _param_from_parameter_object(p, root)
        if param is not None:
            params.append(param)
    return params


def _swagger2_body_projection(
    parameters: List[Any],
    root: Dict[str, Any],
) -> Tuple[List[ApiParamDef], str]:
    """First body parameter (Swagger 2.0) → `(body_params, body_mode)`.

    Swagger allows only one body parameter per operation; extra body entries
    are ignored to keep a single assembly rule.
    """
    for raw in parameters:
        p = raw if isinstance(raw, dict) else {}
        p = _resolve_schema(p, root)
        if not p or p.get("in") != "body":
            continue
        return _project_body_schema(
            p.get("schema") or {},
            root,
            body_required=bool(p.get("required", False)),
            fallback_name=p.get("name") or "body",
            fallback_description=p.get("description") or "",
        )
    return [], "object"


def _openapi3_body_projection(
    op: Dict[str, Any],
    root: Dict[str, Any],
) -> Tuple[List[ApiParamDef], str]:
    body = op.get("requestBody") or {}
    body = _resolve_schema(body, root)
    if not body:
        return [], "object"
    content = body.get("content") or {}
    json_content = _pick_json_content(content)
    body_schema = json_content.get("schema") if json_content else None
    if not body_schema:
        return [], "object"
    return _project_body_schema(
        body_schema,
        root,
        body_required=bool(body.get("required", False)),
        fallback_name="body",
        fallback_description=body.get("description") or "",
    )


# Sibling keys treated as business-status when present alongside a data array.
_ENVELOPE_CODE_KEYS = ("code", "status", "statusCode", "status_code", "errcode", "errCode")


def _success_response_schema(
    op: Dict[str, Any],
    root: Dict[str, Any],
    *,
    oas_version: int,
) -> Any:
    ok = _success_response(op.get("responses") or {})
    ok = _resolve_schema(ok, root)
    if not ok:
        return None
    if oas_version == 2:
        return ok.get("schema")
    content = ok.get("content") or {}
    json_content = _pick_json_content(content)
    return json_content.get("schema") if json_content else None


def _response_projection_from_schema(
    schema: Any,
    root: Dict[str, Any],
) -> Tuple[List[ApiResponseFieldDef], str, str]:
    """Derive (response_fields, data_path, code_path) from a 2xx body schema.

    Selection rules (protocol extraction relies on them):
    1. Root array-of-object → fields = item leaves, data_path empty.
    2. Object with one (or more) array-of-object properties → first such property
       becomes ``data_path``; fields = its item leaves (relative); sibling envelope
       fields (code/message/…) are **not** columns.
    3. Otherwise flatten the object. Prefer short top-level leaves; keep nested
       path as ``a.b`` (no ``[]``).
    """
    schema = _resolve_schema(schema, root)
    if not schema:
        return [], "", ""

    stype = _schema_type(schema)

    # Root is the row list itself.
    if stype == "array":
        items = _resolve_schema(schema.get("items") or {}, root)
        fields = _response_fields_from_schema(items, root, prefix="", depth=0)
        return _strip_array_tokens(fields), "", ""

    props = schema.get("properties") or {}
    if not isinstance(props, dict) or not props:
        return [], "", ""

    code_path = ""
    for key in _ENVELOPE_CODE_KEYS:
        if key in props:
            code_path = key
            break

    # Prefer first array-of-objects as the row source (common {code,data[],message}).
    data_path = ""
    item_fields: List[ApiResponseFieldDef] = []
    for prop_name, prop_raw in props.items():
        prop = _resolve_schema(prop_raw, root)
        if _schema_type(prop) != "array":
            continue
        items = _resolve_schema(prop.get("items") or {}, root)
        if not (items.get("properties") or items.get("allOf") or items.get("$ref")):
            continue
        nested = _response_fields_from_schema(items, root, prefix="", depth=0)
        nested = _strip_array_tokens(nested)
        if nested:
            data_path = str(prop_name)
            item_fields = nested
            break

    if item_fields:
        return item_fields, data_path, code_path

    # No array-of-objects: flatten whole body. Drop pure empty free-form.
    fields = _strip_array_tokens(_response_fields_from_schema(schema, root, prefix="", depth=0))
    return fields, "", code_path


def _strip_array_tokens(fields: List[ApiResponseFieldDef]) -> List[ApiResponseFieldDef]:
    """Remove JSONPath-style ``[]`` from names/paths produced by nested flatten."""
    cleaned: List[ApiResponseFieldDef] = []
    for f in fields:
        name = (f.name or "").replace("[]", "")
        path = (f.path or f.name or "").replace("[]", "")
        # Collapse accidental empty segments: "data..x" after stripping is rare;
        # double-dot cleanup for safety.
        while ".." in name:
            name = name.replace("..", ".")
        while ".." in path:
            path = path.replace("..", ".")
        name = name.strip(".")
        path = path.strip(".")
        if not name:
            continue
        cleaned.append(
            ApiResponseFieldDef(
                name=name,
                type=f.type or "string",
                description=f.description or "",
                path=path or name,
            )
        )
    return cleaned


def _response_fields_for_op(
    op: Dict[str, Any],
    root: Dict[str, Any],
    *,
    oas_version: int,
) -> List[ApiResponseFieldDef]:
    schema = _success_response_schema(op, root, oas_version=oas_version)
    if not schema:
        return []
    fields, _, _ = _response_projection_from_schema(schema, root)
    return fields


def _endpoint_from_operation(
    *,
    name: str,
    path: str,
    method: str,
    op: Dict[str, Any],
    path_params: List[Any],
    root: Dict[str, Any],
    oas_version: int,
) -> ApiEndpointDef:
    """Single construction path for both Swagger2 and OpenAPI3."""
    merged = _merge_parameters(path_params, op.get("parameters") or [])
    non_body = _params_from_non_body(merged, root)
    if oas_version == 2:
        body_params, body_mode = _swagger2_body_projection(merged, root)
    else:
        body_params, body_mode = _openapi3_body_projection(op, root)

    schema = _success_response_schema(op, root, oas_version=oas_version)
    if schema:
        response_fields, data_path, code_path = _response_projection_from_schema(schema, root)
    else:
        response_fields, data_path, code_path = [], "", ""

    return ApiEndpointDef(
        name=name,
        path=path,
        method=method.upper(),
        description=op.get("summary") or op.get("description") or "",
        params=non_body + body_params,
        response_fields=response_fields,
        body_mode=body_mode,
        data_path=data_path,
        code_path=code_path,
    )


# ---------------------------------------------------------------------------
# Swagger 2.0 / OpenAPI 3.x path walkers (thin shells over shared projection)
# ---------------------------------------------------------------------------

def _walk_paths(spec: Dict[str, Any], *, oas_version: int) -> List[ApiEndpointDef]:
    paths: Dict[str, Any] = spec.get("paths") or {}
    endpoints: List[ApiEndpointDef] = []
    seen_names: set[str] = set()

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        path_params = path_item.get("parameters") or []
        for method in _HTTP_METHODS:
            op = path_item.get(method)
            if not isinstance(op, dict):
                continue
            name = _make_unique_name(
                op.get("operationId") or f"{method}_{path}",
                seen_names,
            )
            endpoints.append(_endpoint_from_operation(
                name=name,
                path=path,
                method=method,
                op=op,
                path_params=path_params,
                root=spec,
                oas_version=oas_version,
            ))
    return endpoints


# ---------------------------------------------------------------------------
# Name helpers
# ---------------------------------------------------------------------------

def _sanitize_name(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip().strip("/"))
    name = re.sub(r"_+", "_", name).strip("_")
    return name[:120] if name else "endpoint"


def _make_unique_name(candidate: str, seen: set[str]) -> str:
    base = _sanitize_name(candidate)
    name = base
    counter = 2
    while name in seen:
        name = f"{base}_{counter}"
        counter += 1
    seen.add(name)
    return name

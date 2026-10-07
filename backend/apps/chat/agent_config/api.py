"""Admin API for the versioned agent configuration (prompt / tools / loop bounds)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from apps.chat.agent_config.defaults import (
    DEFAULT_TOOL_NAMES,
    LOOP_PARAM_SPECS,
    REQUIRED_TOOL_NAMES,
    SQL_RULE_SPECS,
)
from apps.chat.agent_config.models import (
    AgentConfigDetail,
    AgentConfigSaveRequest,
)
from apps.chat.agent_config.service import (
    MAX_CHANGE_NOTE_CHARS,
    MAX_DESCRIPTION_CHARS,
    MAX_PROMPT_CHARS,
    MAX_TOOL_ROUND_BUDGET,
    MIN_PROMPT_CHARS,
    MIN_TOOL_ROUND_BUDGET,
    PLACEHOLDER,
    REQUIRED_PROMPT_MARKERS,
    ConfigValidationError,
    get_detail,
    publish_draft,
    rollback_to,
    save_draft,
)
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from common.audit.models.log_model import OperationModules, OperationType
from common.audit.schemas.logger_decorator import LogConfig, system_log
from common.core.deps import CurrentUser, SessionDep, Trans

router = APIRouter(tags=["system/agent_config"], prefix="/system/agent_config")


def _bad_request(exc: ConfigValidationError, trans: Any) -> HTTPException:
    message = str(trans(exc.key))
    if exc.detail:
        message = f"{message}: {exc.detail}"
    return HTTPException(status_code=400, detail=message)


@router.get("", response_model=AgentConfigDetail)
@require_permissions(permission=SqlbotPermission(role=["admin"]))
async def read_agent_config(session: SessionDep) -> AgentConfigDetail:
    """Effective snapshot (draft > published > code defaults) plus history."""
    return get_detail(session)


def build_meta() -> dict[str, Any]:
    """Field metadata so the page never hard-codes tools or param bounds."""
    return {
        "prompt": {
            "min_chars": MIN_PROMPT_CHARS,
            "max_chars": MAX_PROMPT_CHARS,
            "placeholder": PLACEHOLDER,
            "required_markers": list(REQUIRED_PROMPT_MARKERS),
        },
        "tool_description_max_chars": MAX_DESCRIPTION_CHARS,
        "tool_round_budget": {
            "min": MIN_TOOL_ROUND_BUDGET,
            "max": MAX_TOOL_ROUND_BUDGET,
        },
        "change_note_max_chars": MAX_CHANGE_NOTE_CHARS,
        "params": [
            {
                "key": spec.key,
                "default": spec.default,
                "minimum": spec.minimum,
                "maximum": spec.maximum,
                "label_key": f"agent_config.params.{spec.label_key}",
            }
            for spec in LOOP_PARAM_SPECS
        ],
        "tool_names": list(DEFAULT_TOOL_NAMES),
        "required_tool_names": sorted(REQUIRED_TOOL_NAMES),
        "sql_rules": [
            {
                "key": spec.kind,
                "default_enabled": spec.enabled,
                "label_key": f"agent_config.sql_rules.{spec.label_key}",
            }
            for spec in SQL_RULE_SPECS
        ],
    }


@router.get("/meta")
@require_permissions(permission=SqlbotPermission(role=["admin"]))
async def read_agent_config_meta() -> dict[str, Any]:
    return build_meta()


@router.put("", response_model=AgentConfigDetail)
@require_permissions(permission=SqlbotPermission(role=["admin"]))
@system_log(
    LogConfig(
        operation_type=OperationType.UPDATE,
        module=OperationModules.SETTING,
    )
)
async def write_agent_config_draft(
    session: SessionDep,
    user: CurrentUser,
    trans: Trans,
    payload: AgentConfigSaveRequest,
) -> AgentConfigDetail:
    try:
        return save_draft(session, payload, user_id=int(user.id) if user.id else None)
    except ConfigValidationError as exc:
        raise _bad_request(exc, trans) from exc


@router.post("/publish", response_model=AgentConfigDetail)
@require_permissions(permission=SqlbotPermission(role=["admin"]))
@system_log(
    LogConfig(
        operation_type=OperationType.UPDATE,
        module=OperationModules.SETTING,
    )
)
async def publish_agent_config(
    session: SessionDep,
    user: CurrentUser,
    trans: Trans,
) -> AgentConfigDetail:
    try:
        return publish_draft(session, user_id=int(user.id) if user.id else None)
    except ConfigValidationError as exc:
        raise _bad_request(exc, trans) from exc


@router.post("/rollback/{version_id}", response_model=AgentConfigDetail)
@require_permissions(permission=SqlbotPermission(role=["admin"]))
@system_log(
    LogConfig(
        operation_type=OperationType.UPDATE,
        module=OperationModules.SETTING,
        resource_id_expr="version_id",
    )
)
async def rollback_agent_config(
    session: SessionDep,
    user: CurrentUser,
    trans: Trans,
    version_id: int,
) -> AgentConfigDetail:
    try:
        return rollback_to(
            session, version_id, user_id=int(user.id) if user.id else None
        )
    except ConfigValidationError as exc:
        raise _bad_request(exc, trans) from exc

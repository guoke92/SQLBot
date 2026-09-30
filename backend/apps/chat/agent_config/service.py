"""Draft / publish / rollback service for the agent configuration page.

History is append-only: publishing never overwrites a row, and rollback writes a
*new* revision carrying the old body, so the audit trail stays complete.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlmodel import Session, func, select

from apps.chat.agent_config.defaults import (
    LOOP_PARAM_SPECS,
    REQUIRED_TOOL_NAMES,
    default_tools,
)
from apps.chat.agent_config.loader import (
    merge_loop_params,
    merge_tools,
)
from apps.chat.agent_config.models import (
    SCOPE_GLOBAL,
    AgentConfigDetail,
    AgentConfigSaveRequest,
    AgentConfigSnapshot,
    AgentConfigStatus,
    AgentConfigVersion,
    AgentConfigVersionRead,
    ToolOverride,
)
from common.utils.utils import SQLBotLogUtil

MIN_PROMPT_CHARS = 800
MAX_PROMPT_CHARS = 40_000
MAX_DESCRIPTION_CHARS = 2_000
MAX_CHANGE_NOTE_CHARS = 255
MIN_TOOL_ROUND_BUDGET = 0
MAX_TOOL_ROUND_BUDGET = 20
PLACEHOLDER = "{execution_limit}"
#: Distinct from any digit sequence in the shipped prompt, so a successful
#: ``str.format`` that merely echoes escaped braces still fails this check.
_RENDER_SENTINEL = 917_353

#: Tripwire against saving a truncated prompt. Defined here so relaxing the
#: French/English rewrite of the system prompt is a one-line change.
REQUIRED_PROMPT_MARKERS: tuple[str, ...] = ("## 用户可见文案", "## 1.", "## 3.")

_SPECS_BY_KEY = {spec.key: spec for spec in LOOP_PARAM_SPECS}


class ConfigValidationError(ValueError):
    """Validation failure carrying an i18n key for the API layer to translate."""

    def __init__(self, key: str, detail: str | None = None) -> None:
        super().__init__(key)
        self.key = key
        self.detail = detail


def default_snapshot() -> AgentConfigSnapshot:
    """What a fresh install runs — used to seed the editor on first open."""
    from apps.chat.task.agent_prompt import _SHARED_PROMPT_TEMPLATE

    return AgentConfigSnapshot(
        prompt_body=_SHARED_PROMPT_TEMPLATE,
        tools={name: dict(cfg) for name, cfg in default_tools().items()},
        loop_params={spec.key: spec.default for spec in LOOP_PARAM_SPECS},
        change_note=None,
    )


def validate_snapshot(payload: AgentConfigSnapshot) -> AgentConfigSnapshot:
    """Reject anything that would break the runtime; returns the cleaned copy."""
    body = str(payload.prompt_body or "")
    if not body.strip():
        raise ConfigValidationError("agent_config.err_prompt_empty")
    if not (MIN_PROMPT_CHARS <= len(body) <= MAX_PROMPT_CHARS):
        raise ConfigValidationError(
            "agent_config.err_prompt_length",
            detail=f"{MIN_PROMPT_CHARS}-{MAX_PROMPT_CHARS}",
        )
    if PLACEHOLDER not in body:
        raise ConfigValidationError("agent_config.err_prompt_placeholder_missing")
    # The same call the runtime makes. Unknown fields and stray braces fail
    # here; escaped ``{{...}}`` literals pass. The sentinel must survive into
    # the rendered text, so a fully escaped ``{{execution_limit}}`` does not.
    try:
        rendered = body.format(execution_limit=_RENDER_SENTINEL)
    except (KeyError, IndexError, ValueError) as exc:
        raise ConfigValidationError(
            "agent_config.err_prompt_placeholder_invalid", detail=str(exc)
        ) from exc
    if str(_RENDER_SENTINEL) not in rendered:
        raise ConfigValidationError("agent_config.err_prompt_placeholder_missing")
    missing = [marker for marker in REQUIRED_PROMPT_MARKERS if marker not in body]
    if missing:
        raise ConfigValidationError(
            "agent_config.err_prompt_section_missing", detail=", ".join(missing)
        )

    cleaned_tools: dict[str, ToolOverride] = {}
    known = set(default_tools())
    for name in payload.tools or {}:
        if name not in known:
            raise ConfigValidationError(
                "agent_config.err_tool_unknown", detail=str(name)
            )
    for name, override in (payload.tools or {}).items():
        if not override.enabled and name in REQUIRED_TOOL_NAMES:
            raise ConfigValidationError("agent_config.err_tool_required", detail=name)
        if override.description and len(override.description) > MAX_DESCRIPTION_CHARS:
            raise ConfigValidationError(
                "agent_config.err_tool_description", detail=name
            )
        budget = override.round_budget
        if budget is not None and not (
            MIN_TOOL_ROUND_BUDGET <= budget <= MAX_TOOL_ROUND_BUDGET
        ):
            raise ConfigValidationError("agent_config.err_tool_budget", detail=name)
        cleaned_tools[name] = ToolOverride(
            enabled=override.enabled,
            description=(override.description or "").strip() or None,
            parallel_safe=override.parallel_safe,
            round_budget=budget,
        )

    loop_params: dict[str, int] = {}
    for key, value in (payload.loop_params or {}).items():
        spec = _SPECS_BY_KEY.get(key)
        if spec is None:
            raise ConfigValidationError(
                "agent_config.err_param_unknown", detail=str(key)
            )
        if isinstance(value, bool) or not isinstance(value, int):
            raise ConfigValidationError("agent_config.err_param_type", detail=str(key))
        if not (spec.minimum <= value <= spec.maximum):
            raise ConfigValidationError(
                "agent_config.err_param_range",
                detail=f"{key}: {spec.minimum}-{spec.maximum}",
            )
        loop_params[key] = int(value)

    note = payload.change_note
    if note is not None and len(str(note)) > MAX_CHANGE_NOTE_CHARS:
        raise ConfigValidationError("agent_config.err_note_length")

    return AgentConfigSnapshot(
        prompt_body=body,
        tools=cleaned_tools,
        loop_params=loop_params,
        change_note=str(note) if note else None,
    )


def _select_versions(limit: int | None = None) -> Any:
    stmt = (
        select(AgentConfigVersion)
        .where(AgentConfigVersion.scope_key == SCOPE_GLOBAL)
        .order_by(AgentConfigVersion.version_no.desc())  # type: ignore[arg-type]
    )
    return stmt.limit(limit) if limit else stmt


def get_draft(session: Session) -> AgentConfigVersion | None:
    return session.exec(
        select(AgentConfigVersion)
        .where(AgentConfigVersion.scope_key == SCOPE_GLOBAL)
        .where(AgentConfigVersion.status == AgentConfigStatus.DRAFT.value)
        .limit(1)
    ).first()


def get_published(session: Session) -> AgentConfigVersion | None:
    return session.exec(
        select(AgentConfigVersion)
        .where(AgentConfigVersion.scope_key == SCOPE_GLOBAL)
        .where(AgentConfigVersion.status == AgentConfigStatus.PUBLISHED.value)
        .limit(1)
    ).first()


def list_versions(session: Session, limit: int = 50) -> list[AgentConfigVersion]:
    return list(session.exec(_select_versions(limit)).all())


def _next_version_no(session: Session) -> int:
    highest = session.exec(
        select(func.max(AgentConfigVersion.version_no)).where(
            AgentConfigVersion.scope_key == SCOPE_GLOBAL
        )
    ).one()
    return int(highest or 0) + 1


def _snapshot_from_row(row: AgentConfigVersion) -> AgentConfigSnapshot:
    tools = merge_tools(row.tools if isinstance(row.tools, Mapping) else None)
    params = merge_loop_params(
        row.loop_params if isinstance(row.loop_params, Mapping) else None
    )
    return AgentConfigSnapshot(
        prompt_body=str(row.prompt_body or ""),
        tools={
            name: {
                "enabled": cfg["enabled"],
                "description": cfg["description"],
                "parallel_safe": cfg["parallel_safe"],
                "round_budget": cfg["round_budget"],
            }
            for name, cfg in tools.items()
        },
        loop_params=params,
        change_note=row.change_note,
    )


def get_detail(session: Session) -> AgentConfigDetail:
    """Editor payload: draft if present, else published, else code defaults."""
    draft = get_draft(session)
    published = get_published(session)
    if draft is not None:
        snapshot = _snapshot_from_row(draft)
        source = "draft"
    elif published is not None:
        snapshot = _snapshot_from_row(published)
        source = "published"
    else:
        snapshot = default_snapshot()
        source = "code"
    return AgentConfigDetail(
        source=source,
        active_version_no=int(published.version_no) if published is not None else None,
        draft_version_no=int(draft.version_no) if draft is not None else None,
        snapshot=snapshot,
        versions=[
            AgentConfigVersionRead.model_validate(row) for row in list_versions(session)
        ],
    )


def save_draft(
    session: Session, payload: AgentConfigSaveRequest, user_id: int | None
) -> AgentConfigDetail:
    """Create or update the single draft row from the editor payload."""
    cleaned = validate_snapshot(payload)
    stored_tools = {
        name: override.model_dump() for name, override in cleaned.tools.items()
    }
    now = datetime.now()
    draft = get_draft(session)
    if draft is None:
        draft = AgentConfigVersion(
            scope_key=SCOPE_GLOBAL,
            version_no=_next_version_no(session),
            status=AgentConfigStatus.DRAFT.value,
            prompt_body=cleaned.prompt_body,
            tools=stored_tools,
            loop_params=dict(cleaned.loop_params),
            change_note=cleaned.change_note,
            create_by=user_id,
            create_time=now,
        )
    else:
        draft.prompt_body = cleaned.prompt_body
        draft.tools = stored_tools
        draft.loop_params = dict(cleaned.loop_params)
        draft.change_note = cleaned.change_note
        draft.create_by = user_id
    session.add(draft)
    session.commit()
    return get_detail(session)


def publish_draft(session: Session, user_id: int | None) -> AgentConfigDetail:
    """Promote the draft to published, archiving the previous revision."""
    draft = get_draft(session)
    if draft is None:
        raise ConfigValidationError("agent_config.err_no_draft")
    validate_snapshot(_snapshot_from_row(draft))
    now = datetime.now()
    previous = get_published(session)
    if previous is not None:
        previous.status = AgentConfigStatus.ARCHIVED.value
        session.add(previous)
    draft.status = AgentConfigStatus.PUBLISHED.value
    draft.published_by = user_id
    draft.published_time = now
    session.add(draft)
    session.commit()
    activate_published(draft)
    return get_detail(session)


def rollback_to(
    session: Session, version_id: int, user_id: int | None
) -> AgentConfigDetail:
    """Re-publish the body of a historical revision as a new revision."""
    row = session.get(AgentConfigVersion, int(version_id))
    if row is None or row.scope_key != SCOPE_GLOBAL:
        raise ConfigValidationError("agent_config.err_version_not_found")
    validate_snapshot(_snapshot_from_row(row))
    now = datetime.now()
    previous = get_published(session)
    if previous is not None:
        previous.status = AgentConfigStatus.ARCHIVED.value
        session.add(previous)
    restored = AgentConfigVersion(
        scope_key=SCOPE_GLOBAL,
        version_no=_next_version_no(session),
        status=AgentConfigStatus.PUBLISHED.value,
        prompt_body=str(row.prompt_body or ""),
        tools=dict(row.tools or {}),
        loop_params=dict(row.loop_params or {}),
        change_note=f"rollback -> v{row.version_no}"[:MAX_CHANGE_NOTE_CHARS],
        create_by=user_id,
        create_time=now,
        published_by=user_id,
        published_time=now,
    )
    session.add(restored)
    # A stale draft would silently shadow the rollback on the next page load.
    draft = get_draft(session)
    if draft is not None:
        session.delete(draft)
    session.commit()
    activate_published(restored)
    return get_detail(session)


def activate_published(row: AgentConfigVersion) -> None:
    """Install a just-published row into the process cache. No extra DB read."""
    from apps.chat.agent_config.loader import config_from_row, install_agent_config

    install_agent_config(config_from_row(row))
    SQLBotLogUtil.info("agent config: published v%s is now live", row.version_no)

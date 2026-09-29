"""Versioned agent runtime configuration: system prompt + tool overrides + loop bounds.

One row per revision. At most one ``published`` and one ``draft`` row may exist
per scope (enforced by partial unique indexes), so the management page can
"save draft -> publish -> rollback" without ever losing history.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Identity,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

SCOPE_GLOBAL = "global"


class AgentConfigStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AgentConfigVersion(SQLModel, table=True):
    __tablename__ = "agent_config_version"
    __table_args__ = (
        Index("ix_agent_config_version_scope_status", "scope_key", "status"),
        Index(
            "uq_agent_config_version_no",
            "scope_key",
            "version_no",
            unique=True,
        ),
        # Database-level guarantee: at most one published / one draft per scope.
        Index(
            "uq_agent_config_version_published",
            "scope_key",
            unique=True,
            postgresql_where=text("status = 'published'"),
        ),
        Index(
            "uq_agent_config_version_draft",
            "scope_key",
            unique=True,
            postgresql_where=text("status = 'draft'"),
        ),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    scope_key: str = Field(
        default=SCOPE_GLOBAL,
        sa_column=Column(
            String(64), nullable=False, server_default=text(f"'{SCOPE_GLOBAL}'")
        ),
    )
    version_no: int = Field(sa_column=Column(Integer, nullable=False))
    status: str = Field(sa_column=Column(String(16), nullable=False))
    prompt_body: str = Field(sa_column=Column(Text, nullable=False))
    tools: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    )
    loop_params: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    )
    change_note: str | None = Field(
        default=None, sa_column=Column(String(255), nullable=True)
    )
    create_by: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    create_time: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    published_by: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    published_time: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )


class ToolOverride(BaseModel):
    """Per-tool override; ``None`` means "inherit the code default"."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    description: str | None = None
    parallel_safe: bool | None = None
    round_budget: int | None = None


class AgentConfigSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt_body: str
    tools: dict[str, ToolOverride] = PydanticField(default_factory=dict)
    loop_params: dict[str, int] = PydanticField(default_factory=dict)
    change_note: str | None = None


class AgentConfigSaveRequest(AgentConfigSnapshot):
    pass


class AgentConfigVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_no: int
    status: str
    change_note: str | None = None
    create_by: int | None = None
    create_time: datetime
    published_by: int | None = None
    published_time: datetime | None = None


class AgentConfigDetail(BaseModel):
    """What the management page edits: effective snapshot + history."""

    source: str  # "db" | "code"
    active_version_no: int | None = None
    draft_version_no: int | None = None
    snapshot: AgentConfigSnapshot
    versions: list[AgentConfigVersionRead] = PydanticField(default_factory=list)

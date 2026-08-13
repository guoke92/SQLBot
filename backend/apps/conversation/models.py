"""Durable conversation run, interrupt, and NLQ evidence models.

``ChatRecord`` remains the user-visible message/result aggregate.  These
models own workflow state so transport events and message rows never have to
double as a scheduler or a semantic contract store.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


def new_id() -> str:
    return str(uuid4())


class ConversationRun(SQLModel, table=True):
    __tablename__ = "conversation_run"

    run_id: str = Field(
        default_factory=new_id,
        sa_column=Column(String(36), primary_key=True),
    )
    chat_record_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("chat_record.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )
    )
    graph_key: str = Field(sa_column=Column(String(32), nullable=False))
    status: str = Field(
        default="queued",
        sa_column=Column(String(24), nullable=False, index=True),
    )
    current_node: str | None = Field(
        default=None, sa_column=Column(String(64), nullable=True)
    )
    checkpoint_id: str | None = Field(
        default=None, sa_column=Column(String(128), nullable=True)
    )
    active_interrupt_id: str | None = Field(
        default=None, sa_column=Column(String(36), nullable=True)
    )
    user_id: int = Field(sa_column=Column(BigInteger, nullable=False, index=True))
    assistant_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True)
    )
    oid: int = Field(default=1, sa_column=Column(BigInteger, nullable=False))
    event_cursor: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    dispatch_attempts: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, default=0)
    )
    error_summary: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    started_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    completed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )
    create_time: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )
    update_time: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )


class ConversationInterrupt(SQLModel, table=True):
    __tablename__ = "conversation_interrupt"
    __table_args__ = (
        UniqueConstraint("run_id", "version", name="uq_interrupt_run_version"),
        UniqueConstraint("run_id", "idempotency_key", name="uq_interrupt_idempotency"),
    )

    interrupt_id: str = Field(
        default_factory=new_id,
        sa_column=Column(String(36), primary_key=True),
    )
    run_id: str = Field(
        sa_column=Column(
            String(36),
            ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    version: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    status: str = Field(
        default="open", sa_column=Column(String(20), nullable=False, index=True)
    )
    payload: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False, default=dict)
    )
    answers: list[dict[str, Any]] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    idempotency_key: str | None = Field(
        default=None, sa_column=Column(String(128), nullable=True)
    )
    create_time: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )
    consumed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )


class ConversationRunEvent(SQLModel, table=True):
    __tablename__ = "conversation_run_event"
    __table_args__ = (UniqueConstraint("run_id", "cursor", name="uq_run_event_cursor"),)

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    run_id: str = Field(
        sa_column=Column(
            String(36),
            ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    cursor: int = Field(sa_column=Column(Integer, nullable=False))
    payload: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    create_time: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )


class NlqRun(SQLModel, table=True):
    __tablename__ = "nlq_run"

    run_id: str = Field(
        sa_column=Column(
            String(36),
            ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    active_specification_revision: int = Field(
        default=0, sa_column=Column(Integer, nullable=False)
    )
    specifications: list[dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False, default=list)
    )
    # Durable input boundary for semantic planning.  Request-local LLMService
    # objects are deliberately not checkpointed; the context they assembled
    # must nevertheless survive a process restart that resumes immediately
    # before ``plan_query``.
    planning_context: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False, default=dict)
    )
    planning_status: str = Field(
        default="pending", sa_column=Column(String(24), nullable=False)
    )
    active_plan_id: str | None = Field(
        default=None, sa_column=Column(String(36), nullable=True)
    )
    plans: list[dict[str, Any]] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False, default=list)
    )
    execution_status: str = Field(
        default="pending", sa_column=Column(String(24), nullable=False)
    )
    executed_plan_ids: list[str] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False, default=list)
    )
    result_quality: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    update_time: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )


class NlqEvidenceEvent(SQLModel, table=True):
    __tablename__ = "nlq_evidence_event"
    __table_args__ = (
        UniqueConstraint("run_id", "sequence", name="uq_nlq_evidence_sequence"),
    )

    evidence_id: str = Field(
        default_factory=new_id,
        sa_column=Column(String(36), primary_key=True),
    )
    run_id: str = Field(
        sa_column=Column(
            String(36),
            ForeignKey("conversation_run.run_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    sequence: int = Field(sa_column=Column(Integer, nullable=False))
    kind: str = Field(sa_column=Column(String(32), nullable=False))
    source: str = Field(sa_column=Column(String(24), nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    structured_value: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    confidence: float = Field(default=1.0, sa_column=Column(Float, nullable=False))
    supersedes: str | None = Field(
        default=None,
        sa_column=Column(
            String(36),
            ForeignKey("nlq_evidence_event.evidence_id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    create_time: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )

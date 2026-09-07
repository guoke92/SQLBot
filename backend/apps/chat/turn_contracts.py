"""Unified routing and terminal answer contracts for a conversation turn."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator


class TurnRoute(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_kind: Literal["query", "analysis", "prediction", "unsupported"]
    relation: Literal["independent", "continue", "revise"] = "independent"
    reference_record_ids: tuple[int, ...] = Field(default=(), max_length=3)
    source: Literal["hint", "deterministic", "model", "fallback"]
    confidence: float = Field(default=1.0, ge=0, le=1)

    @model_validator(mode="after")
    def validate_route(self) -> TurnRoute:
        if self.task_kind == "unsupported" and self.reference_record_ids:
            raise ValueError("Unsupported turns cannot reference result records")
        if self.task_kind == "analysis" and self.relation == "independent":
            raise ValueError("Analysis requires referenced result datasets")
        if self.relation != "independent" and not self.reference_record_ids:
            raise ValueError("Continuation and revision routes require references")
        if len(self.reference_record_ids) != len(set(self.reference_record_ids)):
            raise ValueError("Route references must be unique")
        return self


class AnswerError(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    retryable: bool = False


class AnswerDataset(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)

    dataset_id: str
    status: Literal["succeeded", "degraded", "failed"]
    required: bool = True
    title: str = ""
    sql: str = ""
    fields: tuple[str, ...] = ()
    rows: tuple[dict[str, Any], ...] = ()
    preview_rows: tuple[dict[str, Any], ...] = ()
    row_count: int | None = None
    truncated: bool = False
    limit: int | None = None
    truncation_reason: str | None = None
    presentation: dict[str, Any] | None = None
    chart: dict[str, Any] | None = None
    error: AnswerError | None = None


class AnswerBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal[1] = 1
    answer_revision: int = Field(ge=1)
    source_run_id: str
    status: Literal["succeeded", "degraded", "failed"]
    content: str = ""
    source_record_ids: tuple[int, ...] = ()
    assumptions: tuple[dict[str, Any], ...] = ()
    quality: dict[str, Any] | None = None
    error: AnswerError | None = None


class QueryTurnAnswer(AnswerBase):
    kind: Literal["query"] = "query"
    execution_mode: Literal["verified", "unverified", "agent"] = "verified"
    datasets: tuple[AnswerDataset, ...] = ()
    intent_summary: str = ""


class AnalysisTurnAnswer(AnswerBase):
    kind: Literal["analysis"] = "analysis"
    dataset_ids: tuple[str, ...] = ()
    source_datasets: tuple[AnswerDataset, ...] = ()


class PredictionTurnAnswer(AnswerBase):
    kind: Literal["prediction"] = "prediction"
    dataset_id: str | None = None
    forecast_rows: tuple[dict[str, Any], ...] = ()
    source_datasets: tuple[AnswerDataset, ...] = ()


class UnsupportedTurnAnswer(AnswerBase):
    kind: Literal["unsupported"] = "unsupported"


TurnAnswer = Annotated[
    QueryTurnAnswer | AnalysisTurnAnswer | PredictionTurnAnswer | UnsupportedTurnAnswer,
    Field(discriminator="kind"),
]
TURN_ANSWER_ADAPTER = TypeAdapter(TurnAnswer)

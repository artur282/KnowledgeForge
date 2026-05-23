"""Pydantic schemas for evaluation endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EvalRunRequest(BaseModel):
    """Request schema for running evaluation."""

    name: str = Field(default="auto_eval", min_length=1, max_length=100)
    dataset_path: str | None = Field(
        default=None,
        description="Optional path to custom evaluation dataset JSON file",
    )


class EvalMetricResult(BaseModel):
    """Single metric result."""

    name: str
    score: float


class EvalRunResponse(BaseModel):
    """Response schema for evaluation run."""

    report_id: UUID
    name: str
    faithfulness: float | None
    answer_relevancy: float | None
    context_precision: float | None
    context_recall: float | None
    created_at: datetime


class EvalReportItem(BaseModel):
    """Single report in list response."""

    id: UUID
    name: str
    faithfulness: float | None
    answer_relevancy: float | None
    context_precision: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvalReportsResponse(BaseModel):
    """Response schema for listing evaluation reports."""

    reports: list[EvalReportItem]

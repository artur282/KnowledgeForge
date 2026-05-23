"""Pydantic schemas for chat endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for RAG chat."""

    session_id: UUID | None = None
    question: str = Field(..., min_length=1, max_length=2000)


class SourceInfo(BaseModel):
    """Source citation for RAG response."""

    doc_id: UUID
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    """Response schema for RAG chat."""

    answer: str
    sources: list[SourceInfo]
    session_id: UUID


class MessageHistory(BaseModel):
    """Single message in chat history."""

    id: UUID
    role: str
    content: str
    context_used: list = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    """Response schema for chat history."""

    session_id: UUID
    messages: list[MessageHistory]

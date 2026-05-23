"""Pydantic schemas for search endpoints."""

from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request schema for hybrid search."""

    query: str = Field(..., min_length=1, max_length=500)
    k: int = Field(default=10, ge=1, le=100)
    filters: dict | None = None


class SearchResult(BaseModel):
    """Single search result with source info."""

    doc_id: UUID
    chunk_index: int
    content: str
    score: float
    filename: str
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response schema for hybrid search."""

    results: list[SearchResult]
    total: int


class SuggestResponse(BaseModel):
    """Response schema for autocomplete suggestions."""

    suggestions: list[str]

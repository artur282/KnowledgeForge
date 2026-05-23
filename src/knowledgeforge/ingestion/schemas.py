"""Pydantic schemas for ingestion endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Response schema for document details."""

    id: UUID
    filename: str
    status: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""

    status: str = "queued"
    document_id: UUID | None = None

"""HTTP endpoints for document ingestion."""

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.ingestion.repositories import DocumentRepository
from knowledgeforge.ingestion.schemas import DocumentResponse, DocumentUploadResponse
from knowledgeforge.ingestion.services import IngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


async def get_session(request: Request) -> AsyncSession:
    """Get database session from app state."""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def get_ingestion_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> IngestionService:
    """Dependency injection for IngestionService."""
    from knowledgeforge.config import Settings

    settings = Settings()
    es_client = request.app.state.es_client
    return IngestionService(session, es_client, settings)


def get_document_repo(
    session: AsyncSession = Depends(get_session),
) -> DocumentRepository:
    """Dependency injection for DocumentRepository."""
    return DocumentRepository(session)


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=202,
    operation_id="uploadDocument",
)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    ingestion_svc: IngestionService = Depends(get_ingestion_service),
):
    """Upload a document for async ingestion."""
    file_bytes = await file.read()
    doc_id = await ingestion_svc.process(file_bytes, file.filename or "unknown")
    return DocumentUploadResponse(document_id=doc_id)


@router.get(
    "/{doc_id}",
    response_model=DocumentResponse,
    operation_id="getDocumentStatus",
)
async def get_document_status(
    doc_id: UUID,
    repo: DocumentRepository = Depends(get_document_repo),
):
    """Get document processing status."""
    doc = await repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.delete(
    "/{doc_id}",
    status_code=204,
    operation_id="deleteDocument",
)
async def delete_document(
    doc_id: UUID,
    repo: DocumentRepository = Depends(get_document_repo),
):
    """Delete a document and all its chunks."""
    deleted = await repo.delete(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return None

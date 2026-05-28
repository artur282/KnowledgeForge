"""HTTP endpoints for document ingestion."""

import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.deps import get_session, get_settings
from knowledgeforge.ingestion.repositories import DocumentRepository
from knowledgeforge.ingestion.schemas import DocumentResponse, DocumentUploadResponse
from knowledgeforge.ingestion.services import IngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


def get_ingestion_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
    settings=Depends(get_settings),
) -> IngestionService:
    """Dependency injection for IngestionService."""
    es_client = request.app.state.es_client
    return IngestionService(session, es_client, settings, embeddings=request.app.state.embeddings)


def get_document_repo(
    session: AsyncSession = Depends(get_session),
) -> DocumentRepository:
    """Dependency injection for DocumentRepository."""
    return DocumentRepository(session)


async def _process_in_background(
    session_factory,
    es_client,
    settings,
    doc_id: UUID,
    file_bytes: bytes,
    filename: str,
) -> None:
    """Process document in background with its own session."""
    async with session_factory() as session:
        try:
            service = IngestionService(session, es_client, settings)
            doc = await service.doc_repo.get_by_id(doc_id)
            if doc and doc.status in ("ready", "processing"):
                return
            await service.process_existing(doc_id, file_bytes, filename)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=202,
    operation_id="uploadDocument",
)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    request: Request,
    ingestion_svc: IngestionService = Depends(get_ingestion_service),
):
    """Upload a document for async ingestion."""
    file_bytes = await file.read()
    filename = file.filename or "unknown"

    doc_id = await ingestion_svc.create_document(file_bytes, filename)

    background_tasks.add_task(
        _process_in_background,
        request.app.state.session_factory,
        request.app.state.es_client,
        request.app.state.settings,
        doc_id,
        file_bytes,
        filename,
    )

    return DocumentUploadResponse(document_id=doc_id, status="queued")


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

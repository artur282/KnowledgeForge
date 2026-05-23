"""HTTP endpoints for RAG chat."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.chat.repositories import ChatMessageRepository, ChatSessionRepository
from knowledgeforge.chat.schemas import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    MessageHistory,
    SourceInfo,
)
from knowledgeforge.chat.services import RAGChatService
from knowledgeforge.config import Settings
from knowledgeforge.search.services import HybridSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


async def get_session(request: Request) -> AsyncSession:
    """Get database session from app state."""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def get_rag_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> RAGChatService:
    """Dependency injection for RAGChatService."""
    settings = Settings()
    search_service = HybridSearchService(session, request.app.state.es_client)
    return RAGChatService(session, settings, search_service)


@router.post(
    "",
    response_model=ChatResponse,
    operation_id="chat",
)
async def chat(
    request: ChatRequest,
    service: RAGChatService = Depends(get_rag_service),
):
    """Execute RAG Q&A with session memory."""
    answer, sources, session_id = await service.chat(
        question=request.question,
        session_id=request.session_id,
    )

    return ChatResponse(
        answer=answer,
        sources=[SourceInfo(**s) for s in sources],
        session_id=session_id,
    )


@router.get(
    "/{session_id}/history",
    response_model=HistoryResponse,
    operation_id="getChatHistory",
)
async def get_chat_history(
    session_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get chat session message history."""
    session_repo = ChatSessionRepository(session)
    message_repo = ChatMessageRepository(session)

    chat_session = await session_repo.get_by_id(session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await message_repo.get_by_session(session_id)

    return HistoryResponse(
        session_id=session_id,
        messages=[MessageHistory.model_validate(m) for m in messages],
    )

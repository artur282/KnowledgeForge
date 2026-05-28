"""HTTP endpoints for RAG chat."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from openai import OpenAIError
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
from knowledgeforge.db.deps import get_session, get_settings
from knowledgeforge.search.services import HybridSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def get_rag_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
    settings=Depends(get_settings),
) -> RAGChatService:
    """Dependency injection for RAGChatService."""
    search_service = HybridSearchService(
        session,
        request.app.state.es_client,
        settings=settings,
        embeddings=request.app.state.embeddings,
    )
    return RAGChatService(session, settings, search_service, llm=request.app.state.llm)


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
    try:
        answer, sources, session_id = await service.chat(
            question=request.question,
            session_id=request.session_id,
        )

        return ChatResponse(
            answer=answer,
            sources=[SourceInfo(**s) for s in sources],
            session_id=session_id,
        )
    except OpenAIError:
        logger.exception("OpenAI API error")
        raise HTTPException(status_code=502, detail="LLM service unavailable") from None
    except Exception:
        logger.exception("Chat failed")
        raise HTTPException(status_code=503, detail="Chat service unavailable") from None


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

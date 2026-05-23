"""Data access layer for chat sessions and messages."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.models import ChatMessage, ChatSession


class ChatSessionRepository:
    """Repository for chat session operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self) -> ChatSession:
        """Create a new chat session."""
        chat_session = ChatSession()
        self.session.add(chat_session)
        await self.session.flush()
        return chat_session

    async def get_by_id(self, session_id: UUID) -> ChatSession | None:
        """Get chat session by ID."""
        result = await self.session.execute(select(ChatSession).where(ChatSession.id == session_id))
        return result.scalar_one_or_none()


class ChatMessageRepository:
    """Repository for chat message operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        session_id: UUID,
        role: str,
        content: str,
        context_used: list | None = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            context_used=context_used or [],
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_by_session(self, session_id: UUID, limit: int = 50) -> list[ChatMessage]:
        """Get messages for a session, ordered by creation time."""
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

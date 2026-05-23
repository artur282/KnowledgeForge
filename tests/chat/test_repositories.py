"""Tests for chat repositories."""

import json

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.chat.repositories import ChatMessageRepository, ChatSessionRepository


@pytest.fixture
def session_repo(db_session: AsyncSession) -> ChatSessionRepository:
    return ChatSessionRepository(db_session)


@pytest.fixture
def message_repo(db_session: AsyncSession) -> ChatMessageRepository:
    return ChatMessageRepository(db_session)


async def test_create_session(session_repo: ChatSessionRepository, db_session: AsyncSession):
    session = await session_repo.create()
    await db_session.commit()
    assert session.id is not None
    assert session.created_at is not None


async def test_get_session_by_id(session_repo: ChatSessionRepository, db_session: AsyncSession):
    session = await session_repo.create()
    await db_session.commit()
    found = await session_repo.get_by_id(session.id)
    assert found is not None
    assert found.id == session.id


async def test_get_nonexistent_session(session_repo: ChatSessionRepository):
    from uuid import uuid4

    result = await session_repo.get_by_id(uuid4())
    assert result is None


async def test_create_message(
    message_repo: ChatMessageRepository, session_repo: ChatSessionRepository, db_session: AsyncSession
):
    session = await session_repo.create()
    await db_session.commit()

    msg = await message_repo.create(
        session_id=session.id,
        role="user",
        content="Hello, world!",
    )
    await db_session.commit()

    assert msg.role == "user"
    assert msg.content == "Hello, world!"
    assert json.loads(msg.context_used) == []


async def test_create_message_with_context(
    message_repo: ChatMessageRepository, session_repo: ChatSessionRepository, db_session: AsyncSession
):
    session = await session_repo.create()
    await db_session.commit()

    context = [{"doc_id": "123", "chunk_index": 0, "score": 0.9}]
    msg = await message_repo.create(
        session_id=session.id,
        role="assistant",
        content="Based on the documents...",
        context_used=context,
    )
    await db_session.commit()

    assert json.loads(msg.context_used) == context


async def test_get_messages_by_session(
    message_repo: ChatMessageRepository, session_repo: ChatSessionRepository, db_session: AsyncSession
):
    session = await session_repo.create()
    await db_session.commit()

    await message_repo.create(session_id=session.id, role="user", content="Q1")
    await message_repo.create(session_id=session.id, role="assistant", content="A1")
    await message_repo.create(session_id=session.id, role="user", content="Q2")
    await db_session.commit()

    messages = await message_repo.get_by_session(session.id)
    assert len(messages) == 3
    assert messages[0].content == "Q1"
    assert messages[1].content == "A1"
    assert messages[2].content == "Q2"

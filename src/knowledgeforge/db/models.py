from datetime import datetime, timezone
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    filename = Column(Text, nullable=False)
    content_hash = Column(Text, nullable=False, unique=True)
    status = Column(String(20), nullable=False, default="pending")
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename={self.filename} status={self.status}>"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (CheckConstraint("chunk_index >= 0", name="chk_chunk_index_positive"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    metadata_ = Column("metadata", JSONB, nullable=False, server_default="{}")

    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk id={self.id} doc={self.document_id} idx={self.chunk_index}>"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id}>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (CheckConstraint("role IN ('user', 'assistant')", name="chk_role_valid"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    context_used = Column("context_used", JSONB, nullable=False, server_default="[]")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} role={self.role} session={self.session_id}>"

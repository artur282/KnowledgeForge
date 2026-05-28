"""MCP tool factory for KnowledgeForge with dependency injection."""

import json
import logging
from collections.abc import Callable
from uuid import UUID

logger = logging.getLogger(__name__)


def create_mcp_tools(
    session_factory: Callable,
    es_client,
    settings,
    embeddings=None,
    llm=None,
) -> dict:
    """Create MCP tool functions with injected dependencies.

    Returns a dict of tool name -> async function.
    """

    async def search_knowledge(query: str, k: int = 10) -> str:
        """Search the knowledge base using hybrid search (BM25 + semantic).

        Args:
            query: The search query.
            k: Number of results to return (default 10, max 100).

        Returns:
            Formatted search results with document content and sources.
        """
        try:
            from knowledgeforge.search.services import HybridSearchService

            async with session_factory() as session:
                service = HybridSearchService(session, es_client, settings, embeddings=embeddings)
                results = await service.search(query=query, k=min(k, 100))

            if not results:
                return "No relevant documents found."

            formatted = []
            for r in results:
                formatted.append(f"[{r.filename}] (chunk {r.chunk_index}, score: {r.score:.4f})\n{r.content[:300]}")

            return "\n\n---\n\n".join(formatted)
        except Exception as e:
            return json.dumps({"error": str(e)})

    if llm is None:
        raise ValueError("llm parameter is required")

    async def summarize_document(doc_id: str) -> str:
        """Generate a summary of a specific document from the knowledge base.

        Args:
            doc_id: The UUID of the document to summarize.

        Returns:
            A concise summary of the document content.
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from sqlalchemy import select

            from knowledgeforge.db.models import DocumentChunk
            from knowledgeforge.ingestion.repositories import DocumentRepository

            async with session_factory() as session:
                doc_repo = DocumentRepository(session)
                doc = await doc_repo.get_by_id(UUID(doc_id))

                if not doc:
                    return f"Document {doc_id} not found."

                if doc.status != "ready":
                    return f"Document is not ready for summarization (status: {doc.status})."

                result = await session.execute(
                    select(DocumentChunk).where(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index)
                )
                chunks = result.scalars().all()

                if not chunks:
                    return "Document has no content chunks."

                full_content = "\n\n".join(c.content for c in chunks)
                max_tokens = 8000
                if len(full_content) > max_tokens * 4:
                    full_content = full_content[: max_tokens * 4] + "...[truncated]"

                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "Summarize the following document concisely. Focus on key facts and main points.",
                        ),
                        ("human", "Document: {content}"),
                    ]
                )

                chain = prompt | llm

                callbacks = []
                if settings.langfuse_public_key:
                    from langfuse.callback import CallbackHandler

                    callbacks.append(CallbackHandler())

                response = await chain.ainvoke(
                    {"content": full_content},
                    config={"callbacks": callbacks},
                )

                return response.content
        except Exception as e:
            return json.dumps({"error": str(e)})

    return {
        "search_knowledge": search_knowledge,
        "summarize_document": summarize_document,
    }

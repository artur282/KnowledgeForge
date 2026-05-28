"""Search repository for database operations."""

import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SearchRepository:
    """Handles all search-related database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def semantic_search(
        self,
        embedding: list[float],
        k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[dict]:
        """Search document_chunks by embedding similarity using pgvector."""
        filter_clause = ""
        params: dict = {"embedding": str(embedding), "k": k}

        if filters:
            for key, value in filters.items():
                if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                    continue
                filter_clause += f" AND dc.metadata->>'{key}' = :filter_{key}"
                params[f"filter_{key}"] = value

        sql = text(f"""
            SELECT dc.id::text,
                   dc.document_id::text,
                   dc.chunk_index,
                   dc.content,
                   dc.metadata,
                   1 - (dc.embedding <=> :embedding::vector) AS score
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE d.status = 'ready'{filter_clause}
            ORDER BY dc.embedding <=> :embedding::vector
            LIMIT :k
        """)

        result = await self.session.execute(sql, params)
        rows = result.fetchall()
        return [
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "chunk_index": row[2],
                "content": row[3],
                "metadata": row[4],
                "score": float(row[5]),
            }
            for row in rows
        ]

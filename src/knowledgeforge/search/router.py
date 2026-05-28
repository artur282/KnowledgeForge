"""HTTP endpoints for hybrid search."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.deps import get_session
from knowledgeforge.search.schemas import SearchRequest, SearchResponse, SuggestResponse
from knowledgeforge.search.services import HybridSearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


def get_search_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> HybridSearchService:
    """Dependency injection for HybridSearchService."""
    return HybridSearchService(
        session,
        request.app.state.es_client,
        settings=request.app.state.settings,
        embeddings=request.app.state.embeddings,
    )


@router.post(
    "",
    response_model=SearchResponse,
    operation_id="hybridSearch",
)
async def hybrid_search(
    request: SearchRequest,
    service: HybridSearchService = Depends(get_search_service),
):
    """Execute hybrid search with BM25 + semantic fusion."""
    try:
        results = await service.search(
            query=request.query,
            k=request.k,
            filters=request.filters,
        )
        return SearchResponse(results=results, total=len(results))
    except Exception:
        logger.exception("Search failed")
        raise HTTPException(status_code=503, detail="Search service unavailable") from None


@router.get(
    "/suggest",
    response_model=SuggestResponse,
    operation_id="searchSuggestions",
)
async def search_suggestions(
    q: str = Query(..., min_length=1, max_length=100),
    service: HybridSearchService = Depends(get_search_service),
):
    """Get autocomplete suggestions from Elasticsearch."""
    suggestions = await service._get_suggestions(q)
    return SuggestResponse(suggestions=suggestions)

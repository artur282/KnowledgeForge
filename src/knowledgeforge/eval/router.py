"""HTTP endpoints for RAGAS evaluation."""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.eval.repositories import EvalReportRepository
from knowledgeforge.eval.schemas import (
    EvalReportItem,
    EvalReportsResponse,
    EvalRunRequest,
    EvalRunResponse,
)
from knowledgeforge.eval.services import RAGASEvalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/eval", tags=["evaluation"])


async def get_session(request: Request) -> AsyncSession:
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def get_eval_service(
    session: AsyncSession = Depends(get_session),
) -> RAGASEvalService:
    from knowledgeforge.config import Settings

    settings = Settings()
    eval_repo = EvalReportRepository(session)
    return RAGASEvalService(settings, eval_repo)


@router.post(
    "/run",
    response_model=EvalRunResponse,
    operation_id="runEvaluation",
)
async def run_evaluation(
    request: EvalRunRequest = EvalRunRequest(),
    service: RAGASEvalService = Depends(get_eval_service),
):
    result = await service.run_evaluation(
        name=request.name,
        dataset_path=request.dataset_path,
    )
    return EvalRunResponse(**result)


@router.get(
    "/reports",
    response_model=EvalReportsResponse,
    operation_id="listEvalReports",
)
async def list_eval_reports(
    session: AsyncSession = Depends(get_session),
):
    eval_repo = EvalReportRepository(session)
    reports = await eval_repo.get_all()
    return EvalReportsResponse(reports=[EvalReportItem.model_validate(r) for r in reports])

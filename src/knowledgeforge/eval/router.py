"""HTTP endpoints for RAGAS evaluation."""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.deps import get_session, get_settings
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


def get_eval_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
    settings=Depends(get_settings),
) -> RAGASEvalService:
    eval_repo = EvalReportRepository(session)
    return RAGASEvalService(
        settings,
        eval_repo,
        session_factory=request.app.state.session_factory,
        es_client=request.app.state.es_client,
        embeddings=request.app.state.embeddings,
        llm=request.app.state.llm,
    )


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

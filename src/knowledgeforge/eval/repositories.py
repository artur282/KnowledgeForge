"""Data access layer for evaluation reports."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.models import EvalReport


class EvalReportRepository:
    """Repository for evaluation report operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        name: str,
        faithfulness: float | None = None,
        answer_relevancy: float | None = None,
        context_precision: float | None = None,
        context_recall: float | None = None,
        results_json: dict | None = None,
    ) -> EvalReport:
        """Create a new evaluation report."""
        report = EvalReport(
            name=name,
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            context_precision=context_precision,
            context_recall=context_recall,
            results_json=results_json or {},
        )
        self.session.add(report)
        await self.session.flush()
        return report

    async def get_all(self, limit: int = 50) -> list[EvalReport]:
        """Get all evaluation reports, ordered by creation time."""
        result = await self.session.execute(select(EvalReport).order_by(EvalReport.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, report_id: UUID) -> EvalReport | None:
        """Get evaluation report by ID."""
        result = await self.session.execute(select(EvalReport).where(EvalReport.id == report_id))
        return result.scalar_one_or_none()

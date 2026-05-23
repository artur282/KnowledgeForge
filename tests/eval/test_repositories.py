"""Tests for evaluation repositories."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.eval.repositories import EvalReportRepository


@pytest.fixture
def eval_repo(db_session: AsyncSession) -> EvalReportRepository:
    return EvalReportRepository(db_session)


async def test_create_report(eval_repo: EvalReportRepository, db_session: AsyncSession):
    report = await eval_repo.create(
        name="test_run",
        faithfulness=0.92,
        answer_relevancy=0.88,
        context_precision=0.85,
    )
    await db_session.commit()

    assert report.name == "test_run"
    assert report.faithfulness == 0.92
    assert report.id is not None


async def test_get_all_reports(eval_repo: EvalReportRepository, db_session: AsyncSession):
    await eval_repo.create(name="run1", faithfulness=0.9)
    await eval_repo.create(name="run2", faithfulness=0.85)
    await db_session.commit()

    reports = await eval_repo.get_all()
    assert len(reports) == 2
    assert reports[0].name == "run2"


async def test_get_report_by_id(eval_repo: EvalReportRepository, db_session: AsyncSession):
    report = await eval_repo.create(name="test", faithfulness=0.9)
    await db_session.commit()

    found = await eval_repo.get_by_id(report.id)
    assert found is not None
    assert found.id == report.id


async def test_get_nonexistent_report(eval_repo: EvalReportRepository):
    from uuid import uuid4

    result = await eval_repo.get_by_id(uuid4())
    assert result is None

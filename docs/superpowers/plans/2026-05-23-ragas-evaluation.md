# Sub-proyecto 6: Evaluación RAGAS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar evaluación del pipeline RAG con RAGAS, ejecutando métricas de faithfulness, answer relevancy y context precision sobre un dataset curado de Q&A.

**Architecture:** Servicio de evaluación que construye un dataset RAGAS, ejecuta el pipeline RAG sobre preguntas del dataset, calcula métricas, y persiste los resultados. Router expone `POST /eval/run` para ejecutar evaluación y `GET /eval/reports` para listar reportes históricos.

**Tech Stack:** FastAPI, RAGAS, datasets, SQLAlchemy async, pandas (para export CSV), LangChain

---

## Estructura de Archivos

| Archivo | Responsabilidad |
|---------|----------------|
| `src/knowledgeforge/eval/schemas.py` | Pydantic schemas para eval request/response |
| `src/knowledgeforge/eval/services.py` | Servicio de evaluación RAGAS |
| `src/knowledgeforge/eval/repositories.py` | CRUD para reportes de evaluación |
| `src/knowledgeforge/eval/models.py` | Modelo SQLAlchemy para EvalReport |
| `src/knowledgeforge/eval/router.py` | Endpoints HTTP: POST /eval/run, GET /eval/reports |
| `src/knowledgeforge/eval/__init__.py` | Package export |
| `tests/eval/__init__.py` | Package marker |
| `tests/eval/test_services.py` | Tests de evaluación |
| `tests/eval/test_router.py` | Tests de endpoints |
| `src/knowledgeforge/main.py` | Registrar eval router |
| `src/knowledgeforge/db/models.py` | Agregar EvalReport model |

---

### Task 1: Modelo EvalReport

**Files:**
- Modify: `src/knowledgeforge/db/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Agregar modelo EvalReport**

Agregar a `src/knowledgeforge/db/models.py`:

```python
# Agregar imports necesarios
from datetime import UTC, datetime

class EvalReport(Base):
    __tablename__ = "eval_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    name = Column(Text, nullable=False)
    faithfulness = Column(Float, nullable=True)
    answer_relevancy = Column(Float, nullable=True)
    context_precision = Column(Float, nullable=True)
    context_recall = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    results_json = Column("results_json", JSONB, nullable=False, server_default="{}")

    def __repr__(self) -> str:
        return f"<EvalReport id={self.id} name={self.name}>"
```

- [ ] **Step 2: Actualizar test de modelos**

Agregar a `tests/test_models.py`:

```python
def test_eval_report_table_name():
    """EvalReport model maps to eval_reports table."""
    from knowledgeforge.db.models import EvalReport
    assert EvalReport.__tablename__ == "eval_reports"
```

- [ ] **Step 3: Commit**

```bash
git add src/knowledgeforge/db/models.py tests/test_models.py
git commit -m "feat(eval): add EvalReport model for storing evaluation results"
```

---

### Task 2: Repositories de Evaluación

**Files:**
- Create: `src/knowledgeforge/eval/repositories.py`
- Test: `tests/eval/test_repositories.py`

- [ ] **Step 1: Crear repository de evaluación**

```python
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
        result = await self.session.execute(
            select(EvalReport).order_by(EvalReport.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, report_id: UUID) -> EvalReport | None:
        """Get evaluation report by ID."""
        result = await self.session.execute(
            select(EvalReport).where(EvalReport.id == report_id)
        )
        return result.scalar_one_or_none()
```

- [ ] **Step 2: Escribir tests para repository**

```python
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
    assert reports[0].name == "run2"  # Most recent first


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
```

- [ ] **Step 3: Commit**

```bash
git add src/knowledgeforge/eval/repositories.py tests/eval/test_repositories.py
git commit -m "feat(eval): add repository for evaluation report CRUD"
```

---

### Task 3: Schemas de Evaluación

**Files:**
- Create: `src/knowledgeforge/eval/schemas.py`

- [ ] **Step 1: Crear schemas de evaluación**

```python
"""Pydantic schemas for evaluation endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EvalRunRequest(BaseModel):
    """Request schema for running evaluation."""

    name: str = Field(default="auto_eval", min_length=1, max_length=100)
    dataset_path: str | None = Field(
        default=None,
        description="Optional path to custom evaluation dataset JSON file",
    )


class EvalMetricResult(BaseModel):
    """Single metric result."""

    name: str
    score: float


class EvalRunResponse(BaseModel):
    """Response schema for evaluation run."""

    report_id: UUID
    name: str
    faithfulness: float | None
    answer_relevancy: float | None
    context_precision: float | None
    context_recall: float | None
    created_at: datetime


class EvalReportItem(BaseModel):
    """Single report in list response."""

    id: UUID
    name: str
    faithfulness: float | None
    answer_relevancy: float | None
    context_precision: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvalReportsResponse(BaseModel):
    """Response schema for listing evaluation reports."""

    reports: list[EvalReportItem]
```

- [ ] **Step 2: Commit**

```bash
git add src/knowledgeforge/eval/schemas.py
git commit -m "feat(eval): add Pydantic schemas for evaluation endpoints"
```

---

### Task 4: Servicio de Evaluación RAGAS

**Files:**
- Create: `src/knowledgeforge/eval/services.py`
- Test: `tests/eval/test_services.py`

- [ ] **Step 1: Crear servicio de evaluación**

```python
"""RAGAS evaluation service."""

import logging
from datetime import UTC, datetime
from pathlib import Path

from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_precision, faithfulness
from ragas.metrics._context_recall import context_recall

from knowledgeforge.config import Settings
from knowledgeforge.eval.repositories import EvalReportRepository

logger = logging.getLogger(__name__)

DEFAULT_EVAL_DATASET = [
    {
        "question": "¿Cuál es la política de devoluciones?",
        "answer": "",  # Will be filled by RAG pipeline
        "contexts": [],  # Will be filled by RAG pipeline
        "ground_truth": "La política de devoluciones permite devolver productos dentro de los 30 días.",
    },
]


class RAGASEvalService:
    """Executes RAGAS evaluation on the RAG pipeline."""

    def __init__(
        self,
        settings: Settings,
        eval_repo: EvalReportRepository,
    ) -> None:
        self.settings = settings
        self.eval_repo = eval_repo
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            openai_api_key=settings.openai_api_key,
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key,
        )

    async def run_evaluation(self, name: str, dataset_path: str | None = None) -> dict:
        """Run RAGAS evaluation.

        1. Load or create evaluation dataset
        2. Execute RAG pipeline to fill answers and contexts
        3. Run RAGAS metrics
        4. Save report
        5. Export to CSV
        """
        # Load dataset
        if dataset_path:
            import json
            data = json.loads(Path(dataset_path).read_text())
            eval_dataset = Dataset.from_list(data)
        else:
            eval_dataset = Dataset.from_list(DEFAULT_EVAL_DATASET)

        # Fill in answers and contexts using RAG pipeline
        filled_data = await self._fill_dataset(eval_dataset)

        # Run RAGAS evaluation
        result = evaluate(
            dataset=filled_data,
            metrics=[faithfulness, answer_relevancy, context_precision],
            llm=self.llm,
            embeddings=self.embeddings,
        )

        # Extract scores
        scores = {
            "faithfulness": result.get("faithfulness"),
            "answer_relevancy": result.get("answer_relevancy"),
            "context_precision": result.get("context_precision"),
        }

        # Save report
        report = await self.eval_repo.create(
            name=name,
            faithfulness=scores["faithfulness"],
            answer_relevancy=scores["answer_relevancy"],
            context_precision=scores["context_precision"],
            results_json={k: v for k, v in scores.items() if v is not None},
        )

        # Export to CSV
        self._export_to_csv(result)

        logger.info(
            "Evaluation '%s' complete: faithfulness=%.2f, answer_relevancy=%.2f, context_precision=%.2f",
            name,
            scores.get("faithfulness", 0),
            scores.get("answer_relevancy", 0),
            scores.get("context_precision", 0),
        )

        return {
            "report_id": report.id,
            "name": name,
            **scores,
            "created_at": report.created_at,
        }

    async def _fill_dataset(self, dataset: Dataset) -> Dataset:
        """Fill dataset with RAG answers and contexts.

        For each question in the dataset, execute the RAG pipeline
        to get the answer and retrieved contexts.
        """
        from knowledgeforge.main import app
        from knowledgeforge.db.engine import get_async_session
        from knowledgeforge.search.services import HybridSearchService
        from knowledgeforge.chat.services import RAGChatService

        filled_rows = []
        for row in dataset:
            question = row["question"]

            # Get RAG answer and contexts
            session_factory = app.state.session_factory
            async with session_factory() as session:
                search_service = HybridSearchService(session, app.state.es_client)
                rag_service = RAGChatService(session, self.settings, search_service)

                answer, sources, _ = await rag_service.chat(question=question)

                # Extract context content from sources
                contexts = [f"[{s.get('filename', 'unknown')}] chunk {s['chunk_index']}" for s in sources]

                filled_rows.append({
                    "question": question,
                    "answer": answer,
                    "contexts": contexts if contexts else ["No context retrieved"],
                    "ground_truth": row.get("ground_truth", ""),
                })

        return Dataset.from_list(filled_rows)

    def _export_to_csv(self, result) -> None:
        """Export evaluation results to CSV."""
        import pandas as pd

        df = result.to_pandas()
        output_path = Path("docs") / "eval_report.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info("Evaluation report exported to %s", output_path)
```

- [ ] **Step 2: Escribir tests para servicio**

```python
"""Tests for RAGAS evaluation service."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from knowledgeforge.eval.services import RAGASEvalService


@pytest.fixture
def mock_settings():
    from knowledgeforge.config import Settings
    return Settings(
        database_url="sqlite+aiosqlite:///test.db",
        elasticsearch_url="http://localhost:9200",
        openai_api_key="sk-test-key",
    )


@pytest.fixture
def mock_eval_repo():
    repo = AsyncMock()
    repo.create.return_value = MagicMock(
        id=uuid4(),
        created_at="2026-05-23T00:00:00Z",
    )
    return repo


@patch("knowledgeforge.eval.services.ChatOpenAI")
@patch("knowledgeforge.eval.services.OpenAIEmbeddings")
def test_service_initialization(mock_embeddings, mock_llm, mock_settings, mock_eval_repo):
    """RAGASEvalService initializes with all components."""
    service = RAGASEvalService(mock_settings, mock_eval_repo)
    assert service.llm is not None
    assert service.embeddings is not None
```

- [ ] **Step 3: Commit**

```bash
git add src/knowledgeforge/eval/services.py tests/eval/test_services.py
git commit -m "feat(eval): add RAGAS evaluation service with metric computation"
```

---

### Task 5: Router de Evaluación

**Files:**
- Create: `src/knowledgeforge/eval/router.py`
- Create: `src/knowledgeforge/eval/__init__.py`
- Modify: `src/knowledgeforge/main.py`
- Test: `tests/eval/test_router.py`

- [ ] **Step 1: Crear router de evaluación**

```python
"""HTTP endpoints for RAGAS evaluation."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.db.engine import get_async_session
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
    session: AsyncSession = Depends(get_async_session),
) -> RAGASEvalService:
    """Dependency injection for RAGASEvalService."""
    from knowledgeforge.config import Settings
    from knowledgeforge.eval.repositories import EvalReportRepository

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
    """Execute RAGAS evaluation on the RAG pipeline."""
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
    session: AsyncSession = Depends(get_async_session),
):
    """List historical evaluation reports."""
    eval_repo = EvalReportRepository(session)
    reports = await eval_repo.get_all()
    return EvalReportsResponse(
        reports=[EvalReportItem.model_validate(r) for r in reports]
    )
```

- [ ] **Step 2: Actualizar eval/__init__.py**

```python
"""RAGAS evaluation module."""

from knowledgeforge.eval.router import router

__all__ = ["router"]
```

- [ ] **Step 3: Registrar router en main.py**

Agregar a `src/knowledgeforge/main.py`:

```python
from knowledgeforge.eval import router as eval_router

# En create_app():
app.include_router(eval_router)
```

- [ ] **Step 4: Escribir tests para router**

```python
"""Tests for evaluation endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


@patch("knowledgeforge.eval.router.RAGASEvalService")
async def test_run_evaluation(mock_service, client: AsyncClient):
    """POST /eval/run executes evaluation and returns scores."""
    mock_instance = AsyncMock()
    mock_instance.run_evaluation.return_value = {
        "report_id": uuid4(),
        "name": "test_run",
        "faithfulness": 0.92,
        "answer_relevancy": 0.88,
        "context_precision": 0.85,
        "created_at": "2026-05-23T00:00:00Z",
    }
    mock_service.return_value = mock_instance

    response = await client.post("/eval/run", json={"name": "test_run"})
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "faithfulness" in data
    assert "answer_relevancy" in data
    assert "context_precision" in data


async def test_list_eval_reports_empty(client: AsyncClient):
    """GET /eval/reports returns empty list when no reports exist."""
    response = await client.get("/eval/reports")
    assert response.status_code == 200
    data = response.json()
    assert "reports" in data
    assert isinstance(data["reports"], list)
```

- [ ] **Step 5: Commit**

```bash
git add src/knowledgeforge/eval/__init__.py src/knowledgeforge/eval/router.py tests/eval/test_router.py src/knowledgeforge/main.py
git commit -m "feat(eval): add HTTP endpoints for RAGAS evaluation and report listing"
```

---

### Task 6: Verificación Final

- [ ] **Step 1: Ejecutar tests**

```bash
uv run pytest tests/ -v
```

Esperado: Todos los tests pasan

- [ ] **Step 2: Ejecutar linting**

```bash
uv run ruff check src/ tests/
```

Esperado: 0 issues

- [ ] **Step 3: Verificar OpenAPI actualizado**

```bash
uv run knowledgeforge &
curl http://localhost:8000/openapi.json | python -m json.tool > docs/openapi.json
```

- [ ] **Step 4: Commit final si hay cambios**

```bash
git add -A
git commit -m "chore: final verification for RAGAS evaluation sub-project"
```
"""RAGAS evaluation service."""

import asyncio
import logging
from pathlib import Path

from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import evaluate
from ragas.metrics.collections import answer_relevancy, context_precision, faithfulness

from knowledgeforge.config import Settings
from knowledgeforge.eval.repositories import EvalReportRepository

logger = logging.getLogger(__name__)

DEFAULT_EVAL_DATASET = [
    {
        "question": "¿Cuál es la política de devoluciones?",
        "answer": "",
        "contexts": [],
        "ground_truth": "La política de devoluciones permite devolver productos dentro de los 30 días.",
    },
]


class RAGASEvalService:
    """Executes RAGAS evaluation on the RAG pipeline."""

    def __init__(
        self,
        settings: Settings,
        eval_repo: EvalReportRepository,
        session_factory=None,
        es_client=None,
        embeddings: OpenAIEmbeddings | None = None,
        llm: ChatOpenAI | None = None,
    ) -> None:
        self.settings = settings
        self.eval_repo = eval_repo
        self.session_factory = session_factory
        self.es_client = es_client
        self.llm = llm or ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        self.embeddings = embeddings or OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def run_evaluation(self, name: str, dataset_path: str | None = None) -> dict:
        """Run RAGAS evaluation.

        1. Load or create evaluation dataset
        2. Execute RAG pipeline to fill answers and contexts
        3. Run RAGAS metrics
        4. Save report
        5. Export to CSV
        """
        if dataset_path:
            import json

            data = await asyncio.to_thread(Path(dataset_path).read_text)
            data = json.loads(data)
            eval_dataset = Dataset.from_list(data)
        else:
            eval_dataset = Dataset.from_list(DEFAULT_EVAL_DATASET)

        filled_data = await self._fill_dataset(eval_dataset)

        result = await asyncio.to_thread(
            evaluate,
            dataset=filled_data,
            metrics=[faithfulness, answer_relevancy, context_precision],
            llm=self.llm,
            embeddings=self.embeddings,
        )

        scores = {
            "faithfulness": result.get("faithfulness"),
            "answer_relevancy": result.get("answer_relevancy"),
            "context_precision": result.get("context_precision"),
        }

        report = await self.eval_repo.create(
            name=name,
            faithfulness=scores["faithfulness"],
            answer_relevancy=scores["answer_relevancy"],
            context_precision=scores["context_precision"],
            results_json={k: v for k, v in scores.items() if v is not None},
        )

        await self._export_to_csv(result)

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
        from knowledgeforge.chat.services import RAGChatService
        from knowledgeforge.search.services import HybridSearchService

        filled_rows = []
        for row in dataset:
            question = row["question"]

            async with self.session_factory() as session:
                search_service = HybridSearchService(session, self.es_client, self.settings)
                rag_service = RAGChatService(session, self.settings, search_service)

                answer, sources, _ = await rag_service.chat(question=question)

                contexts = [f"[{s.get('filename', 'unknown')}] chunk {s['chunk_index']}" for s in sources]

                filled_rows.append(
                    {
                        "question": question,
                        "answer": answer,
                        "contexts": contexts if contexts else ["No context retrieved"],
                        "ground_truth": row.get("ground_truth", ""),
                    }
                )

        return Dataset.from_list(filled_rows)

    async def _export_to_csv(self, result) -> None:
        """Export evaluation results to CSV."""

        df = result.to_pandas()
        output_path = Path("docs") / "eval_report.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(df.to_csv, output_path, index=False)
        logger.info("Evaluation report exported to %s", output_path)

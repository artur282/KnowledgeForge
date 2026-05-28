"""RAG chat service with LCEL chain and Langfuse tracing."""

import logging
from uuid import UUID

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from knowledgeforge.chat.repositories import ChatMessageRepository, ChatSessionRepository
from knowledgeforge.config import Settings
from knowledgeforge.search.services import HybridSearchService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a knowledgeable assistant that answers questions based on the provided context.

Answer the question using ONLY the information from the context below.
If the context doesn't contain enough information to answer, say so clearly.

Always cite your sources by mentioning the document filename when referencing information.

Context:
{context}

Question: {question}

Answer:"""


class RAGChatService:
    """RAG chat service with LCEL chain."""

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        search_service: HybridSearchService,
        llm: ChatOpenAI | None = None,
    ) -> None:
        self.session = session
        self.settings = settings
        self.search_service = search_service
        self.session_repo = ChatSessionRepository(session)
        self.message_repo = ChatMessageRepository(session)

        self.llm = llm or ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=0,
        )

        self._last_results: list = []

        self.callbacks = []
        if settings.langfuse_public_key:
            from langfuse.callback import CallbackHandler

            self.callbacks.append(CallbackHandler())

        self.chain = (
            {
                "context": RunnableLambda(self._retrieve_and_format),
                "question": RunnablePassthrough(),
            }
            | ChatPromptTemplate.from_messages(
                [
                    ("system", SYSTEM_PROMPT),
                    ("human", "{question}"),
                ]
            )
            | self.llm
        )

    async def _retrieve_and_format(self, question: str) -> str:
        """Retrieve chunks, store results, and format as context string."""
        results = await self.search_service.search(query=question, k=5)
        self._last_results = results
        context_parts = [f"[Document: {r.filename}] (chunk {r.chunk_index})\n{r.content}" for r in results]
        return "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

    async def chat(self, question: str, session_id: UUID | None = None) -> tuple[str, list[dict], UUID]:
        """Execute RAG chat.

        1. Get or create session
        2. Save user message
        3. Execute RAG chain with Langfuse tracing
        4. Save assistant message with context
        5. Return answer, sources, and session_id
        """
        if session_id:
            chat_session = await self.session_repo.get_by_id(session_id)
            if not chat_session:
                chat_session = await self.session_repo.create()
        else:
            chat_session = await self.session_repo.create()

        await self.message_repo.create(
            session_id=chat_session.id,
            role="user",
            content=question,
        )

        self._last_results = []
        response = await self.chain.ainvoke(
            question,
            config={"callbacks": self.callbacks},
        )

        answer = response.content if hasattr(response, "content") else str(response)

        sources = [{"doc_id": r.doc_id, "chunk_index": r.chunk_index, "score": r.score} for r in self._last_results]

        await self.message_repo.create(
            session_id=chat_session.id,
            role="assistant",
            content=answer,
            context_used=sources,
        )

        return answer, sources, chat_session.id

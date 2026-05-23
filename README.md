# KnowledgeForge

Enterprise knowledge management platform with AI-powered RAG.

## Quick Start

```bash
# 1. Copy environment variables
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 2. Start all services
docker compose up -d

# 3. Run migrations
docker compose exec app uv run alembic upgrade head

# 4. Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Langfuse: http://localhost:3000
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Start dev server
uv run knowledgeforge
```

## Architecture

- **FastAPI** — Async web framework
- **SQLAlchemy + pgvector** — Database with vector embeddings
- **Elasticsearch** — Full-text search with BM25
- **LangChain** — RAG pipeline
- **Langfuse** — LLM observability
- **MCP** — Model Context Protocol server
- **RAGAS** — RAG evaluation metrics

## Project Structure

```
src/knowledgeforge/
├── config.py       # Settings
├── main.py         # FastAPI app
├── db/             # Database layer
├── ingestion/      # Document ingestion
├── search/         # Hybrid search
├── chat/           # RAG chat
├── mcp/            # MCP server
└── eval/           # Evaluation
```

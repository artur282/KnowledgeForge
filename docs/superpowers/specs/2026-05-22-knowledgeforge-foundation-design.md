# KnowledgeForge — Fundación: Diseño de Arquitectura

> **Sub-proyecto 1 de 6** — Base sobre la cual se construyen Ingesta, Búsqueda, RAG, MCP y Evaluación.

## Visión

Crear la infraestructura base del proyecto: estructura de directorios, configuración, base de datos, Docker Compose con todos los servicios, y el esqueleto de la aplicación FastAPI.

## Decisiones de Arquitectura

| Decisión | Elección | Justificación |
|----------|----------|---------------|
| Layout | `src/` | Paquete aislado, imports limpios, estándar Python moderno |
| Python | 3.12+ | Mejor rendimiento, excepciones con grupo, f-strings mejorados |
| Gestor | `uv` | Resolución ultra-rápida, compatible con pyproject.toml |
| Patrón | Monolito modular | Simple, un solo `uv run`, imports directos |
| Deploy | Docker Compose | Todo corre con un solo `docker compose up` |

## Estructura del Proyecto

```
KnowledgeForge/
├── src/
│   └── knowledgeforge/
│       ├── __init__.py
│       ├── __main__.py             # python -m knowledgeforge
│       ├── config.py               # pydantic-settings
│       ├── main.py                 # FastAPI app + lifespan
│       ├── db/
│       │   ├── __init__.py
│       │   ├── engine.py           # Async engine + get_session
│       │   └── models.py           # SQLAlchemy declarative models
│       ├── ingestion/              # Placeholder (sub-proyecto 2)
│       │   └── __init__.py
│       ├── search/                 # Placeholder (sub-proyecto 3)
│       │   └── __init__.py
│       ├── chat/                   # Placeholder (sub-proyecto 4)
│       │   └── __init__.py
│       ├── mcp/                    # Placeholder (sub-proyecto 5)
│       │   └── __init__.py
│       └── eval/                   # Placeholder (sub-proyecto 6)
│           └── __init__.py
├── tests/
│   ├── conftest.py                 # Fixtures compartidos
│   └── test_health.py              # Test de smoke
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── docs/
    └── openapi.yaml                # Contrato API (Definition of Done)
```

## Docker Compose

Todos los servicios en un solo `docker compose up`:

| Servicio | Imagen | Puerto | Propósito |
|----------|--------|--------|-----------|
| `postgres` | `pgvector/pgvector:pg16` | 5432 | Base de datos principal con pgvector |
| `elasticsearch` | `elasticsearch:8.15.0` | 9200 | Búsqueda BM25 + suggest |
| `langfuse` | `ghcr.io/langfuse/langfuse:latest` | 3000 | Observabilidad LLM |
| `langfuse-db` | `postgres:16` | — | DB dedicada para Langfuse |
| `app` | Build local | 8000 | FastAPI con hot-reload |

La app se construye desde el `Dockerfile` con volumen bind-mount para hot-reload en desarrollo.

## Configuración

`pydantic-settings` lee variables de entorno desde `.env`:

```python
class Settings(BaseSettings):
    database_url: str
    elasticsearch_url: str
    openai_api_key: str
    langfuse_host: str
    langfuse_public_key: str
    langfuse_secret_key: str
```

## Modelos SQLAlchemy

### Document
- `id` UUID PK
- `filename` str NOT NULL
- `content_hash` str UNIQUE (deduplicación)
- `status` str DEFAULT 'pending'
- `uploaded_at` datetime DEFAULT now()

### DocumentChunk
- `id` UUID PK
- `document_id` UUID FK → documents ON DELETE CASCADE
- `chunk_index` int NOT NULL
- `content` str NOT NULL
- `embedding` vector(1536) pgvector
- `metadata` JSONB DEFAULT '{}'

### ChatSession
- `id` UUID PK
- `created_at` datetime DEFAULT now()

### ChatMessage
- `id` UUID PK
- `session_id` UUID FK → chat_sessions ON DELETE CASCADE
- `role` str CHECK IN ('user', 'assistant')
- `content` str NOT NULL
- `context_used` JSONB DEFAULT '[]'
- `created_at` datetime DEFAULT now()

## FastAPI App

- `lifespan` context manager inicializa conexiones a PG y ES
- Health endpoint en `GET /health`
- Routers registrados por dominio (placeholders por ahora)
- CORS habilitado para desarrollo

## Testing

- pytest como framework
- `conftest.py` con fixtures para app, db session
- Test de smoke: `GET /health` retorna 200

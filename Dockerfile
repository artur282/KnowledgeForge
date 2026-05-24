FROM python:3.12-slim AS base

WORKDIR /app
RUN pip install --no-cache-dir uv

# Install all dependencies (prod + dev) for testing
FROM base AS dev-deps
COPY pyproject.toml ./
COPY src/ ./src/
RUN uv sync --group dev

# Production stage - minimal
FROM base AS production
COPY pyproject.toml ./
COPY src/ ./src/
RUN uv sync --no-dev
COPY alembic/ ./alembic/
COPY alembic.ini ./

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "knowledgeforge.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage - with hot reload
FROM base AS development
COPY pyproject.toml ./
COPY src/ ./src/
RUN uv sync --group dev
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY tests/ ./tests/

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "knowledgeforge.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Test stage - runs pytest
FROM base AS test
COPY pyproject.toml ./
COPY src/ ./src/
RUN uv sync --group dev
COPY tests/ ./tests/

CMD ["uv", "run", "pytest", "tests/", "-v"]

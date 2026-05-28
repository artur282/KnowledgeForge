FROM python:3.12-slim AS base

WORKDIR /app
RUN pip install --no-cache-dir uv

# Install all dependencies (prod + dev) for testing
FROM base AS dev-deps
COPY pyproject.toml uv.lock ./
RUN uv sync --group dev
COPY src/ ./src/

# Production stage - minimal
FROM base AS production
RUN addgroup --gid 1001 appgroup && adduser --uid 1001 --ingroup appgroup --disabled-password --gecos "" appuser
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN chown -R appuser:appgroup /app
COPY --chown=appuser:appgroup pyproject.toml uv.lock ./
USER appuser
RUN uv sync --no-dev
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini ./
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "knowledgeforge.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage - with hot reload
FROM base AS development
RUN addgroup --gid 1001 appgroup && adduser --uid 1001 --ingroup appgroup --disabled-password --gecos "" appuser
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN chown -R appuser:appgroup /app
COPY --chown=appuser:appgroup pyproject.toml uv.lock ./
USER appuser
RUN uv sync --group dev
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini ./
COPY --chown=appuser:appgroup tests/ ./tests/
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "knowledgeforge.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Test stage - runs pytest
FROM base AS test
COPY pyproject.toml uv.lock ./
RUN uv sync --group dev
COPY src/ ./src/
COPY tests/ ./tests/

CMD ["uv", "run", "pytest", "tests/", "-v"]

#!/bin/sh
set -e

echo "Enabling pgvector extension..."
/app/.venv/bin/python -c "
import asyncio, asyncpg, os
async def main():
    url = os.environ['DATABASE_URL'].replace('+asyncpg', '')
    conn = await asyncpg.connect(url)
    await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
    await conn.close()
    print('pgvector extension enabled')
asyncio.run(main())
" || echo "pgvector extension already exists or skipped"

echo "Running database migrations..."
/app/.venv/bin/python -m alembic upgrade head

echo "Starting application..."
exec /app/.venv/bin/python -m uvicorn knowledgeforge.main:app --host 0.0.0.0 --port 8000

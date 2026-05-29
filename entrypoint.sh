#!/bin/sh
set -e

echo "Enabling pgvector extension..."
/app/.venv/bin/python -c "
import asyncio, asyncpg, os, sys

async def main():
    url = os.environ.get('DATABASE_URL', '').replace('+asyncpg', '')
    if not url:
        print('ERROR: DATABASE_URL not set', file=sys.stderr)
        sys.exit(1)
    try:
        conn = await asyncpg.connect(url)
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        await conn.close()
        print('pgvector extension enabled')
    except Exception as e:
        print(f'WARNING: pgvector extension creation failed: {e}', file=sys.stderr)
        print('Extension may already exist or will be created by migrations')

asyncio.run(main())
"

echo "Running database migrations..."
/app/.venv/bin/python -m alembic upgrade head

echo "Starting application..."
exec /app/.venv/bin/python -m uvicorn knowledgeforge.main:app --host 0.0.0.0 --port 8000

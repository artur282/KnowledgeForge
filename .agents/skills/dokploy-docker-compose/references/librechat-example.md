# LibreChat Deployment on Dokploy

## Architecture Overview

LibreChat is a multi-service stack:
- `api` (LibreChat Node.js backend) — main app, port 3080
- `mongodb` — database
- `meilisearch` — search engine
- `vectordb` (pgvector/postgresql) — for RAG features
- `rag_api` (Python) — retrieval-augmented generation

## Complete docker-compose.yml for Dokploy

```yaml
services:
  api:
    image: ghcr.io/danny-avila/librechat-dev:v0.8.4
    restart: always
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      mongodb:
        condition: service_healthy
      rag_api:
        condition: service_started
    env_file:
      - .env        # loads all vars from Dokploy's Environment tab
    environment:
      - HOST=0.0.0.0
      - NODE_ENV=production
      - MONGO_URI=mongodb://${MONGO_USER}:${MONGO_PASS}@mongodb:27017/LibreChat?authSource=admin
      - MEILI_HOST=http://meilisearch:7700
      - RAG_PORT=${RAG_PORT:-8000}
      - RAG_API_URL=http://rag_api:${RAG_PORT:-8000}
    volumes:
      - librechat-images:/app/client/public/images
      - librechat-uploads:/app/uploads
      - librechat-logs:/app/logs
    networks:
      - librechat-net

  mongodb:
    image: mongo:8.0.17
    restart: always
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_USER}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASS}
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    volumes:
      - mongodb-data:/data/db
    networks:
      - librechat-net

  meilisearch:
    image: getmeili/meilisearch:v1.35.1
    restart: always
    environment:
      - MEILI_HOST=http://meilisearch:7700
      - MEILI_NO_ANALYTICS=true
      - MEILI_MASTER_KEY=${MEILI_MASTER_KEY}
    volumes:
      - meilisearch-data:/meili_data
    networks:
      - librechat-net

  vectordb:
    image: pgvector/pgvector:0.8.0-pg15-trixie
    restart: always
    environment:
      POSTGRES_DB: ${VECTORDB_DB:-mydatabase}
      POSTGRES_USER: ${VECTORDB_USER}
      POSTGRES_PASSWORD: ${VECTORDB_PASS}
    volumes:
      - vectordb-data:/var/lib/postgresql/data
    networks:
      - librechat-net

  rag_api:
    image: ghcr.io/danny-avila/librechat-rag-api-dev-lite:v0.7.3
    restart: always
    depends_on:
      - vectordb
    env_file:
      - .env
    environment:
      - DB_HOST=vectordb
      - RAG_PORT=${RAG_PORT:-8000}
    networks:
      - librechat-net

networks:
  librechat-net:
    driver: bridge

volumes:
  librechat-images:
  librechat-uploads:
  librechat-logs:
  mongodb-data:
  meilisearch-data:
  vectordb-data:
```

## Required Environment Variables (Dokploy Environment Tab)

```
# JWT — required, app crashes without these
JWT_SECRET=<run: openssl rand -hex 32>
JWT_REFRESH_SECRET=<run: openssl rand -hex 32>

# Encryption keys — exact lengths required
CREDS_KEY=<exactly 64 hex chars — run: openssl rand -hex 32>
CREDS_IV=<exactly 32 hex chars — run: openssl rand -hex 16>

# MongoDB auth (must match values in compose)
MONGO_USER=librechat
MONGO_PASS=<run: openssl rand -hex 24>

# pgvector (vectordb) credentials
VECTORDB_USER=raguser
VECTORDB_PASS=<run: openssl rand -hex 24>

# Meilisearch
MEILI_MASTER_KEY=<any random string>
```

**CREDS_KEY and CREDS_IV explained:**
- Used to AES-encrypt user API keys (OpenAI, Claude, etc.) before storing in MongoDB
- If lost, all stored API keys become unreadable — users must re-enter them
- Never change these after users have saved keys — rotating them invalidates all stored API keys
- Treat them as long-lived secrets — store them in a password manager alongside your deployment
- CREDS_KEY = 64 hex chars (32 bytes) — AES-256 key
- CREDS_IV = 32 hex chars (16 bytes) — initialization vector

## Domain/Port Setup

In Dokploy → Domains tab of the `api` service (or stack):
- **Container Port**: `3080`
- This is the LibreChat web UI port

## librechat.yaml Config File

LibreChat requires a config file at `/app/librechat.yaml`. Without it, you get:
```
error: Config file YAML format is invalid: ENOENT: no such file or directory, open '/app/librechat.yaml'
```
(Note: this error does not crash the app if JWT is set — it's a warning)

**Option A — File Mount in Dokploy:**
Advanced → **Mounts** → File Mount:
- **Content**: (paste YAML below)
- **File Path**: `librechat.yaml`
- **Mount Path**: `/app/librechat.yaml`

**Option B — `../files/` bind mount (from Dokploy's persistent files folder):**
In your compose YAML, under `api` service volumes:
```yaml
- ../files/librechat.yaml:/app/librechat.yaml
```
SSH to VPS once to create the file in the `files` directory alongside your compose deployment.

**Minimal librechat.yaml content:**
```yaml
version: 1.2.1
cache: true
# Add model endpoints here as needed
# See: https://www.librechat.ai/docs/configuration/librechat_yaml
```

## Creating the First Admin Account

LibreChat has no default admin credentials. The **first registered user becomes Admin**.

**Method 1 — Register via UI:**
1. Open LibreChat URL
2. Click "Sign up" / "Don't have an account?"
3. Register — this account is now Admin

**Method 2 — CLI (if registration is disabled):**
```bash
docker exec -it LibreChat npm run create-user
```

**Security:** After creating admin, go to Settings → disable "Allow Registration" to prevent
unauthorized signups.

## Common Errors

### `JwtStrategy requires a secret or key`
→ JWT_SECRET not in environment OR env var not passed to container
→ Make sure compose YAML has `- JWT_SECRET=${JWT_SECRET}` in environment block
→ Must **Redeploy** (not just Restart) after adding env vars

### `getaddrinfo EAI_AGAIN mongodb`
→ Race condition — api started before mongodb was ready
→ Fix: add `healthcheck` to mongodb and `depends_on: condition: service_healthy` to api
→ This stack uses a `librechat-net` custom network which ensures reliable DNS by service name
→ Do NOT use `container_name:` as a DNS workaround — it breaks Dokploy monitoring

### `EACCES permission denied` on uploads/logs
→ Remove `user: "${UID}:${GID}"` from compose — this is a **Dokploy-specific workaround** for
  stacks that hardcode a non-root UID from the dev environment. The LibreChat image handles
  its own filesystem permissions internally. Only apply this if you see the error; don't add
  it pre-emptively to stacks that don't need it.

### RAG API warning on startup
→ Normal if app just restarted — rag_api starts slower than api
→ Disappears after ~30-60 seconds once all services are up

# SOP: Compose (Stack) Deployment on Dokploy

**Use this for:** Multi-service applications using pre-built Docker images.
**Examples:** LibreChat, SigNoz, Wordpress+MySQL, Grafana+Prometheus, etc.

---

## Phase 1: Prepare Your docker-compose.yml

Before pasting into Dokploy, apply these transformations to any docker-compose.yml:

### 1. Remove `container_name:` from all services

**Critical:** Setting `container_name:` breaks Dokploy's logs, metrics, and monitoring features.

Before:
```yaml
services:
  mongodb:
    container_name: chat-mongodb   # remove this
```

After:
```yaml
services:
  mongodb:
    image: mongo:8.0.17            # no container_name
```

### 2. Replace relative bind mounts — use `../files/` or named volumes

These will break or become empty after AutoDeploy:
```yaml
volumes:
  - ./data:/app/data          # wiped by git clone on each deploy
  - ./config.yaml:/app/config # wiped by git clone on each deploy
  - /opt/myapp:/app/data      # absolute path cleaned up by Dokploy
```

Use `../files/` for bind mounts that need to survive deploys:
```yaml
volumes:
  - ../files/my-data:/app/data
  - ../files/my-logs:/app/logs
```

Or use named volumes for databases and large datasets:
```yaml
volumes:
  - myapp-data:/app/data

# At bottom of file:
volumes:
  myapp-data:
```

### 3. Remove user directives
```yaml
# Remove this line — causes EACCES permission errors in Dokploy
user: "${UID}:${GID}"
```

### 4. Fix env file references and add secrets to Dokploy's Environment tab

Before:
```yaml
env_file:
  - ./.env      # ./ prefix causes issues; file also won't exist if using raw compose
```

After — Option A (load everything, recommended for many vars):
```yaml
env_file:
  - .env        # no ./ prefix — Dokploy writes vars to .env in compose directory
```

After — Option B (select specific vars):
```yaml
environment:
  - MONGO_URI=${MONGO_URI}
  - JWT_SECRET=${JWT_SECRET}
```

Add all required values in Dokploy → **Environment tab**.

### 5. Handle config file mounts

Before:
```yaml
volumes:
  - ./config.yaml:/app/config.yaml   # wiped on each git clone
```

After (three options, in order of preference):

**Option A — `../files/` bind mount (persistent, survives deploys):**
```yaml
volumes:
  - ../files/app-config/config.yaml:/app/config.yaml
```
SSH to VPS once to create the file: `mkdir -p ~/dokploy-files/app-config && nano ~/dokploy-files/app-config/config.yaml`

**Option B — File Mount in Dokploy UI (no SSH needed for small configs):**
Delete the bind mount line. Go to Advanced → Mounts → File Mount:
- Content: [paste file content]
- File Path: `config.yaml`
- Mount Path: `/app/config.yaml`

**Option C — Init Container (complex/multiple configs or binaries needed):**
See `init-container-patterns.md`

---

## Phase 2: Create the Service in Dokploy

1. Navigate to your Project in Dokploy
2. Click **Create Service** → Select **Compose**
3. Name it (e.g., `my-app-stack`)
4. Go to **Editor** tab
5. Paste your adapted YAML
6. Click **Save**

---

## Phase 3: Configure Environment Variables

**How Dokploy env vars work:** Variables you add in the Environment tab are written to a `.env`
file. They are **NOT automatically injected** into containers — you must explicitly load them.

1. Go to **Environment** tab of the stack
2. Add all required variables (one per line, `KEY=VALUE` format)
3. Click **Save**
4. In your compose YAML, load them using one of:
   - `env_file: - .env` on each service (loads all vars — easiest for many secrets)
   - `environment: - MY_VAR=${MY_VAR}` per service (explicit, loads only what you list)

---

## Phase 4: Configure Volumes (if using File Mounts)

1. Go to **Advanced** tab
2. Scroll to **Volumes/Mounts** section
3. For each config file: Click **Add Volume** → **File Mount** tab
4. Fill in Content, File Path, and Mount Path
5. Click **Create**

---

## Phase 5: Deploy

1. Click the **Deploy** button (top right)
2. Watch **Logs** tab for errors
3. Common startup errors to watch for:
   - `is unhealthy` → check dependency service logs
   - `ENOENT` for config files → file mount not attached correctly
   - `EAI_AGAIN` → DNS issue, see networking section in SKILL.md

---

## Phase 6: Configure Domain (Optional)

⚠️ **Do this AFTER the first deploy.** The Domains tab requires a running service to select — you
cannot add a domain before the service has been deployed at least once.

For web apps that need a public URL (recommended approach since v0.7.0):
1. Find the web service in the container list
2. Go to **Domains** tab
3. Click **Add Domain**
4. Enter your domain (e.g., `app.yourdomain.com`)
5. **Container Port**: the app's internal listening port (e.g., `3000`, `8080`)
6. **HTTPS / SSL** — choose based on your DNS setup:
   - **Direct DNS** (A record pointing to VPS IP): ✅ Enable — Traefik handles Let's Encrypt
   - **Behind Cloudflare proxy** (orange cloud enabled): ❌ Disable — Cloudflare terminates TLS;
     enabling causes double-TLS / cert errors. Set Cloudflare SSL/TLS mode to **Full** (not Full Strict).
7. Click **Create**
8. Redeploy the service so Traefik picks up the new domain labels

Dokploy automatically injects Traefik labels into the compose file. You don't need to add them manually.
Use **Preview Compose** to see what the final file will look like before deploying.

In your compose YAML, use `expose:` instead of `ports:` for services routed via Traefik:
```yaml
services:
  app:
    expose:
      - 3000    # Traefik will route to this; no host port needed
```

### Isolated Deployments (for multiple instances or better isolation)
If you need to run the same app more than once (e.g., two WordPress sites), enable
**Isolated Deployments** in the Dokploy UI. This creates a private per-app network and avoids
service name conflicts on `dokploy-network`.

---

## Phase 7: Verify

- Check all containers show "Running" (green) status
- Access the application URL
- Check application-level logs for any remaining errors

---

## Maintenance

### Updating the stack
Click **Deploy** again → Dokploy pulls latest images and recreates containers.
Named volumes preserve all data automatically.

### Editing configuration
- For env vars: Edit Environment tab → **Redeploy** (not just Restart — env vars require full redeploy)
- For compose YAML: Edit in Editor tab → **Deploy**
- For File Mounts: Edit the mount content → **Deploy**

### Troubleshooting a stuck/crashed container
In Dokploy terminal or SSH:
```bash
# Restart single container without full redeploy
docker restart <container_name>

# View real-time logs
docker logs -f <container_name>

# Check container details
docker inspect <container_name>
```

# SOP: Git (Application) Deployment on Dokploy

**Use this for:** Source code in a Git repo that you want to build and run using a Dockerfile.
**Examples:** Custom Node.js/Go/Python APIs, full-stack apps you own or have forked.

---

## When to Use Git Deployment vs Compose

| Scenario | Use |
|----------|-----|
| Running official pre-built images (nginx, postgres, etc.) | Compose |
| Running your own app code from a Dockerfile | **Git (Application)** |
| Multi-service stack with databases | Compose |
| Single service you build from source | **Git (Application)** |
| Need to modify application code | **Git (Application)** (fork if public repo) |

**Do you need to fork the repo?**
- **No** → if you only need to change config files (use File Mounts/env vars in Dokploy)
- **Yes** → if you want to modify source code, or need automatic deploys via webhook

---

## Step 1: Create the Application Service

1. Go to your Dokploy Project
2. Click **Create Service** → **Application**
3. **Name**: use lowercase kebab-case (e.g., `my-api`, `cli-proxy-api`)
4. **Source**: Select **Git**
5. **Repository URL**: paste the HTTPS URL (e.g., `https://github.com/user/repo`)
6. **Branch**: `main` or `master`
7. **Build Path**: `/` (or `/server` if app is in a subfolder)
8. Click **Create**

---

## Step 2: Configure the Build

Go to the **General** tab:

### Option A: Dockerfile (Recommended)
- **Build Type**: `Dockerfile`
- **Dockerfile Path**: `./Dockerfile`
- **Context Path**: `./`

### Option B: Nixpacks (No Dockerfile)
- **Build Type**: `Nixpacks`
- Dokploy auto-detects language and builds
- Works well for standard Node.js, Python, Ruby apps

Click **Save**.

---

## Step 3: Inject Configuration

Never commit secrets to Git. Use Dokploy instead.

### A. Environment Variables
Go to **Environment** tab. Add variables as `KEY=VALUE`:
```
PORT=3000
DATABASE_URL=postgres://user:pass@host:5432/db
API_KEY=your_secret_key
NODE_ENV=production
```

### B. Config Files (File Mounts)
For apps that need a config file (e.g., `config.yaml`, `firebase.json`):
1. Go to **Advanced** → **Volumes**
2. Click **Add Volume** → **File Mount**
3. Fill in:
   - **Content**: paste the file text
   - **File Path**: filename only (e.g., `config.yaml`)
   - **Mount Path**: full container path (e.g., `/app/config/settings.yaml`)
4. Click **Create**

### C. Bind Mounts (Large Files)
For files too large for File Mount:
1. SSH into VPS: `ssh user@your-server`
2. Create directory and place file: `mkdir -p /opt/myapp && nano /opt/myapp/config.json`
3. In Dokploy Advanced → Volumes → **Bind Mount**:
   - **Host Path**: `/opt/myapp/config.json`
   - **Mount Path**: `/app/config.json`

---

## Step 4: Configure Persistence

Containers reset on every deploy. Mount directories that store important data:

1. Identify data directories (uploads, db files, auth tokens, logs)
2. Go to **Advanced** → **Volumes** → **Volume Mount**
3. For each:
   - **Name**: descriptive name (e.g., `myapp-uploads`)
   - **Mount Path**: container path (e.g., `/app/uploads`)
4. Click **Create**

---

## Step 5: Configure Networking

### Ports
Go to **Advanced** → **Ports** (or Network tab):
- **Published Port**: host port (external-facing)
- **Target Port**: what the app listens on internally
- **Protocol**: TCP
- Repeat for each port the service needs

### Domain (HTTPS)
Go to **Domains** tab:
- Add domain (e.g., `api.yourdomain.com`)
- **Container Port**: app's internal port
- Enable HTTPS
- When using a domain, you typically don't need a published port

---

## Step 6: Deploy

1. Go to **Deployments** tab
2. Click **Deploy**
3. Watch build logs — common failures:
   - **Dockerfile not found** → check Dockerfile Path in General tab
   - **npm install fails** → check for missing env vars at build time
   - **Build context error** → adjust Context Path

---

## Updating the Application

### Manual (for public repos you don't own)
1. Go to Deployments tab
2. Click **Deploy** — pulls latest commit
3. If stale cache: find "Redeploy without Cache" or clean Build Cache in System Settings

### Automatic (requires owning/forking the repo)
1. Go to **Deployments** tab → copy the **Webhook URL**
2. On GitHub: Settings → Webhooks → Add webhook
3. Paste the URL, set Content-Type to `application/json`, choose "Just the push event"
4. Every `git push` to the branch now triggers automatic deploy

---

## Cheat Sheet: Mount Types

| Type | Best For | Managed By |
|------|----------|------------|
| Volume Mount | Persistent data (DB, uploads, logs) | Docker (automatic) |
| File Mount (UI) | Small config files pasted as text | Dokploy |
| Bind Mount | Large files or VPS-managed files | You (requires SSH) |

# Init Container Patterns for Dokploy

Init containers solve a key Dokploy constraint: you can't use relative bind mounts (`./config.yaml`)
because Dokploy's build directory is ephemeral. Instead, use lightweight alpine containers to
generate config files into named volumes before the main services start.

## Pattern 1: Simple Config File Generation

```yaml
services:
  app-conf:
    image: alpine:3.20
    command:
      - /bin/sh
      - -lc
      - |
        cat > /config/app.yaml <<'YAML'
        server:
          port: 8080
          host: 0.0.0.0
        database:
          url: postgres://user:pass@db:5432/mydb
        YAML
    volumes:
      - app-config:/config
    restart: "no"   # exits after writing, never restarts

  app:
    image: myapp:latest
    depends_on:
      app-conf:
        condition: service_completed_successfully
    volumes:
      - app-config:/etc/myapp

volumes:
  app-config:
```

## Pattern 2: Multiple Config Files

```yaml
services:
  nginx-conf:
    image: alpine:3.20
    command:
      - /bin/sh
      - -lc
      - |
        # Main nginx config
        cat > /etc/nginx/nginx.conf <<'EOF'
        worker_processes auto;
        events { worker_connections 1024; }
        http {
          include /etc/nginx/conf.d/*.conf;
        }
        EOF
        
        # Site config
        cat > /etc/nginx/conf.d/app.conf <<'EOF'
        server {
          listen 80;
          location / {
            proxy_pass http://app:3000;
          }
        }
        EOF
    volumes:
      - nginx-config:/etc/nginx
    restart: "no"
```

## Pattern 3: Config + Binary Download

This pattern is used by SigNoz to download the `histogramQuantile` binary for ClickHouse:

> **Supply-chain security note:** Downloading and executing binaries at runtime from external
> URLs (GitHub releases) is an intentional architectural choice when the binary isn't available
> in a container image. To minimize risk:
> - **Pin the version explicitly** (never use `latest` or a floating tag in the URL)
> - **Verify the checksum** against the release's published SHA256 if one is provided
> - **Prefer a pre-built image** over runtime downloads whenever the vendor offers one
> - The `alpine` init container runs once and exits - the downloaded binary is never re-fetched
>   after the volume is populated on first deploy

```yaml
services:
  ch-conf:
    image: alpine:3.20
    command:
      - /bin/sh
      - -lc
      - |
        # Write config files
        cat > /config/settings.xml <<'XML'
        <?xml version="1.0"?>
        <config>...</config>
        XML
        
        # Download binary
        apk add --no-cache wget tar
        version="v1.0.0"   # pin to a specific, known-good release
        # Use $$ to escape shell vars from Docker Compose interpolation
        node_os=$$(uname -s | tr '[:upper:]' '[:lower:]')
        node_arch=$$(uname -m | sed s/aarch64/arm64/ | sed s/x86_64/amd64/)
        cd /tmp
        wget -O tool.tar.gz "https://github.com/owner/repo/releases/download/$${version}/tool_$${node_os}_$${node_arch}.tar.gz"
        # Optional: verify checksum (replace <expected_sha256> with the value from the release page)
        # echo "<expected_sha256>  tool.tar.gz" | sha256sum -c
        tar -xzf tool.tar.gz
        mv tool /scripts/myTool
        chmod +x /scripts/myTool
    volumes:
      - app-config:/config
      - app-scripts:/scripts
    restart: "no"

  app:
    depends_on:
      ch-conf:
        condition: service_completed_successfully
    volumes:
      - app-config:/etc/app/config.d
      - app-scripts:/usr/local/scripts
```

## Pattern 4: Multiple Init Containers

When you need separate containers for different initialization tasks (e.g., separate concerns,
different base images):

```yaml
services:
  config-writer:
    image: alpine:3.20
    command: ["/bin/sh", "-lc", "cat > /config/app.yaml <<'EOF'\nkey: value\nEOF"]
    volumes:
      - app-config:/config
    restart: "no"

  data-seeder:
    image: postgres:16
    command: ["psql", "-f", "/seeds/init.sql"]
    # ... setup
    restart: "no"

  app:
    depends_on:
      config-writer:
        condition: service_completed_successfully
      data-seeder:
        condition: service_completed_successfully
```

## Key Rules

### 1. Always set `restart: "no"`
Init containers must exit after completing their task. Without this, Docker might restart them
and overwrite your config files.

### 2. `condition: service_completed_successfully`
Main services must wait for init containers to finish:
```yaml
depends_on:
  my-init:
    condition: service_completed_successfully  # not service_started
```

### 3. Shell variable escaping: `$$` not `$`
Docker Compose processes `${VAR}` syntax before passing commands to containers. To use
shell variables inside init container commands, escape with `$$`:

```yaml
# WRONG — Docker Compose consumes $(uname -s), passes empty string
node_os=$(uname -s)

# CORRECT — becomes $(uname -s) inside the container shell
node_os=$$(uname -s)
```

This applies everywhere in the `command:` block within docker-compose.yml.

### 4. Shared volumes connect init to main services
```yaml
# Init container writes to /config
volumes:
  - my-config-volume:/config

# Main service reads from the same volume at different path
volumes:
  - my-config-volume:/etc/myapp/conf.d
```

### 5. Use heredoc delimiters with single quotes to prevent interpolation
```yaml
# The <<'YAML' prevents the shell inside the container from expanding $vars in the content
cat > /config/app.yaml <<'YAML'
api_key: ${SOME_KEY}   # this literal string is written, not expanded
YAML

# Use <<YAML (no quotes) only if you WANT shell to expand variables
cat > /config/app.yaml <<YAML
api_key: $(cat /run/secrets/api_key)   # this WOULD be expanded
YAML
```

## When to Use Each Volume Approach

| Scenario | Approach |
|----------|----------|
| Single small text config | File Mount in Dokploy UI |
| Multiple config files | Init container |
| Binary files needed | Init container with wget/curl |
| Config depends on other config | Init container (can compute values) |
| XML/YAML with complex structure | Init container (heredoc, no escaping issues) |
| Large file from VPS disk | Bind Mount (requires SSH) |

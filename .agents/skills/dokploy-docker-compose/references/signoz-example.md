# SigNoz Deployment on Dokploy

## Architecture Overview

SigNoz is an observability platform (metrics, traces, logs):
- `zookeeper-1` — ClickHouse cluster coordinator
- `clickhouse` — columnar database for telemetry storage
- `ch-conf` — init container: generates ClickHouse configs + downloads histogram binary
- `otel-collector-conf` — init container: generates OTel Collector + OpAMP configs
- `signoz-telemetrystore-migrator` — runs DB migrations
- `signoz` — main web UI and API (port 8080)
- `signoz-otel-collector` — receives OTLP data from apps

## The Init Container Pattern (Dokploy-Specific)

Since Dokploy doesn't support bind mounts from relative paths, SigNoz's config files are
generated at runtime by alpine init containers that write into shared named volumes.

This replaces the bind mounts used in the official GitHub compose file:
```
Official: - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
Dokploy:  - otel-config:/etc/otel  (written by otel-collector-conf init container)
```

## Complete docker-compose.yml (Dokploy-optimized)

```yaml
services:
  otel-collector-conf:
    image: alpine:3.20
    command:
      - /bin/sh
      - -lc
      - |
        cat > /otel/otel-collector-config.yaml <<'YAML'
        receivers:
          otlp:
            protocols:
              grpc:
                endpoint: 0.0.0.0:4317
              http:
                endpoint: 0.0.0.0:4318
        processors:
          batch:
            send_batch_size: 1024
            send_batch_max_size: 2048
            timeout: 0.75s
        exporters:
          clickhousetraces:
            datasource: tcp://clickhouse:9000/signoz_traces
          signozclickhousemetrics:
            dsn: tcp://clickhouse:9000/signoz_metrics
          clickhouselogsexporter:
            dsn: tcp://clickhouse:9000/signoz_logs
        service:
          pipelines:
            traces:
              receivers: [otlp]
              processors: [batch]
              exporters: [clickhousetraces]
            metrics:
              receivers: [otlp]
              processors: [batch]
              exporters: [signozclickhousemetrics]
            logs:
              receivers: [otlp]
              processors: [batch]
              exporters: [clickhouselogsexporter]
        YAML
        cat > /otel/manager-config.yaml <<'YAML'
        server_endpoint: ws://signoz:4320/v1/opamp
        capabilities:
          accepts_remote_config: true
          accepts_restart_command: true
          reports_effective_config: true
        YAML
    volumes:
      - otel-config:/otel
    restart: "no"

  ch-conf:
    image: alpine:3.20
    command:
      - /bin/sh
      - -lc
      - |
        cat > /config/cluster.xml <<'XML'
        <?xml version="1.0"?>
        <clickhouse>
          <remote_servers>
            <cluster>
              <shard>
                <replica>
                  <host>clickhouse</host>
                  <port>9000</port>
                </replica>
              </shard>
            </cluster>
          </remote_servers>
          <zookeeper>
            <node index="1">
              <host>zookeeper-1</host>
              <port>2181</port>
            </node>
          </zookeeper>
          <distributed_ddl>
            <path>/clickhouse/task_queue/ddl</path>
          </distributed_ddl>
          <macros>
            <shard>0</shard>
            <replica>clickhouse</replica>
          </macros>
        </clickhouse>
        XML
        cat > /config/users.xml <<'XML'
        <?xml version="1.0"?>
        <clickhouse>
          <users>
            <default>
              <password></password>
              <networks><ip>::/0</ip></networks>
              <profile>default</profile>
              <quota>default</quota>
              <access_management>1</access_management>
              <named_collection_control>1</named_collection_control>
              <show_named_collections>1</show_named_collections>
              <show_named_collections_secrets>1</show_named_collections_secrets>
            </default>
          </users>
        </clickhouse>
        XML
        cat > /config/config-override.xml <<'XML'
        <?xml version="1.0"?>
        <clickhouse>
          <logger><level>warning</level><console>true</console></logger>
          <listen_host>0.0.0.0</listen_host>
          <http_port>8123</http_port>
          <tcp_port>9000</tcp_port>
          <max_connections>4096</max_connections>
          <keep_alive_timeout>3</keep_alive_timeout>
          <max_concurrent_queries>100</max_concurrent_queries>
          <max_table_size_to_drop>0</max_table_size_to_drop>
          <max_partition_size_to_drop>0</max_partition_size_to_drop>
        </clickhouse>
        XML
        # Supply-chain note: version is pinned; verify SHA256 from the GitHub release page
        # before deploying to production (sha256sum -c histogram-quantile.tar.gz.sha256)
        version="v0.0.1"   # pin to a specific, known-good release
        node_os=$$(uname -s | tr '[:upper:]' '[:lower:]')
        node_arch=$$(uname -m | sed s/aarch64/arm64/ | sed s/x86_64/amd64/)
        apk add --no-cache wget tar
        cd /tmp
        wget -O histogram-quantile.tar.gz "https://github.com/SigNoz/signoz/releases/download/histogram-quantile%2F$${version}/histogram-quantile_$${node_os}_$${node_arch}.tar.gz"
        # Optional: verify checksum (replace <sha256> with value from release page)
        # echo "<sha256>  histogram-quantile.tar.gz" | sha256sum -c
        tar -xvzf histogram-quantile.tar.gz
        mv histogram-quantile /scripts/histogramQuantile
        chmod +x /scripts/histogramQuantile
    volumes:
      - ch-config:/config
      - ch-scripts:/scripts
    restart: "no"

  zookeeper-1:
    image: signoz/zookeeper:3.7.1
    user: root
    restart: unless-stopped
    environment:
      - ZOO_SERVER_ID=1
      - ALLOW_ANONYMOUS_LOGIN=yes
      - ZOO_AUTOPURGE_INTERVAL=1
      - ZOO_ENABLE_PROMETHEUS_METRICS=yes
      - ZOO_PROMETHEUS_METRICS_PORT_NUMBER=9141
    healthcheck:
      test: ["CMD-SHELL", "curl -s -m 2 http://localhost:8080/commands/ruok | grep error | grep null"]
      interval: 30s
      timeout: 5s
      retries: 3
    volumes:
      - zookeeper-data:/bitnami/zookeeper

  clickhouse:
    image: clickhouse/clickhouse-server:25.5.6
    restart: unless-stopped
    depends_on:
      ch-conf:
        condition: service_completed_successfully
      zookeeper-1:
        condition: service_healthy
    environment:
      - CLICKHOUSE_SKIP_USER_SETUP=1
    ulimits:
      nproc: 65535
      nofile:
        soft: 262144
        hard: 262144
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "0.0.0.0:8123/ping"]
      interval: 30s
      timeout: 5s
      retries: 3
    volumes:
      - clickhouse-data:/var/lib/clickhouse
      - ch-config:/etc/clickhouse-server/config.d
      - ch-scripts:/var/lib/clickhouse/user_scripts

  signoz-telemetrystore-migrator:
    image: signoz/signoz-otel-collector:v0.144.2
    depends_on:
      clickhouse:
        condition: service_healthy
    environment:
      - SIGNOZ_OTEL_COLLECTOR_CLICKHOUSE_DSN=tcp://clickhouse:9000
      - SIGNOZ_OTEL_COLLECTOR_CLICKHOUSE_CLUSTER=cluster
      - SIGNOZ_OTEL_COLLECTOR_CLICKHOUSE_REPLICATION=true
      - SIGNOZ_OTEL_COLLECTOR_TIMEOUT=10m
    entrypoint:
      - /bin/sh
    command:
      - -c
      - |
        /signoz-otel-collector migrate bootstrap &&
        /signoz-otel-collector migrate sync up &&
        /signoz-otel-collector migrate async up
    restart: on-failure

  signoz:
    image: signoz/signoz:v0.116.1
    depends_on:
      clickhouse:
        condition: service_healthy
    environment:
      - SIGNOZ_ALERTMANAGER_PROVIDER=signoz
      - SIGNOZ_TELEMETRYSTORE_CLICKHOUSE_DSN=tcp://clickhouse:9000
      - SIGNOZ_SQLSTORE_SQLITE_PATH=/var/lib/signoz/signoz.db
      - SIGNOZ_TOKENIZER_JWT_SECRET=${SIGNOZ_JWT_SECRET:-secret}
    ports:
      - 8080:8080
    restart: unless-stopped
    volumes:
      - signoz-sqlite:/var/lib/signoz
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "localhost:8080/api/v1/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  signoz-otel-collector:
    image: signoz/signoz-otel-collector:v0.144.2
    depends_on:
      clickhouse:
        condition: service_healthy
      otel-collector-conf:
        condition: service_completed_successfully
    entrypoint:
      - /bin/sh
    command:
      - -c
      - |
        /signoz-otel-collector migrate sync check &&
        /signoz-otel-collector --config=/etc/otel/otel-collector-config.yaml --manager-config=/etc/otel/manager-config.yaml --copy-path=/var/tmp/collector-config.yaml
    volumes:
      - otel-config:/etc/otel
    environment:
      - OTEL_RESOURCE_ATTRIBUTES=host.name=signoz-host,os.type=linux
      - SIGNOZ_OTEL_COLLECTOR_CLICKHOUSE_DSN=tcp://clickhouse:9000
      - SIGNOZ_OTEL_COLLECTOR_CLICKHOUSE_CLUSTER=cluster
    ports:
      - 4317:4317  # OTLP gRPC receiver
      - 4318:4318  # OTLP HTTP receiver
    restart: unless-stopped

volumes:
  clickhouse-data:
  ch-config:
  ch-scripts:
  zookeeper-data:
  signoz-sqlite:
  otel-config:
```

## Environment Variable (Dokploy Environment Tab)
```
SIGNOZ_JWT_SECRET=<any random string>
```

## First-Time Setup

1. Deploy the stack
2. Wait for all containers to go green (~2-3 minutes)
3. Access UI at `http://<server-ip>:8080`
4. You'll see: `cannot create agent without orgId` in logs — this is **normal**
5. Complete organization/admin setup in the UI
6. Once org is created, the log error disappears automatically

## Port Reference

| Port | Service | Purpose |
|------|---------|---------|
| 8080 | signoz | Web UI (mapped from internal 8080) |
| 4317 | signoz-otel-collector | OTLP gRPC receiver (apps send traces here) |
| 4318 | signoz-otel-collector | OTLP HTTP receiver (apps send traces here) |

## Connecting Apps to SigNoz

For Node.js/Hono apps, use the OTLP HTTP exporter (avoids gRPC binary compilation issues):
```typescript
// instrumentation.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://<server-ip>:4318/v1/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: 'my-service-name',
});
sdk.start();
```

Run with `--import ./instrumentation.js` flag before your app entry point.

## Zookeeper Image Notes

SigNoz supports two Zookeeper images:

| Image | healthcheck method | user | Notes |
|-------|-------------------|------|-------|
| `signoz/zookeeper:3.7.1` | curl AdminServer API (port 8080) | root | Official SigNoz image |
| `bitnamilegacy/zookeeper:3.7.1` | nc port 2181 | 1001 | Fallback if volume permission issues |

**Volume migration warning:** Switching from bitnami to signoz/zookeeper image on an existing
deployment can cause permission errors on the volume (bitnami uses uid 1001, signoz uses root).
Fix: rename the volume in YAML (e.g., `zookeeper-data-v2`) to force fresh initialization.
Zookeeper only stores ClickHouse metadata — this is safe to recreate.

**Do NOT use `ZOO_4LW_COMMANDS_WHITELIST`** with signoz/zookeeper — it's a Bitnami-specific
env var that this image doesn't recognize. The healthcheck uses curl, not nc.

## Common Errors

### `cannot create agent without orgId`
→ Normal! Happens before org is created. Access UI and complete setup.

### `zookeeper-1 is unhealthy`
→ Wrong healthcheck for image (bitnami vs signoz healthcheck methods differ)
→ Or: volume permission conflict from old bitnami data
→ Fix: rename volume to `zookeeper-data-v2` to start fresh

### `dependency zookeeper-1 failed to start`
→ Caused by zookeeper unhealthy above
→ Fix zookeeper first, this resolves automatically

### Shell variable escaping (`$$` vs `$`)
In heredoc commands inside docker-compose.yml, use `$$` for shell variables to prevent
Docker Compose from trying to interpolate them as compose variables:
```bash
node_os=$$(uname -s)  # correct in docker-compose.yml
node_os=$(uname -s)   # would be consumed by compose, becomes empty string
```

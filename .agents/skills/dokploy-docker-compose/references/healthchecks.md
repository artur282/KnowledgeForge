# Healthchecks Reference

Copy-paste snippets for common services. Add `start_period` when the service takes time to initialize (databases, indexers).

## MongoDB
```yaml
healthcheck:
  test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

## PostgreSQL
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```
> Use `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}` if you have those vars set.

## Redis
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 3s
  retries: 3
```

## ClickHouse
```yaml
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "0.0.0.0:8123/ping"]
  interval: 30s
  timeout: 5s
  retries: 3
```

## Zookeeper (signoz/zookeeper image — AdminServer API on port 8080)
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -s -m 2 http://localhost:8080/commands/ruok | grep error | grep null"]
  interval: 30s
  timeout: 5s
  retries: 3
```

## Zookeeper (bitnami image — nc on port 2181)
```yaml
healthcheck:
  test: ["CMD-SHELL", "echo ruok | nc -w 2 127.0.0.1 2181 | grep imok"]
  interval: 30s
  timeout: 5s
  retries: 3
```

## HTTP/curl (generic web service)
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

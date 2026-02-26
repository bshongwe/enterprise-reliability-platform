# Observability

## Stack Components

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Metrics**: Exposed at `/metrics` endpoint on each service

## Metrics Exposed

### HTTP Metrics
- `http_requests_total`: Total requests by service, method, endpoint, status
- `http_request_duration_seconds`: Request latency histogram

### Database Metrics
- `db_operations_total`: DB operations by service, operation, status
- `db_connection_errors_total`: Connection errors by service

### SLO Metrics
- `error_budget_remaining_ratio`: Remaining error budget (0-1)

## Quick Start

```bash
# Start Prometheus and Grafana
docker-compose up prometheus grafana

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

## Alert Rules

See `alerts/slo-alerts.yml` for:
- SLO breach alerts
- Error budget burn rate alerts
- Deployment freeze triggers

# Runbooks

Operational runbooks for incident response, troubleshooting, and recovery.

## Available Runbooks

### Critical Incidents
- [SEV1: Payment API Outage](sev1-payment-outage.md) - Complete payment processing failure
- [SEV2: Latency Breach](sev2-latency-breach.md) - Performance degradation and SLO risk

### Infrastructure
- [Database Connection Failure](database-connection-failure.md) - DB connectivity issues
- [Deployment Rollback](deployment-rollback.md) - Restore service to previous state

## Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|----------|
| SEV1 | Critical outage | <5 minutes | Payment API down |
| SEV2 | Major degradation | <15 minutes | Latency >500ms |
| SEV3 | Minor degradation | <1 hour | Single pod failure |
| SEV4 | Informational | <24 hours | Monitoring alert |

## On-Call Procedures

1. Acknowledge alert in PagerDuty
2. Join #incidents Slack channel
3. Follow relevant runbook
4. Update incident timeline
5. Communicate status every 15 minutes
6. Create postmortem after resolution

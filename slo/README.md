# SLO Definitions

All SLOs are measured monthly and enforce reliability using error budgets.

| Service           | SLI                                | SLO (Monthly)  | Notes / Enforcement                                      |
|------------------|-----------------------------------|----------------|-----------------------------------------------------------|
| Payments API      | successful_requests / total       | 99.95%         | Canary auto-rollback if budget burn > 50% in 24h        |
| Ledger Service    | successful_writes / total         | 99.99%         | Critical for audit logs; triggers immediate alert       |
| Account Service   | read_latency < 200ms P95          | 99.9%          | Partial degradation acceptable; SEV3 if breached        |
| Notification API  | delivery_success_rate             | 99.5%          | Slack/email notification delivery                        |
| Analytics Pipeline| query_latency P99 < 1s            | 99.9%          | Ensures SRE dashboards reflect true metrics             |
| DB Connections    | connection_errors / total         | 99.95%         | Monitored across AWS & OCI; triggers failover           |
| Queue Backlog     | messages_queued < threshold       | 99%            | SLA enforced via automated alerts                        |

# Error Budget Enforcement

- If **>50%** of monthly error budget is burned in **24h**, freeze deployments
- Canary auto-rollbacks for critical service breaches
- Incident postmortem required for SEV1/SEV2 events
- SLOs updated quarterly with corporate stakeholder input

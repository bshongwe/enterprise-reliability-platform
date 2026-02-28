# SEV1: Payment API Outage

**Severity:** SEV1 (Critical)  
**Impact:** Complete payment processing failure  
**SLO:** 99.95% availability

## Symptoms
- Payment API returning 5xx errors
- Prometheus alert: `PaymentsErrorBudgetBurn`
- Zero successful payment transactions
- Customer reports of payment failures

## Immediate Actions (First 5 Minutes)

### 1. Verify Outage
```bash
# Check service health
curl https://payments-api.prod/healthz

# Check Prometheus metrics
curl "http://prometheus:9090/api/v1/query?query=up{job='payments-api'}"
```

### 2. Check Dependencies
```bash
# Verify ledger service
curl https://ledger-service.prod/healthz

# Check database connectivity
kubectl logs -l app=payments-api --tail=50 | grep -i "error\|exception"
```

### 3. Activate Circuit Breaker
```bash
# Route traffic to DR region (Azure)
kubectl patch service payments-api -p '{"spec":{"selector":{"region":"azure-dr"}}}'
```

## Investigation (5-15 Minutes)

### Check Recent Deployments
```bash
# View recent changes
kubectl rollout history deployment/payments-api

# Check ArgoCD sync status
argocd app get payments-api
```

### Review Logs
```bash
# Application logs
kubectl logs -l app=payments-api --since=30m | grep ERROR

# Check for OOM kills
kubectl get events --sort-by='.lastTimestamp' | grep OOM
```

### Check Resource Utilization
```bash
# CPU/Memory usage
kubectl top pods -l app=payments-api

# Check pod status
kubectl get pods -l app=payments-api
```

## Mitigation Options

### Option 1: Rollback Deployment
```bash
# Rollback to previous version
kubectl rollout undo deployment/payments-api

# Monitor rollback
kubectl rollout status deployment/payments-api
```

### Option 2: Scale Up
```bash
# Increase replicas
kubectl scale deployment/payments-api --replicas=6

# Verify scaling
kubectl get pods -l app=payments-api -w
```

### Option 3: Restart Pods
```bash
# Rolling restart
kubectl rollout restart deployment/payments-api
```

## Recovery Verification

### 1. Check Service Health
```bash
# Verify endpoints
for i in {1..10}; do curl -s https://payments-api.prod/healthz; sleep 1; done

# Check error rate
curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{service='payments',status='error'}[5m])"
```

### 2. Test Payment Flow
```bash
# Create test payment
curl -X POST https://payments-api.prod/payments \
  -H "X-API-Key: $API_KEY" \
  -d '{"sender_account":"TEST001","receiver_account":"TEST002","amount":1.0,"currency":"USD","reference":"health-check"}'
```

### 3. Monitor SLO
```bash
# Check error budget
python slo/calculate_error_budget.py
```

## Communication

### Internal
- Post in #incidents Slack channel
- Update status page
- Notify on-call SRE team

### External
- Update customer status page if outage >5 minutes
- Prepare customer communication if SLO breach

## Post-Incident

### Required Actions
- [ ] Create postmortem within 48 hours
- [ ] Update error budget tracking
- [ ] Review and update alerting thresholds
- [ ] Schedule blameless postmortem meeting

### Postmortem Template
See: `postmortems/template.md`

## Escalation

- **Primary On-Call:** Check PagerDuty rotation
- **Secondary:** SRE Team Lead
- **Executive:** VP Engineering (if outage >30 minutes)

## Related Runbooks
- [SEV2: Latency Breach](sev2-latency-breach.md)
- [Database Connection Failure](database-connection-failure.md)
- [Deployment Rollback](deployment-rollback.md)

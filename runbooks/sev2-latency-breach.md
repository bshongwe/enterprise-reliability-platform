# SEV2: Latency Breach

**Severity:** SEV2 (High)  
**Impact:** Degraded performance, SLO at risk  
**SLO:** P95 latency <200ms (Account Service), P99 <1s (Analytics)

## Symptoms
- Prometheus alert: `HighLatency` or `AccountServiceLatencyBreach`
- P95 latency >200ms for sustained period
- Customer complaints about slow responses
- Error budget burn rate elevated

## Immediate Actions (First 10 Minutes)

### 1. Identify Affected Service
```bash
# Check latency by service
curl "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))"

# View current P95/P99
kubectl port-forward svc/grafana 3000:3000
# Open: http://localhost:3000/d/slo-dashboard
```

### 2. Check Database Performance
```bash
# Ledger service DB operations
curl "http://prometheus:9090/api/v1/query?query=rate(db_operations_total{service='ledger'}[5m])"

# Check for slow queries
kubectl logs -l app=ledger-service --tail=100 | grep -i "slow\|timeout"
```

### 3. Review Resource Constraints
```bash
# Check if pods are CPU throttled
kubectl top pods -l app=account-service

# Check memory pressure
kubectl describe pods -l app=account-service | grep -A 5 "Conditions"
```

## Investigation

### Check Recent Changes
```bash
# Recent deployments
kubectl rollout history deployment/account-service

# Check for config changes
git log --since="2 hours ago" --oneline -- k8s/
```

### Analyze Traffic Patterns
```bash
# Request rate
curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total[5m])"

# Check for traffic spikes
kubectl logs -l app=payments-api --since=1h | wc -l
```

### Database Connection Pool
```bash
# Check connection errors
curl "http://prometheus:9090/api/v1/query?query=db_connection_errors_total"

# Review pool exhaustion
kubectl logs -l app=ledger-service | grep "connection pool"
```

## Mitigation Options

### Option 1: Scale Horizontally
```bash
# Increase replicas
kubectl scale deployment/account-service --replicas=5

# Enable HPA if not active
kubectl autoscale deployment account-service --min=3 --max=10 --cpu-percent=70
```

### Option 2: Increase Resources
```bash
# Edit deployment
kubectl edit deployment account-service

# Update CPU/memory limits:
# requests: cpu: 500m, memory: 512Mi
# limits: memory: 1Gi
```

### Option 3: Enable Caching
```bash
# Deploy Redis cache (if available)
kubectl apply -f k8s/redis-cache.yaml

# Update service to use cache
kubectl set env deployment/account-service REDIS_URL=redis://redis:6379
```

### Option 4: Rate Limiting
```bash
# Apply rate limits at ingress
kubectl apply -f k8s/rate-limit-config.yaml
```

## Recovery Verification

### 1. Monitor Latency Improvement
```bash
# Watch P95 latency
watch -n 5 'curl -s "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket{service=\"account\"}[5m]))" | jq'
```

### 2. Check Error Budget Impact
```bash
# Calculate remaining budget
python slo/calculate_error_budget.py
```

### 3. Verify Customer Experience
```bash
# Run synthetic tests
for i in {1..20}; do
  time curl -s https://account-service.prod/accounts/TEST001 > /dev/null
done
```

## Communication

### Internal
- Post latency graphs in #incidents
- Update incident timeline
- Notify product team if customer-facing

### External
- Update status page if P95 >500ms for >15 minutes
- Prepare customer advisory if SLO breach imminent

## Post-Incident

### Required Actions
- [ ] Review query optimization opportunities
- [ ] Analyze database indexing
- [ ] Update resource requests/limits
- [ ] Consider implementing caching layer
- [ ] Create postmortem if SLO breached

## Prevention

### Proactive Measures
- Set up latency alerts at 80% of SLO threshold
- Implement query performance monitoring
- Regular load testing
- Database query optimization reviews

## Escalation

- **Primary:** On-call SRE
- **Secondary:** Database Team (if DB-related)
- **Escalate to SEV1 if:** Latency >1s or error rate >5%

## Related Runbooks
- [SEV1: Payment Outage](sev1-payment-outage.md)
- [Database Connection Failure](database-connection-failure.md)

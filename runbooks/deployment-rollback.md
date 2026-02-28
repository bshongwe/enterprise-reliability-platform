# Deployment Rollback

**Severity:** Varies (SEV2-SEV4)  
**Impact:** Restore service to previous stable state  
**Use Case:** Failed deployment, canary failure, configuration error

## When to Rollback

### Automatic Rollback Triggers
- Canary error rate >1% for 5 minutes
- Error budget burn >50% in 1 hour
- Health check failures >3 consecutive checks
- P95 latency >2x baseline

### Manual Rollback Criteria
- Critical bug discovered in production
- Security vulnerability introduced
- Data corruption risk
- Customer-reported critical issues

## Pre-Rollback Checklist

### 1. Verify Issue is Deployment-Related
```bash
# Check deployment history
kubectl rollout history deployment/payments-api

# Compare current vs previous version
kubectl describe deployment payments-api | grep Image
```

### 2. Assess Impact
```bash
# Check error rate
curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status='error'}[5m])"

# Review affected users
kubectl logs -l app=payments-api --since=15m | grep -c "error"
```

### 3. Notify Stakeholders
- Post in #incidents channel
- Tag deployment owner
- Update status page if customer-facing

## Rollback Methods

### Method 1: Kubernetes Rollback (Fastest)
```bash
# Rollback to previous revision
kubectl rollout undo deployment/payments-api

# Rollback to specific revision
kubectl rollout undo deployment/payments-api --to-revision=5

# Monitor rollback progress
kubectl rollout status deployment/payments-api -w

# Verify pods are running
kubectl get pods -l app=payments-api
```

**Time to Complete:** 1-2 minutes

### Method 2: GitOps Rollback (Recommended)
```bash
# Revert the commit that updated manifests
cd enterprise-reliability-platform
git log --oneline k8s/payments-api/deployment.yaml

# Revert the problematic commit
git revert <commit-hash>

# Push to trigger ArgoCD sync
git push origin main

# Monitor ArgoCD sync
argocd app sync payments-api
argocd app wait payments-api --health
```

**Time to Complete:** 2-5 minutes

### Method 3: Manual Image Update
```bash
# Update to previous image tag
kubectl set image deployment/payments-api \
  payments-api=ghcr.io/bshongwe/payments-api:<previous-sha>

# Verify update
kubectl rollout status deployment/payments-api
```

**Time to Complete:** 1-2 minutes

### Method 4: Canary Rollback
```bash
# Delete canary deployment
kubectl delete deployment payments-api-canary

# Verify stable deployment is handling traffic
kubectl get pods -l app=payments-api,version=stable

# Revert canary manifest in git
git revert <canary-commit-hash>
git push origin main
```

**Time to Complete:** 1-3 minutes

## Post-Rollback Verification

### 1. Health Checks
```bash
# Verify all pods are ready
kubectl get pods -l app=payments-api

# Test health endpoint
for i in {1..10}; do
  curl -s https://payments-api.prod/healthz
  sleep 1
done
```

### 2. Functional Testing
```bash
# Test critical path
curl -X POST https://payments-api.prod/payments \
  -H "X-API-Key: $API_KEY" \
  -d '{"sender_account":"TEST001","receiver_account":"TEST002","amount":10.0,"currency":"USD","reference":"rollback-test"}'

# Verify ledger integration
curl https://ledger-service.prod/entries/test_payment_id \
  -H "X-API-Key: $API_KEY"
```

### 3. Monitor Metrics
```bash
# Check error rate normalized
curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{service='payments',status='error'}[5m])"

# Verify latency returned to baseline
curl "http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket{service='payments'}[5m]))"

# Check error budget impact
python slo/calculate_error_budget.py
```

### 4. Log Analysis
```bash
# Check for errors in rolled-back version
kubectl logs -l app=payments-api --since=5m | grep -i error

# Verify no crash loops
kubectl get pods -l app=payments-api -w
```

## Rollback Failure Scenarios

### If Rollback Fails
```bash
# Check pod events
kubectl describe pods -l app=payments-api

# Check for image pull errors
kubectl get events --sort-by='.lastTimestamp' | grep -i error

# Force delete and recreate
kubectl delete pods -l app=payments-api --force --grace-period=0
```

### If Previous Version Also Broken
```bash
# Rollback to known-good revision
kubectl rollout history deployment/payments-api
kubectl rollout undo deployment/payments-api --to-revision=<known-good>

# Or deploy emergency hotfix
kubectl set image deployment/payments-api \
  payments-api=ghcr.io/bshongwe/payments-api:emergency-fix
```

## Communication

### During Rollback
```
🔄 ROLLBACK IN PROGRESS
Service: payments-api
Reason: [error rate spike / latency breach / bug]
ETA: 2-5 minutes
Status: [link to status page]
```

### After Rollback
```
✅ ROLLBACK COMPLETE
Service: payments-api
Previous version: <sha>
Current version: <sha>
Status: Monitoring for 15 minutes
Next steps: RCA and postmortem
```

## Post-Rollback Actions

### Immediate (0-1 hour)
- [ ] Monitor service for 15-30 minutes
- [ ] Verify error budget impact
- [ ] Document rollback reason
- [ ] Update incident timeline

### Short-term (1-24 hours)
- [ ] Root cause analysis
- [ ] Fix identified issues
- [ ] Update tests to catch issue
- [ ] Plan re-deployment strategy

### Long-term (1-7 days)
- [ ] Create postmortem
- [ ] Update deployment checklist
- [ ] Improve automated testing
- [ ] Review rollback procedures

## Prevention

### Pre-Deployment Checks
- Run full test suite
- Check error budget status
- Review recent incidents
- Verify canary configuration
- Test in staging environment

### Automated Safeguards
- Canary deployments with auto-rollback
- Error budget enforcement in CI/CD
- Automated smoke tests post-deployment
- Progressive traffic shifting

## Escalation

- **Primary:** Deployment owner
- **Secondary:** On-call SRE
- **Escalate if:** Rollback fails or issue persists

## Related Runbooks
- [SEV1: Payment Outage](sev1-payment-outage.md)
- [SEV2: Latency Breach](sev2-latency-breach.md)
- [Database Connection Failure](database-connection-failure.md)

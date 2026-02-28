# Database Connection Failure

**Severity:** SEV1/SEV2 (depends on scope)  
**Impact:** Service degradation or outage  
**SLO:** 99.95% connection success rate

## Symptoms
- Prometheus alert: `db_connection_errors_total` elevated
- Services logging "connection refused" or "timeout"
- Ledger service unable to write transactions
- Account service unable to query balances

## Immediate Actions (First 5 Minutes)

### 1. Identify Affected Database
```bash
# Check connection errors by service
curl "http://prometheus:9090/api/v1/query?query=rate(db_connection_errors_total[5m])"

# Check service logs
kubectl logs -l app=ledger-service --tail=50 | grep -i "connection\|database"
```

### 2. Verify Database Status
```bash
# For SQLite (local dev)
kubectl exec -it deployment/ledger-service -- ls -lh /app/*.db

# For production DB (OCI Autonomous DB)
# Check OCI console or use SQL*Plus
sqlplus admin@ledger_db <<EOF
SELECT status FROM v\$instance;
EOF
```

### 3. Check Connection Pool
```bash
# Review pool configuration
kubectl get configmap db-config -o yaml

# Check active connections
kubectl logs -l app=ledger-service | grep "pool size\|active connections"
```

## Investigation

### Check Network Connectivity
```bash
# Test DB endpoint from pod
kubectl exec -it deployment/ledger-service -- nc -zv ledger-db.oci.internal 1521

# Check DNS resolution
kubectl exec -it deployment/ledger-service -- nslookup ledger-db.oci.internal
```

### Review Database Metrics
```bash
# Check DB CPU/memory (OCI)
oci db autonomous-database get --autonomous-database-id <db-ocid>

# Check for locks
# Connect to DB and run:
SELECT * FROM v$lock WHERE block > 0;
```

### Check Credentials
```bash
# Verify secret exists
kubectl get secret db-credentials -o yaml

# Test credentials manually
kubectl exec -it deployment/ledger-service -- env | grep DATABASE
```

## Mitigation Options

### Option 1: Restart Connection Pool
```bash
# Rolling restart of affected service
kubectl rollout restart deployment/ledger-service

# Monitor restart
kubectl rollout status deployment/ledger-service
```

### Option 2: Increase Connection Pool Size
```bash
# Update environment variable
kubectl set env deployment/ledger-service DB_POOL_SIZE=20

# Or edit configmap
kubectl edit configmap db-config
```

### Option 3: Failover to DR Database
```bash
# Switch to Azure DR replica
kubectl set env deployment/ledger-service DATABASE_URL=$AZURE_DR_DB_URL

# Verify failover
kubectl logs -l app=ledger-service --tail=20
```

### Option 4: Enable Read Replica
```bash
# Route read traffic to replica
kubectl apply -f k8s/db-read-replica-service.yaml

# Update service configuration
kubectl set env deployment/account-service READ_DB_URL=$READ_REPLICA_URL
```

## Recovery Verification

### 1. Test Database Connectivity
```bash
# From pod
kubectl exec -it deployment/ledger-service -- python3 <<EOF
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
conn = engine.connect()
print("Connection successful")
conn.close()
EOF
```

### 2. Verify Write Operations
```bash
# Create test ledger entry
curl -X POST https://ledger-service.prod/entries \
  -H "X-API-Key: $API_KEY" \
  -d '{"payment_id":"test_001","sender_account":"TEST","receiver_account":"TEST","amount":1.0,"currency":"USD","reference":"health-check"}'
```

### 3. Monitor Connection Errors
```bash
# Watch error rate
watch -n 5 'curl -s "http://prometheus:9090/api/v1/query?query=rate(db_connection_errors_total[5m])" | jq'
```

## Root Cause Analysis

### Common Causes
1. **Connection pool exhaustion** - Too many concurrent requests
2. **Network issues** - Firewall rules, security groups
3. **Database overload** - CPU/memory saturation
4. **Credential rotation** - Expired or incorrect credentials
5. **DNS issues** - Unable to resolve database hostname
6. **Database maintenance** - Scheduled or emergency maintenance

### Investigation Checklist
- [ ] Check recent infrastructure changes
- [ ] Review database maintenance windows
- [ ] Analyze traffic patterns for spikes
- [ ] Verify security group rules
- [ ] Check for expired credentials
- [ ] Review database performance metrics

## Communication

### Internal
- Post connection error graphs in #incidents
- Notify database team immediately
- Update incident timeline with findings

### External
- Update status page if customer-facing impact
- Prepare communication if outage >10 minutes

## Post-Incident

### Required Actions
- [ ] Create postmortem
- [ ] Review connection pool sizing
- [ ] Implement connection retry logic
- [ ] Set up database failover automation
- [ ] Add connection pool metrics to dashboards
- [ ] Test DR database failover procedure

## Prevention

### Proactive Measures
- Implement exponential backoff for retries
- Set up connection pool monitoring
- Regular DR failover testing
- Database performance reviews
- Automated credential rotation testing

## Escalation

- **Primary:** On-call SRE
- **Secondary:** Database Team
- **Cloud Provider:** OCI Support (if infrastructure issue)
- **Escalate to SEV1 if:** All database connections failing

## Related Runbooks
- [SEV1: Payment Outage](sev1-payment-outage.md)
- [Deployment Rollback](deployment-rollback.md)

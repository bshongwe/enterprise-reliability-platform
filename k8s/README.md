# Kubernetes Resource Specifications

## Resource Requests and Limits

### Payments API
```yaml
resources:
  requests:
    cpu: "250m"              # 0.25 CPU cores
    memory: "256Mi"          # 256 mebibytes
    ephemeral-storage: "1Gi" # 1 gibibyte
  limits:
    memory: "512Mi"          # Max 512 MiB
    ephemeral-storage: "2Gi" # Max 2 GiB
```

**Rationale:**
- Lightweight Python FastAPI service
- Stateless HTTP request handling
- Minimal storage for logs

### Ledger Service
```yaml
resources:
  requests:
    cpu: "500m"              # 0.5 CPU cores
    memory: "512Mi"          # 512 mebibytes
    ephemeral-storage: "5Gi" # 5 gibibytes
  limits:
    memory: "1Gi"            # Max 1 GiB
    ephemeral-storage: "10Gi" # Max 10 GiB
```

**Rationale:**
- Database operations (SQLite)
- Higher CPU for write operations
- More storage for database file

## Security

### Service Account
```yaml
automountServiceAccountToken: false
```

**Why:** Services don't need Kubernetes API access. Disabling automount follows least privilege principle and prevents token exposure if pod is compromised.

## Image Tags

### Production
```yaml
image: ghcr.io/bshongwe/payments-api:v1.0.0
```

**v1.0.0** is replaced by CI/CD with commit SHA:
```yaml
image: ghcr.io/bshongwe/payments-api:abc123def456
```

### Canary
```yaml
image: ghcr.io/bshongwe/payments-api:canary
```

Replaced with:
```yaml
image: ghcr.io/bshongwe/payments-api:canary-abc123def456
```

## Adjusting Resources

Monitor actual usage:
```bash
kubectl top pod -l app=payments-api
```

Update based on:
- **Requests:** Set to P50 (median) usage
- **Limits:** Set to P95 usage + 20% buffer

## Quality of Service

Current configuration provides **Burstable** QoS:
- Guaranteed minimum resources (requests)
- Can burst up to limits under load
- Balanced for cost and reliability

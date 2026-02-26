# CI/CD Pipeline - GitOps with GitHub Actions

## Architecture

**GitOps Flow:**
1. GitHub Actions builds and tests code
2. On success, updates Kubernetes manifests in `k8s/`
3. ArgoCD detects manifest changes and syncs to cluster
4. Prometheus monitors SLOs and triggers alerts
5. Auto-rollback via git revert if canary fails

## GitHub Actions Workflows

### 1. CI Pipeline (`.github/workflows/ci.yml`)
- Runs on push/PR to main/develop
- Tests, linting, code quality checks
- **Error budget enforcement**: Blocks deployment if >50% budget burned

### 2. GitOps Deployment (`.github/workflows/canary-deploy.yml`)
- Checks error budget before deployment
- Updates K8s manifests with new image tags
- Commits changes to trigger ArgoCD sync
- Monitors canary for 5 minutes
- **Auto-rollback via git revert** if error rate >1%

## ArgoCD Setup

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Deploy applications
kubectl apply -f k8s/argocd-apps.yaml

# Access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

## Deployment Types

### Canary Deployment
```bash
gh workflow run canary-deploy.yml \
  -f service=payments-api \
  -f deployment_type=canary
```

### Production Deployment
```bash
gh workflow run canary-deploy.yml \
  -f service=payments-api \
  -f deployment_type=production
```

## SLO Enforcement

### Error Budget Gates
```bash
# Check before deployment
python slo/calculate_error_budget.py
```

### Deployment Freeze Conditions
- Payments API: >50% error budget burned in 24h
- Ledger Service: >50% error budget burned in 24h
- Alert label: `action: freeze_deployments`
- GitHub Actions blocks manifest updates

## Local Development

```bash
# Start observability stack
docker-compose up prometheus grafana

# Run services with metrics
export API_KEY="your-key"
uvicorn services.payments_api.main:app --port 8000
uvicorn services.ledger_service.main:app --port 8001

# View metrics
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics

# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

## Kubernetes Manifests

```
k8s/
├── argocd-apps.yaml          # ArgoCD application definitions
├── payments-api/
│   ├── deployment.yaml       # Stable production deployment
│   └── canary.yaml          # Canary deployment (10% traffic)
└── ledger-service/
    └── deployment.yaml       # Stable production deployment
```

## Secrets Management

Required secrets in GitHub:
- `PROMETHEUS_URL`: Prometheus endpoint for SLO checks
- `API_KEY`: Service authentication key

Required secrets in Kubernetes:
```bash
kubectl create secret generic api-secrets \
  --from-literal=api-key=your-secure-key \
  -n production
```

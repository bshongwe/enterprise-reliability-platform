README.md
# Enterprise Hybrid SRE Platform (EHRP)

**Purpose:**  
Simulate a regulated payments and account reliability system across **AWS, Azure, GCP, and Oracle Cloud (OCI)**.  
Designed to demonstrate **enterprise SRE practices**, multi-cloud risk management, observability, and incident response.

---

## 🚀 Overview

EHRP is a **production-grade SRE demonstration** built to mimic real-world corporate bank requirements:

- **Services:** Payments, Ledger, Account, Notification, Analytics
- **Cloud Assignment:**
	- AWS: Core payments & event ingestion
	- Azure: Identity, monitoring, DR
	- GCP: Analytics & long-term metrics
	- Oracle Cloud: Ledger & regulated workloads
- **Observability:** Prometheus, Grafana, Loki/ELK, OpenTelemetry traces
- **Reliability Focus:** SLIs, SLOs, Error Budgets, Canary Deployments, Blue-Green Releases
- **Incident Management:** Runbooks, postmortems, severity model (SEV1–SEV4)
- **Compliance Signals:** RBAC, KMS/Vault secrets, immutable audit logs, network segmentation

---

## 📦 Repo Structure

```
enterprise-hybrid-sre-platform/
├── architecture/
├── services/
├── infra/
│   ├── aws/
│   ├── azure/
│   ├── gcp/
│   ├── oci/
├── observability/
├── slo/
├── runbooks/
├── postmortems/
├── chaos/
├── ci-cd/
├── security/
└── README.md
```

---

## 🔍 Observability & Metrics

- Prometheus: per-cluster metrics
- Grafana: cross-cloud dashboards
- Loki / ELK: centralized logging
- OpenTelemetry: distributed tracing
- Key Metrics:
	- P95 / P99 latency
	- Error rate per service
	- Queue backlogs
	- SLO burn alerts

---

## ⚡ Incident Management

- **SEV1:** Core payment outage
- **SEV2:** Latency breach
- **SEV3:** Partial service degradation
- **SEV4:** Informational / minor

**Example Incident Flow:**
1. Prometheus alerts detect OCI ledger latency
2. AWS circuit breaker activates for payments service
3. Azure DR read replica handles read traffic
4. Incident logged and postmortem generated

---

## 🛠 Deployment & Change Control

- CI/CD pipelines with GitOps approach
- Canary & Blue-Green deployments
- SLO enforcement gates
- Automatic rollback on error budget breach
- Audit-friendly logs for each deployment

---

## 🔐 Security & Compliance

- RBAC across all clouds
- Secrets management via KMS/Vault
- Immutable audit logging
- Network segmentation
- Data residency respecting POPIA

---

## 🧪 Chaos Engineering (Safe)

- Kill payment pods, inject latency, drop network connections
- Only during controlled windows
- Observability first
- Pre-approved runbooks

---

## 📄 Reference Links

- [Runbooks](runbooks/)
- [Postmortems](postmortems/)
- [SLO Definitions](slo/README.md)
- [Architecture Diagrams](architecture/)

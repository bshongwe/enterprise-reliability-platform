# Chaos Engineering

Experiments and scenarios for safe chaos testing (latency, pod kills, network drops).

## Available Experiments

- **pod-kill-payments.yaml** - Kill random payments-api pod every 2 hours
- **network-latency-ledger.yaml** - Inject 100ms latency to ledger-service daily
- **cpu-stress-account.yaml** - Stress CPU on account-service pod

## Running Experiments

```bash
cd chaos
./scripts/run-chaos-experiment.sh pod-kill-payments.yaml
```

## Prerequisites

Install Chaos Mesh:
```bash
kubectl create ns chaos-mesh
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh
```

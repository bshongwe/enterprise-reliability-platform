#!/bin/bash
set -e

NAMESPACE=${NAMESPACE:-production}
EXPERIMENT=$1

if [ -z "$EXPERIMENT" ]; then
  echo "Usage: $0 <experiment-file>"
  echo "Available experiments:"
  ls -1 experiments/*.yaml
  exit 1
fi

echo "🧪 Running chaos experiment: $EXPERIMENT"
kubectl apply -f "experiments/$EXPERIMENT"

echo "⏳ Monitoring experiment..."
EXPERIMENT_NAME=$(basename "$EXPERIMENT" .yaml)
kubectl wait --for=condition=AllInjected -n $NAMESPACE podchaos/$EXPERIMENT_NAME --timeout=60s 2>/dev/null || \
kubectl wait --for=condition=AllInjected -n $NAMESPACE networkchaos/$EXPERIMENT_NAME --timeout=60s 2>/dev/null || \
kubectl wait --for=condition=AllInjected -n $NAMESPACE stresschaos/$EXPERIMENT_NAME --timeout=60s 2>/dev/null

echo "✅ Experiment running. Monitor with:"
echo "   kubectl get podchaos,networkchaos,stresschaos -n $NAMESPACE"
echo "   kubectl logs -l app=<service> -n $NAMESPACE --tail=50"

#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME=${CLUSTER_NAME:-"sre-lab"}

echo "[+] Creando cluster kind: $CLUSTER_NAME"

kind create cluster --name "$CLUSTER_NAME" --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
EOF

kubectl cluster-info --context kind-"$CLUSTER_NAME"
echo "[+] Cluster kind creado"

#!/usr/bin/env bash
set -euo pipefail

ENV_SLUG=${1:-"default"}

echo "[+] Desplegando plataforma para entorno: ${ENV_SLUG}"

cd "$(dirname "$0")/.."

kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: observability
---
apiVersion: v1
kind: Namespace
metadata:
  name: logging
---
apiVersion: v1
kind: Namespace
metadata:
  name: security
---
apiVersion: v1
kind: Namespace
metadata:
  name: argocd
EOF

cd k8s
helmfile -e "${ENV_SLUG}" sync

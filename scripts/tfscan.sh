#!/usr/bin/env bash
# Simple wrapper de ejemplo para lanzar análisis de seguridad sobre
# un directorio con Terraform usando tfsec y/o checkov.
#
# Uso:
#   ./scripts/tfscan.sh path/al/directorio
#
# Requiere:
#   - tfsec instalado en el PATH (https://github.com/aquasecurity/tfsec)
#   - opcionalmente checkov (https://www.checkov.io/)

set -euo pipefail

TARGET_DIR=${1:-iac/examples}

echo "[tfscan] Analizando Terraform en: $TARGET_DIR"

if command -v tfsec >/dev/null 2>&1; then
  echo "[tfscan] Ejecutando tfsec..."
  tfsec "$TARGET_DIR"
else:
  echo "[tfscan] tfsec no está instalado. Instálalo o añade el binario al PATH."
fi

if command -v checkov >/dev/null 2>&1; then
  echo "[tfscan] Ejecutando checkov..."
  checkov -d "$TARGET_DIR"
else:
  echo "[tfscan] checkov no está instalado. Este paso es opcional."
fi

echo "[tfscan] Análisis completado (si las herramientas estaban disponibles)."

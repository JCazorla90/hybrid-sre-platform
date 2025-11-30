# Hybrid SRE Platform

Autor: **Jose Cazorla**

Plataforma de referencia para montar entornos SRE / SecOps híbridos (on-prem + multi-cloud) con:

- Panel web (Django) para gestionar entornos y cuentas cloud.
- Despliegue automatizado de:
  - Prometheus + Grafana
  - Apache SkyWalking (extensible)
  - ELK / OpenSearch
  - Wazuh (extensible)
  - ArgoCD (GitOps)
- Scripts base para conectar con:
  - AWS
  - Azure
  - Google Cloud
  - VMware
  - Proxmox
- Autodiscovery de Kubernetes y cloud (esqueleto en Python).
- Etiquetado de recursos por entorno/proveedor/cuenta para observabilidad.

> ⚠️ Este repositorio es un **esqueleto funcional**: listo para levantar el panel, generar configs base
> y orquestar despliegues, pero tendrás que completar la parte de IaC específica por proveedor (Terraform, etc.).

Repo: https://github.com/JCazorla90/hybrid-sre-platform

## Estructura

```text
backend/          # Django + API + panel web
infra/            # IaC, Kubernetes, Helmfile, scripts por proveedor
docs/             # Demo visual que simula la aplicación (para GitHub Pages)
.github/          # Workflows CI/CD
docker-compose.yml
.env.example
```

## Quickstart (modo local con Docker Compose)

Requisitos:

- Docker y Docker Compose
- (Opcional) kind + kubectl + helm + helmfile para pruebas de despliegue

```bash
git clone https://github.com/JCazorla90/hybrid-sre-platform.git
cd hybrid-sre-platform

cp .env.example .env
docker compose up -d --build

# Panel web:
# http://localhost:8000
```

Una vez dentro del panel:

1. Crea una cuenta cloud (AWS/Azure/GCP/VMware/Proxmox o local).
2. Crea un entorno asociado a esa cuenta (dev / pre / prod / lab…).
3. Lanza un despliegue desde la vista del entorno.

El backend:

- Genera ficheros de configuración para las herramientas (Prometheus, ELK, ArgoCD, etc.).
- Llama a los scripts correspondientes en `infra/` según el proveedor y tipo de entorno.

## Docs / Demo visual

El directorio `docs/` contiene una demo estática que **simula la propia aplicación**:

- Vista de dashboard
- Listado de entornos
- Detalle de entorno y despliegues

Pensada para publicarse en GitHub Pages:

- Settings → Pages → Deploy from branch → `main` → `/docs`.

## CI/CD

En `.github/workflows/` se incluye:

- `backend-ci.yml`: pipeline básico de CI para el backend (checks Django).
- `backend-docker-build.yml`: build y push de imagen Docker del backend a GHCR (plantilla).

## Licencia

Puedes usar este esqueleto como base para tus propios proyectos.

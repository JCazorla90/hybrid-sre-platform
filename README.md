# Hybrid SRE Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Plataforma de referencia para montar un **entorno híbrido SRE / SecOps** (on‑prem + multi‑cloud)
> con foco en **persistencia de datos, resiliencia, observabilidad y seguridad**.

Autor: **Jose Cazorla**

---

## 🔍 Visión general

**Hybrid SRE Platform** es un ejemplo de arquitectura técnica y código base para:

- Gestionar entornos **on‑prem (bare‑metal, VMware/Proxmox)** y **cloud (AWS/Azure/GCP)**.
- Desplegar una **plataforma de observabilidad y seguridad** con:
  - Prometheus + Grafana
  - Apache SkyWalking (APM, trazas, topología)
  - ELK / OpenSearch (logs)
  - Wazuh (HIDS / SIEM ligero)
  - Ceph (almacenamiento distribuido)
- Exponer un **panel web ligero (Django)** para:
  - Gestionar entornos y cuentas cloud.
  - Visualizar paneles de seguridad, herramientas y proyectos de IaC.
- Ofrecer una **demo visual estática (`/docs`)** pensada para GitHub Pages, que simula:
  - Dashboard global de salud.
  - Gestión de entornos y cuentas cloud.
  - Panel de Seguridad (Wazuh / ELK / Grafana / SkyWalking).
  - Panel de Admin tools (pool de herramientas + repos GitHub).
  - Panel de IaC / Terraform (estado de escaneos de seguridad).


---

## 🧱 Componentes principales

### 1. Panel web (Django)

Ruta: `backend/`

- App `platform_app`:
  - Lista de **entornos** (on‑prem, AWS, etc.).
  - Lista de **cuentas cloud**.
  - **Panel de Seguridad**: enlaces configurables a Wazuh, ELK/Kibana, Grafana.
  - **Admin tools**:
    - Pool de herramientas (Mist, StackStorm, Wazuh, SkyWalking, ELK, Grafana, ArgoCD, Ceph, GitHub…).
    - Integración ligera con **GitHub API** para listar repos públicos/privados (si se configura token).
  - **IaC / Terraform**:
    - Vista conceptual para proyectos Terraform.
    - Estado de escaneos de seguridad (Crit/High/Medium).
    - Integración pensada con tfsec / checkov / terrascan.
   
## 🧩 Mapa de servicios e infraestructura (laboratorio)

Este diagrama resume la granularidad de componentes que se modelan o se despliegan
(en demo o en diseño):

| Capa                    | Servicio / herramienta         | Rol principal                                           | Ejemplo de despliegue                        |
|-------------------------|--------------------------------|--------------------------------------------------------|----------------------------------------------|
| Presentación / CMDB     | Django Hybrid SRE Platform     | UI de CMDB + panel SRE/SecOps                         | `backend/`, expuesto como `https://sre.local` |
| Datos CMDB              | DB Django (SQLite / Postgres)  | Inventario de entornos, cuentas, clústeres, IaC       | Contenedor DB / servicio gestionado          |
| Automatización          | StackStorm (diseño)            | Runbooks, remediación, orquestación de IaC            | K8s o VM dedicada                             |
| GitOps / CI             | ArgoCD / GitHub Actions        | Deploy continuo, sync de manifiestos / charts         | `stacks/k8s-single-cluster` + `.github/`     |
| IaC                     | Terraform + Ansible            | Provisión infra (cloud + on-prem) y configuración     | Carpetas `infra/` + `scripts/tfscan.sh`      |
| Seguridad infra         | Wazuh                          | HIDS, FIM, correlación básica                         | Agentes en VMs, nodos K8s, sidecars          |
| Observabilidad métricas | Prometheus + exporters         | Métricas técnicas, SLIs                               | `stacks/docker-compose-full` / Helm          |
| Observabilidad dashboards | Grafana                     | Visores SRE, paneles negocio / ejecutivos             | `stacks/docker-compose-full` / Helm          |
| Logs                    | ELK / OpenSearch + Beats       | Centralización de logs de apps, K8s, infra            | Docker Compose / Helm                        |
| APM / trazas            | Apache SkyWalking              | Trazas, topología de servicios, profiling             | Helm en cluster de observabilidad            |
| Almacenamiento datos    | Ceph (diseño)                  | Volúmenes replicados / object storage on-prem         | Cluster Ceph dedicado                        |
| Infra on-prem           | Bare-metal + VMware/Proxmox    | Hosts físicos, hipervisores, VMs                      | Modelado como “Lab on-prem”                  |
| Infra cloud             | AWS / Azure / GCP              | Cuentas cloud, VPC/VNet, EKS/AKS/GKE, servicios       | Modelado como “Prod AWS”, “Pre Azure”, etc.  |

> En la demo UI (`/docs`) se representa principalmente el nivel **Entorno / Proveedor / Clúster**,
> pero el diseño está pensado para bajar hasta **servicio / recurso concreto** si se extiende el backend.

---
### 2. Demo visual (GitHub Pages)

Ruta: `docs/`

- `index.html` + `css/style.css` + `js/app-sim.js`
- Simula una app SPA con varias vistas:

  - **Dashboard**
  - **Entornos**
  - **Cuentas cloud**
  - **Despliegues**
  - **Seguridad**
    - Wazuh, ELK, Grafana
    - Iframe de demo pública de **Apache SkyWalking**
  - **IaC / Terraform**
    - Proyectos Terraform mock
    - Botón para **simular escaneos** (datos random para la demo)
  - **Admin tools**
    - Pool de herramientas
    - Panel para listar repos GitHub llamando a la API pública

Ideal para enseñar el concepto sin necesidad de levantar todo el backend.

### 3. Stacks de observabilidad y seguridad

Ruta: `stacks/`

- `docker-compose-full/`
  - `docker-compose.yml` con:
    - Prometheus
    - Grafana
    - OpenSearch / Elasticsearch + Kibana (según variante)
    - Exporters básicos
  - Pensado para **entorno de laboratorio**.

- `k8s-single-cluster/`
  - `namespaces.yaml`
  - `helmfile.yaml`
  - `values-*.yaml` para:
    - Prometheus / kube-prometheus-stack
    - Grafana
    - Elasticsearch / Kibana
    - ArgoCD
    - SkyWalking
    - Wazuh
  - Te da un punto de partida para un **cluster de observabilidad único**.

### 4. IaC y scripts

Ruta: `infra/` y `scripts/`

- `infra/k8s/helmfile.yaml`
  - Despliegue centralizado vía Helmfile para el cluster de observabilidad.

- Scripts:
  - `infra/scripts/bootstrap-kind.sh`
    - Crear un cluster **kind** local para pruebas.
  - `infra/scripts/deploy-platform.sh`
    - Ejemplo de flujo para desplegar la plataforma al cluster.
  - `scripts/tfscan.sh`
    - Wrapper de ejemplo para lanzar **tfsec** y **checkov** sobre un directorio de Terraform.
    - Punto de entrada para integrarlo en CI/CD o StackStorm.

---

## 🧬 Flujos de alto nivel

### Flujo 1 – Observabilidad y seguridad

1. **Infraestructura híbrida**:
   - On‑prem (bare‑metal / VMware / Proxmox).
   - Cloud (AWS/Azure/GCP).
2. **Mist** orquesta VMs / nodos / clusters K8s (conceptual, no incluido en el código).
3. En los clusters:
   - Se despliegan:
     - Prometheus + Grafana
     - SkyWalking
     - ELK / OpenSearch
     - Wazuh (agentes / DaemonSet)
4. Logs y métricas:
   - Logs de:
     - Apps, K8s, sistemas, Mist, StackStorm, Wazuh…
   - Métricas de:
     - K8s, nodes, services.
5. El **panel Django** actúa como “single pane of glass”:
   - Dashboards de Seguridad (Wazuh/ELK/Grafana/SkyWalking).
   - Vistas de IaC y Admin tools.

### Flujo 2 – IaC + seguridad (Terraform + tfsec/checkov)

1. Definir infraestructura en Terraform (por proveedor / módulo / entorno).
2. Repos Git en GitHub (o tu SCM favorito).
3. Pipeline CI/CD (GitHub Actions, GitLab CI, etc.):
   - `terraform fmt` / `terraform validate`
   - `tfsec` y/o `checkov`
   - Publicación de resultados:
     - Como artefactos de CI.
     - Como JSON para que los consuma el backend (futuro).
4. El panel **IaC / Terraform**:
   - Muestra estado de proyectos y severidad de findings.
   - Permite simular el flujo en la demo `/docs` con datos mock.

---

## 🗂️ Estructura del repositorio

```text
hybrid-sre-platform/
  README.md
  .env.example            # Variables de entorno base para backend / stacks
  docker-compose.yml      # Compose root (puente hacia stacks/docker-compose-full)
  backend/                # Django + panel web SRE/SecOps
    hybrid_sre/
    platform_app/
    templates/
    requirements.txt
    Dockerfile
  docs/                   # Demo SPA estática (pensada para GitHub Pages)
    index.html
    css/
    js/
  stacks/                 # Stacks de observabilidad / seguridad
    docker-compose-full/
    k8s-single-cluster/
  infra/                  # Infra genérica / scripts k8s
    k8s/
    scripts/
  scripts/                # Scripts utilitarios (tfscan, etc.)
  .github/                # Workflows CI/CD
```

---

## 🚀 Quickstart

### 1. Backend (Django) en local

Requisitos:

- Python 3.10+
- virtualenv (opcional pero recomendado)
- Docker (si quieres levantar también los stacks)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # en Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Migraciones iniciales
python manage.py migrate

# Crear superusuario si lo necesitas
python manage.py createsuperuser

# Lanzar el servidor de desarrollo
python manage.py runserver
```

La app quedará disponible en:

- `http://localhost:8000/`

### 2. Stacks de observabilidad con Docker Compose

```bash
cd stacks/docker-compose-full
docker compose up -d
```

Servicios típicos:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Kibana / Dashboards: `http://localhost:5601` (según stack)
- Otros servicios según el `docker-compose.yml`.

### 3. Demo visual en GitHub Pages

1. Publica la carpeta `docs/`:

   - GitHub → Settings → Pages → Deploy from branch
   - Branch: `main`
   - Folder: `/docs`

2. Accede a la URL que te genere GitHub Pages:

   - Verás la demo SPA con los distintos paneles:
     - Dashboard
     - Entornos
     - Cuentas cloud
     - Despliegues
     - Seguridad
     - IaC / Terraform
     - Admin tools

---

## 🧪 Seguridad y calidad

Aunque este repo es principalmente una **demo de arquitectura**, se han tenido en cuenta buenas prácticas:

- Estilo Python con **black**.
- Se recomienda usar:
  - **bandit** para escanear el código Python.
  - **tfsec / checkov** para los módulos Terraform.
- Separación clara entre:
  - Código de app (`backend/`).
  - Infraestructura (`infra/`, `stacks/`).
  - Demo puramente estática (`docs/`).

Ejemplo de ejecución de `tfscan.sh`:

```bash
./scripts/tfscan.sh path/a/tu/terraform
```

---

## 🧭 Roadmap / ideas futuras

- Persistir en base de datos:

  - Proyectos Terraform y resultados de escaneos.
  - Enlaces por entorno a dashboards reales (Grafana, Kibana, Wazuh, SkyWalking).

- Integración real con:

  - Mist (API).
  - StackStorm (packs para IaC, remediación, etc.).
  - ArgoCD (GitOps para las apps y la propia plataforma).

- Añadir:

  - Soporte multi‑tenant real en el panel web.
  - Modelado de SLOs y SLIs por servicio.

---

## 📄 Licencia

Este proyecto se publica bajo licencia **MIT**.

Consulta el fichero [`LICENSE`](./LICENSE) para más detalles.

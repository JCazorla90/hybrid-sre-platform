# Stack completo en un único cluster Kubernetes

Este stack está pensado para un entorno más **productivo** sobre un único cluster
Kubernetes (on-prem, kind, EKS, AKS, GKE, etc.), desplegando:

- kube-prometheus-stack (Prometheus + Alertmanager + Grafana + exporters)
- Elasticsearch + Kibana (logs)
- ArgoCD (GitOps)
- Apache SkyWalking (APM / trazas) – esqueleto
- Wazuh (seguridad) – esqueleto

Utiliza `helmfile` para orquestar todos los charts.

> ℹ️ Asume que ya existe un StorageClass en el cluster (por ejemplo, Ceph RBD,
> EBS, Azure Disk, etc.). La configuración de Ceph como tal se haría con Rook
> u otra solución y no se incluye aquí para simplificar.

## Requisitos

- kubectl
- helm
- helmfile

Cluster:

- Kubernetes >= 1.26
- StorageClass por defecto configurada

## Uso rápido

```bash
cd stacks/k8s-single-cluster

# Comprobar contexto kubectl
kubectl config current-context

# Crear namespaces base
kubectl apply -f namespaces.yaml

# Desplegar stack
helmfile sync
```

Endpoints típicos (ClusterIP, puedes exponerlos con Ingress/NLB):

- Grafana (desde kube-prometheus-stack)
- Kibana
- ArgoCD
- SkyWalking UI
- Wazuh Dashboard (cuando se complete la integración Helm)

Ajusta valores y versiones según tus necesidades reales.

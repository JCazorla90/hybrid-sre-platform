# Stack local completo (Docker Compose)

Este stack levanta en tu máquina local un entorno de observabilidad + seguridad
con las principales herramientas de la plataforma:

- Elasticsearch + Kibana (logs)
- Prometheus (métricas)
- Grafana (dashboards)
- Apache SkyWalking (APM / trazas)
- Wazuh Manager (seguridad / HIDS)

Está pensado como **entorno de laboratorio** para probar la plataforma Hybrid SRE
sin necesidad de un cluster Kubernetes.

## Requisitos

- Docker y Docker Compose

## Uso

```bash
cd stacks/docker-compose-full
docker compose up -d
```

Servicios expuestos:

- Elasticsearch: http://localhost:9200
- Kibana:       http://localhost:5601
- Prometheus:   http://localhost:9090
- Grafana:      http://localhost:3000 (admin / admin)
- SkyWalking UI: http://localhost:8080
- Wazuh API:    puerto 55000 (por defecto)

Los dashboards de Grafana vienen con datasources preconfigurados para:

- Prometheus
- Elasticsearch

Puedes importar dashboards oficiales o de tu entorno real.

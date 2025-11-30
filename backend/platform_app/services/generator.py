from pathlib import Path
import yaml
from ..models import Environment, CloudProvider

BASE_DIR = Path(__file__).resolve().parents[3]
K8S_DIR = BASE_DIR / "infra" / "k8s"


def _env_labels(env: Environment):
    provider = env.cloud_account.provider if env.cloud_account else CloudProvider.LOCAL
    account_id = env.cloud_account.account_id if env.cloud_account else "local"
    return {
        "environment": env.slug,
        "provider": provider,
        "account_id": account_id,
    }


def generate_environment_configs(env: Environment) -> Path:
    # Genera ficheros de valores para Helm basados en la config del entorno.
    env_dir = K8S_DIR / "environments" / env.slug
    env_dir.mkdir(parents=True, exist_ok=True)

    labels = _env_labels(env)

    if env.enable_prometheus:
        prom_values = {
            "prometheus": {
                "prometheusSpec": {
                    "retention": f"{env.metrics_retention_days}d",
                }
            },
            "global": {
                "labels": labels,
            },
        }
        (env_dir / "values-prometheus.yaml").write_text(
            yaml.safe_dump(prom_values), encoding="utf-8"
        )

    if env.enable_elk:
        es_values = {
            "persistence": {"enabled": True, "size": "50Gi"},
            "labels": labels,
        }
        (env_dir / "values-elasticsearch.yaml").write_text(
            yaml.safe_dump(es_values), encoding="utf-8"
        )

    if env.enable_argocd:
        argocd_values = {
            "server": {
                "extraArgs": ["--insecure"],
            },
            "global": {
                "labels": labels,
            },
        }
        (env_dir / "values-argocd.yaml").write_text(
            yaml.safe_dump(argocd_values), encoding="utf-8"
        )

    return env_dir

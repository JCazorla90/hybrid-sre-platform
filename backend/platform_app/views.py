from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
import requests

from .models import Environment, CloudAccount, DeploymentRun
from .forms import EnvironmentForm, CloudAccountForm
from .services.deployer import deploy_environment


# Endpoints por defecto para el panel de seguridad.
# En un despliegue real se pueden sobreescribir en settings.SECURITY_DASHBOARD_ENDPOINTS
DEFAULT_SECURITY_DASHBOARD_ENDPOINTS = {
    "grafana": {
        "key": "grafana",
        "name": "Grafana (métricas)",
        "url": "http://localhost:3000",
        "description": "Visualización de métricas de Prometheus y dashboards SRE.",
    },
    "elk": {
        "key": "elk",
        "name": "Kibana / OpenSearch Dashboards (logs)",
        "url": "http://localhost:5601",
        "description": "Exploración centralizada de logs de aplicaciones, K8s e infra.",
    },
    "wazuh": {
        "key": "wazuh",
        "name": "Wazuh (seguridad / HIDS)",
        "url": "http://localhost:55000",
        "description": "Alertas de seguridad, integridad de ficheros y correlación básica.",
    },
}


TOOLS_POOL = [
    {
        "key": "mist",
        "name": "Mist",
        "description": "Single pane multi-cloud (bare-metal, VMware/Proxmox, AWS, K8s).",
        "category": "orchestrator",
        "doc_url": "https://mist.io/",
    },
    {
        "key": "stackstorm",
        "name": "StackStorm",
        "description": "Automatización basada en eventos, runbooks, integración con Mist / Wazuh / ELK.",
        "category": "automation",
        "doc_url": "https://stackstorm.com/",
    },
    {
        "key": "wazuh",
        "name": "Wazuh",
        "description": "Plataforma de seguridad / HIDS, FIM y correlación de amenazas.",
        "category": "security",
        "doc_url": "https://wazuh.com/",
    },
    {
        "key": "skywalking",
        "name": "Apache SkyWalking",
        "description": "APM, trazas distribuidas, topología de servicios y profiling.",
        "category": "observability",
        "doc_url": "https://skywalking.apache.org/",
    },
    {
        "key": "elk",
        "name": "ELK / OpenSearch",
        "description": "Stack de logs centralizados para aplicaciones, infra y K8s.",
        "category": "observability",
        "doc_url": "https://opensearch.org/",
    },
    {
        "key": "grafana",
        "name": "Grafana",
        "description": "Visualización de métricas y SLIs/SLOs, paneles ejecutivos.",
        "category": "observability",
        "doc_url": "https://grafana.com/",
    },
    {
        "key": "argocd",
        "name": "ArgoCD",
        "description": "GitOps para desplegar y sincronizar la plataforma híbrida.",
        "category": "gitops",
        "doc_url": "https://argo-cd.readthedocs.io/",
    },
    {
        "key": "ceph",
        "name": "Ceph",
        "description": "Almacenamiento distribuido para datos y volúmenes persistentes.",
        "category": "storage",
        "doc_url": "https://ceph.io/",
    },
    {
        "key": "github",
        "name": "GitHub",
        "description": "Código fuente, IaC, pipelines CI/CD y colaboración.",
        "category": "scm",
        "doc_url": "https://github.com/",
    },
]


class HomeView(View):
    def get(self, request):
        envs = Environment.objects.all().order_by("-created_at")[:5]
        accounts = CloudAccount.objects.all().order_by("provider", "name")
        deployments = (
            DeploymentRun.objects.select_related("environment")
            .all()
            .order_by("-created_at")[:5]
        )
        return render(
            request,
            "platform_app/home.html",
            {
                "envs": envs,
                "accounts": accounts,
                "deployments": deployments,
            },
        )


class CloudAccountListView(View):
    def get(self, request):
        accounts = CloudAccount.objects.all().order_by("provider", "name")
        return render(
            request,
            "platform_app/cloudaccount_list.html",
            {"accounts": accounts},
        )


class CloudAccountCreateView(View):
    def get(self, request):
        form = CloudAccountForm()
        return render(
            request,
            "platform_app/cloudaccount_form.html",
            {"form": form},
        )

    def post(self, request):
        form = CloudAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("cloudaccount_list")
        return render(
            request,
            "platform_app/cloudaccount_form.html",
            {"form": form},
        )


class EnvironmentListView(View):
    def get(self, request):
        envs = (
            Environment.objects.select_related("cloud_account")
            .all()
            .order_by("slug")
        )
        return render(
            request,
            "platform_app/environment_list.html",
            {"envs": envs},
        )


class EnvironmentCreateView(View):
    def get(self, request):
        form = EnvironmentForm()
        return render(
            request,
            "platform_app/environment_form.html",
            {"form": form},
        )

    def post(self, request):
        form = EnvironmentForm(request.POST)
        if form.is_valid():
            env = form.save()
            return redirect("env_detail", slug=env.slug)
        return render(
            request,
            "platform_app/environment_form.html",
            {"form": form},
        )


class EnvironmentDetailView(View):
    def get(self, request, slug):
        env = get_object_or_404(Environment, slug=slug)
        deployments = (
            DeploymentRun.objects.filter(environment=env)
            .order_by("-created_at")[:15]
        )
        return render(
            request,
            "platform_app/environment_detail.html",
            {"env": env, "deployments": deployments},
        )


class EnvironmentDeployView(View):
    def post(self, request, slug):
        env = get_object_or_404(Environment, slug=slug)
        deploy = DeploymentRun.objects.create(environment=env)
        # En un entorno productivo esto debería ir a una cola (Celery, RQ, etc.)
        deploy_environment(deploy)
        return redirect("env_detail", slug=env.slug)


class SecurityPanelView(View):
    """Panel ligero donde centralizar enlaces hacia Wazuh, ELK/Kibana y Grafana."""

    def get(self, request):
        endpoints = getattr(
            settings,
            "SECURITY_DASHBOARD_ENDPOINTS",
            DEFAULT_SECURITY_DASHBOARD_ENDPOINTS,
        )
        # Normalizamos a lista para simplificar la plantilla
        endpoints_list = []
        for key, cfg in endpoints.items():
            cfg = dict(cfg)
            cfg.setdefault("key", key)
            endpoints_list.append(cfg)

        return render(
            request,
            "platform_app/security_panel.html",
            {"endpoints": endpoints_list},
        )


class AdminToolsView(View):
    """Panel de herramientas + integración ligera con GitHub para listar repos."""

    def get(self, request):
        github_user = request.GET.get("github_user") or getattr(
            settings, "DEFAULT_GITHUB_USER", "JCazorla90"
        )
        github_repos = []
        github_error = None

        if github_user:
            try:
                headers = {
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "hybrid-sre-platform-demo",
                }
                token = getattr(settings, "GITHUB_API_TOKEN", None)
                if token:
                    headers["Authorization"] = f"Bearer {token}"

                resp = requests.get(
                    f"https://api.github.com/users/{github_user}/repos",
                    params={"sort": "updated", "per_page": 10},
                    headers=headers,
                    timeout=5,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list):
                        for item in data:
                            github_repos.append(
                                {
                                    "name": item.get("name"),
                                    "full_name": item.get("full_name"),
                                    "html_url": item.get("html_url"),
                                    "description": item.get("description"),
                                }
                            )
                else:
                    github_error = (
                        f"No se pudo obtener la lista de repos (HTTP {resp.status_code}). "
                        "Puede deberse a límites de la API pública o a un usuario inexistente."
                    )
            except Exception:
                github_error = (
                    "Error al conectar con la API de GitHub. "
                    "Revisa la conectividad de red o configura GITHUB_API_TOKEN."
                )

        context = {
            "tools": TOOLS_POOL,
            "github_user": github_user,
            "github_repos": github_repos,
            "github_error": github_error,
        }
        return render(request, "platform_app/admin_tools.html", context)



class IaCPanelView(View):
    """Panel conceptual para gestionar Terraform e integrar análisis de seguridad."""

    def get(self, request):
        # En esta demo simplemente devolvemos datos estáticos.
        # En una versión avanzada, aquí podrías:
        # - Registrar proyectos Terraform con su repo, ruta y entorno.
        # - Lanzar escaneos con tfsec / checkov / terrascan.
        # - Mostrar resultados por entorno / severidad / proveedor.
        terraform_projects = [
            {
                "name": "core-networking-prod",
                "provider": "AWS",
                "env": "prod",
                "last_scan_status": "passed",
                "critical": 0,
                "high": 1,
                "medium": 3,
            },
            {
                "name": "eks-platform-dev",
                "provider": "AWS",
                "env": "dev",
                "last_scan_status": "warnings",
                "critical": 0,
                "high": 2,
                "medium": 5,
            },
            {
                "name": "onprem-ceph-cluster",
                "provider": "on-prem",
                "env": "infra",
                "last_scan_status": "failed",
                "critical": 2,
                "high": 4,
                "medium": 7,
            },
        ]

        tools = [
            "tfsec",
            "checkov",
            "terrascan",
        ]

        return render(
            request,
            "platform_app/iac_panel.html",
            {
                "terraform_projects": terraform_projects,
                "security_tools": tools,
            },
        )

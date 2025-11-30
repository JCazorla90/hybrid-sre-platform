from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

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

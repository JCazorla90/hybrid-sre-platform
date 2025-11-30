from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Environment, CloudAccount, DeploymentRun
from .forms import EnvironmentForm, CloudAccountForm
from .services.deployer import deploy_environment


class HomeView(View):
    def get(self, request):
        envs = Environment.objects.all().order_by("-created_at")[:5]
        accounts = CloudAccount.objects.all().order_by("provider", "name")
        deployments = DeploymentRun.objects.select_related("environment").order_by("-created_at")[:5]
        return render(
            request,
            "platform_app/home.html",
            {"envs": envs, "accounts": accounts, "deployments": deployments},
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
        return render(request, "platform_app/cloudaccount_form.html", {"form": form})

    def post(self, request):
        form = CloudAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("cloudaccount_list")
        return render(request, "platform_app/cloudaccount_form.html", {"form": form})


class EnvironmentListView(View):
    def get(self, request):
        envs = Environment.objects.select_related("cloud_account").order_by(
            "-created_at"
        )
        return render(
            request, "platform_app/environment_list.html", {"envs": envs}
        )


class EnvironmentCreateView(View):
    def get(self, request):
        form = EnvironmentForm()
        return render(request, "platform_app/environment_form.html", {"form": form})

    def post(self, request):
        form = EnvironmentForm(request.POST)
        if form.is_valid():
            env = form.save()
            return redirect("env_detail", slug=env.slug)
        return render(request, "platform_app/environment_form.html", {"form": form})


class EnvironmentDetailView(View):
    def get(self, request, slug):
        env = get_object_or_404(Environment, slug=slug)
        deployments = env.deployments.order_by("-created_at")
        return render(
            request,
            "platform_app/environment_detail.html",
            {"env": env, "deployments": deployments},
        )


class EnvironmentDeployView(View):
    def post(self, request, slug):
        env = get_object_or_404(Environment, slug=slug)
        deploy = DeploymentRun.objects.create(environment=env)
        # Sin colas de background para simplificar (en producción -> Celery)
        deploy_environment(deploy)
        return redirect("env_detail", slug=env.slug)

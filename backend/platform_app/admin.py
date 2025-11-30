from django.contrib import admin
from .models import CloudAccount, Environment, DeploymentRun


@admin.register(CloudAccount)
class CloudAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "account_id", "default_region", "created_at")
    list_filter = ("provider",)
    search_fields = ("name", "account_id")


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "cluster_type",
        "cloud_account",
        "enable_prometheus",
        "enable_elk",
        "enable_skywalking",
        "enable_wazuh",
        "created_at",
    )
    list_filter = ("cluster_type", "enable_prometheus", "enable_elk")
    search_fields = ("name", "slug")


@admin.register(DeploymentRun)
class DeploymentRunAdmin(admin.ModelAdmin):
    list_display = ("environment", "status", "created_at", "started_at", "finished_at")
    list_filter = ("status",)
    readonly_fields = ("log",)

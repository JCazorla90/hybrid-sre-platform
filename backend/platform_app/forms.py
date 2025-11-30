from django import forms
from .models import Environment, CloudAccount


class CloudAccountForm(forms.ModelForm):
    class Meta:
        model = CloudAccount
        fields = [
            "name",
            "provider",
            "account_id",
            "credential_ref",
            "default_region",
        ]


class EnvironmentForm(forms.ModelForm):
    class Meta:
        model = Environment
        fields = [
            "name",
            "slug",
            "cluster_type",
            "cloud_account",
            "kubernetes_context",
            "enable_ceph",
            "enable_wazuh",
            "enable_elk",
            "enable_skywalking",
            "enable_prometheus",
            "enable_argocd",
            "enable_autodiscovery_k8s",
            "enable_autodiscovery_cloud",
            "log_retention_days",
            "metrics_retention_days",
        ]

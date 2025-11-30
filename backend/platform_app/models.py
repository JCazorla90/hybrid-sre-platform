from django.db import models


class CloudProvider(models.TextChoices):
    AWS = "aws", "AWS"
    AZURE = "azure", "Azure"
    GCP = "gcp", "Google Cloud"
    VMWARE = "vmware", "VMware vSphere"
    PROXMOX = "proxmox", "Proxmox"
    LOCAL = "local", "Local / On-Prem"


class CloudAccount(models.Model):
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=20, choices=CloudProvider.choices)
    account_id = models.CharField(
        max_length=128,
        help_text="ID cuenta/proyecto/subscription (Account ID, Subscription ID, Project ID...).",
    )
    credential_ref = models.CharField(
        max_length=200,
        help_text="Referencia a credenciales: nombre de perfil, service principal, vault path, etc.",
    )
    default_region = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cuenta cloud"
        verbose_name_plural = "Cuentas cloud"

    def __str__(self):
        return f"{self.get_provider_display()} - {self.name}"


class ClusterType(models.TextChoices):
    K8S = "k8s", "Cluster K8s existente"
    KIND = "kind", "Kubernetes local (kind)"
    MANAGED = "managed", "K8s gestionado (EKS/AKS/GKE)"
    VM = "vm", "Solo VMs (sin K8s)"


class Environment(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    cluster_type = models.CharField(
        max_length=20,
        choices=ClusterType.choices,
        default=ClusterType.K8S,
    )
    cloud_account = models.ForeignKey(
        CloudAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="environments",
    )

    kubernetes_context = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nombre de contexto kubeconfig para clusters existentes.",
    )

    enable_ceph = models.BooleanField(default=False)
    enable_wazuh = models.BooleanField(default=True)
    enable_elk = models.BooleanField(default=True)
    enable_skywalking = models.BooleanField(default=True)
    enable_prometheus = models.BooleanField(default=True)
    enable_argocd = models.BooleanField(default=True)
    enable_autodiscovery_k8s = models.BooleanField(default=True)
    enable_autodiscovery_cloud = models.BooleanField(default=False)

    log_retention_days = models.PositiveIntegerField(default=7)
    metrics_retention_days = models.PositiveIntegerField(default=15)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entorno"
        verbose_name_plural = "Entornos"

    def __str__(self):
        provider = self.cloud_account.provider if self.cloud_account else "local"
        return f"{self.name} ({provider})"


class DeploymentRunStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    RUNNING = "running", "En ejecución"
    SUCCESS = "success", "Éxito"
    FAILED = "failed", "Fallo"


class DeploymentRun(models.Model):
    environment = models.ForeignKey(
        Environment, on_delete=models.CASCADE, related_name="deployments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=DeploymentRunStatus.choices,
        default=DeploymentRunStatus.PENDING,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    log = models.TextField(blank=True)

    class Meta:
        verbose_name = "Ejecución de despliegue"
        verbose_name_plural = "Ejecuciones de despliegue"

    def __str__(self):
        return f"Deploy {self.id} - {self.environment.slug} - {self.status}"

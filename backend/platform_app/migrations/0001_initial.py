from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="CloudAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("provider", models.CharField(choices=[("aws", "AWS"), ("azure", "Azure"), ("gcp", "Google Cloud"), ("vmware", "VMware vSphere"), ("proxmox", "Proxmox"), ("local", "Local / On-Prem")], max_length=20)),
                ("account_id", models.CharField(help_text="ID cuenta/proyecto/subscription (Account ID, Subscription ID, Project ID...).", max_length=128)),
                ("credential_ref", models.CharField(help_text="Referencia a credenciales: nombre de perfil, service principal, vault path, etc.", max_length=200)),
                ("default_region", models.CharField(blank=True, max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Cuenta cloud",
                "verbose_name_plural": "Cuentas cloud",
            },
        ),
        migrations.CreateModel(
            name="Environment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(unique=True)),
                ("cluster_type", models.CharField(choices=[("k8s", "Cluster K8s existente"), ("kind", "Kubernetes local (kind)"), ("managed", "K8s gestionado (EKS/AKS/GKE)"), ("vm", "Solo VMs (sin K8s)")], default="k8s", max_length=20)),
                ("kubernetes_context", models.CharField(blank=True, help_text="Nombre de contexto kubeconfig para clusters existentes.", max_length=100)),
                ("enable_ceph", models.BooleanField(default=False)),
                ("enable_wazuh", models.BooleanField(default=True)),
                ("enable_elk", models.BooleanField(default=True)),
                ("enable_skywalking", models.BooleanField(default=True)),
                ("enable_prometheus", models.BooleanField(default=True)),
                ("enable_argocd", models.BooleanField(default=True)),
                ("enable_autodiscovery_k8s", models.BooleanField(default=True)),
                ("enable_autodiscovery_cloud", models.BooleanField(default=False)),
                ("log_retention_days", models.PositiveIntegerField(default=7)),
                ("metrics_retention_days", models.PositiveIntegerField(default=15)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cloud_account", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="environments", to="platform_app.cloudaccount")),
            ],
            options={
                "verbose_name": "Entorno",
                "verbose_name_plural": "Entornos",
            },
        ),
        migrations.CreateModel(
            name="DeploymentRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("pending", "Pendiente"), ("running", "En ejecución"), ("success", "Éxito"), ("failed", "Fallo")], default="pending", max_length=20)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("log", models.TextField(blank=True)),
                ("environment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="deployments", to="platform_app.environment")),
            ],
            options={
                "verbose_name": "Ejecución de despliegue",
                "verbose_name_plural": "Ejecuciones de despliegue",
            },
        ),
    ]

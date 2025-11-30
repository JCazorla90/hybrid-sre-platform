import subprocess
from pathlib import Path
from django.utils import timezone
from ..models import DeploymentRunStatus, CloudProvider
from .generator import generate_environment_configs

BASE_DIR = Path(__file__).resolve().parents[3]
INFRA_DIR = BASE_DIR / "infra"
K8S_DIR = INFRA_DIR / "k8s"


def run_command(cmd, cwd=None):
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    output_lines = []
    for line in process.stdout:
        output_lines.append(line)
    process.wait()
    return process.returncode, "".join(output_lines)


def deploy_environment(deploy_run):
    env = deploy_run.environment
    deploy_run.status = DeploymentRunStatus.RUNNING
    deploy_run.started_at = timezone.now()
    deploy_run.save()

    logs = []

    env_dir = generate_environment_configs(env)
    logs.append(f"[+] Configs generadas en {env_dir}\n")

    account = env.cloud_account
    provider = account.provider if account else CloudProvider.LOCAL

    if provider in [CloudProvider.AWS, CloudProvider.AZURE, CloudProvider.GCP]:
        logs.append(f"[+] Despliegue en cloud provider: {provider}\n")
        script_dir = INFRA_DIR / "scripts" / "providers" / provider
        deploy_sh = script_dir / "deploy.sh"
        cmd = [
            str(deploy_sh),
            env.slug,
            account.account_id,
            account.credential_ref,
            account.default_region or "eu-west-1",
        ]
        rc, out = run_command(cmd, cwd=str(INFRA_DIR))
        logs.append(out)
        if rc != 0:
            deploy_run.status = DeploymentRunStatus.FAILED
            deploy_run.finished_at = timezone.now()
            deploy_run.log = "".join(logs)
            deploy_run.save()
            return deploy_run

    elif provider in [CloudProvider.VMWARE, CloudProvider.PROXMOX]:
        logs.append(f"[+] Despliegue sobre hypervisor: {provider}\n")
        script_dir = INFRA_DIR / "scripts" / "providers" / provider
        deploy_sh = script_dir / "deploy.sh"
        cmd = [str(deploy_sh), env.slug, account.account_id, account.credential_ref]
        rc, out = run_command(cmd, cwd=str(INFRA_DIR))
        logs.append(out)
        if rc != 0:
            deploy_run.status = DeploymentRunStatus.FAILED
            deploy_run.finished_at = timezone.now()
            deploy_run.log = "".join(logs)
            deploy_run.save()
            return deploy_run

    else:
        logs.append("[+] Despliegue local (kind / kubecontext existente)\n")
        if env.cluster_type == "kind":
            rc, out = run_command(["./scripts/bootstrap-kind.sh"], cwd=str(INFRA_DIR))
            logs.append(out)
            if rc != 0:
                deploy_run.status = DeploymentRunStatus.FAILED
                deploy_run.finished_at = timezone.now()
                deploy_run.log = "".join(logs)
                deploy_run.save()
                return deploy_run

        rc, out = run_command(
            ["helmfile", "-e", env.slug, "sync"], cwd=str(K8S_DIR)
        )
        logs.append(out)
        if rc != 0:
            deploy_run.status = DeploymentRunStatus.FAILED
            deploy_run.finished_at = timezone.now()
            deploy_run.log = "".join(logs)
            deploy_run.save()
            return deploy_run

    deploy_run.status = DeploymentRunStatus.SUCCESS
    deploy_run.finished_at = timezone.now()
    deploy_run.log = "".join(logs)
    deploy_run.save()
    return deploy_run

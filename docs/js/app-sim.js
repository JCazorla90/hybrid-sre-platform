const envData = {
  "prod-aws": {
    name: "Producción AWS",
    slug: "prod-aws",
    provider: "AWS",
    cluster: "EKS · 3 nodos por AZ · multi-AZ",
    components: ["Prometheus", "Grafana", "ELK", "SkyWalking", "Wazuh", "ArgoCD"],
    deployments: [
      "2025-11-30 10:05 · Éxito · helmfile sync · Prometheus/Grafana/ELK up",
      "2025-11-29 16:22 · Éxito · upgrade SkyWalking + agentes",
    ]
  },
  "pre-azure": {
    name: "Preproducción Azure",
    slug: "pre-azure",
    provider: "Azure",
    cluster: "AKS · 2 nodepools (system + workload)",
    components: ["Prometheus", "Grafana", "ELK", "ArgoCD"],
    deployments: [
      "2025-11-29 18:23 · Éxito · AKS actualizado",
      "2025-11-28 11:05 · Éxito · despliegue inicial plataforma",
    ]
  },
  "dev-gcp": {
    name: "Desarrollo GCP",
    slug: "dev-gcp",
    provider: "GCP",
    cluster: "GKE · nodo pequeño · autoscaling",
    components: ["Prometheus", "Grafana"],
    deployments: [
      "2025-11-28 19:40 · Éxito · demo SRE lab",
    ]
  },
  "lab-kind": {
    name: "Lab on-prem",
    slug: "lab-kind",
    provider: "Local",
    cluster: "kind · 1 control-plane + 2 workers",
    components: ["Prometheus", "Grafana", "ELK"],
    deployments: [
      "2025-11-29 12:11 · FALLO · kind cluster no accesible",
      "2025-11-28 09:10 · Éxito · despliegue inicial",
    ]
  }
};

function switchView(viewId) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById("view-" + viewId).classList.add("active");

  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.view === viewId);
  });
}

function bindNav() {
  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.addEventListener("click", () => {
      switchView(btn.dataset.view);
    });
  });
}

function showEnvDetail(slug) {
  const data = envData[slug];
  const container = document.getElementById("env-detail-sim");
  if (!data || !container) return;

  container.querySelector(".env-detail-body").classList.remove("hidden");
  container.querySelector("#env-name").textContent = data.name;
  container.querySelector("#env-slug").textContent = data.slug;
  container.querySelector("#env-provider").textContent = data.provider;
  container.querySelector("#env-cluster").textContent = data.cluster;
  container.querySelector("#env-components").textContent = data.components.join(", ");

  const ul = container.querySelector("#env-deployments");
  ul.innerHTML = "";
  data.deployments.forEach(d => {
    const li = document.createElement("li");
    li.textContent = d;
    ul.appendChild(li);
  });
}

function bindEnvLinks() {
  document.querySelectorAll(".link-env").forEach(a => {
    a.addEventListener("click", e => {
      e.preventDefault();
      switchView("environments");
      const slug = a.dataset.env;
      showEnvDetail(slug);
    });
  });

  document.querySelectorAll(".btn-small[data-env]").forEach(btn => {
    btn.addEventListener("click", () => {
      showEnvDetail(btn.dataset.env);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  bindNav();
  bindEnvLinks();
});

// Datos simulados para la demo
const demoState = {
  envs: [
    {
      slug: "prod-aws",
      name: "Producción AWS",
      provider: "AWS",
      cluster: "EKS · 3 nodos por AZ · multi-AZ",
      retentionDays: 30,
      components: ["Prometheus", "Grafana", "ELK", "SkyWalking", "Wazuh", "ArgoCD"],
      status: "ok",
      lastDeploy: {
        start: "2025-11-30 10:02",
        end: "2025-11-30 10:05",
        summary: "[+] Configs generadas · helmfile sync OK",
        status: "success",
      },
      deployments: [
        "2025-11-30 10:05 · Éxito · helmfile sync OK",
        "2025-11-29 16:22 · Éxito · upgrade SkyWalking + agentes",
      ],
    },
    {
      slug: "pre-azure",
      name: "Preproducción Azure",
      provider: "Azure",
      cluster: "AKS · 2 nodepools (system + workload)",
      retentionDays: 15,
      components: ["Prometheus", "Grafana", "ELK", "ArgoCD"],
      status: "ok",
      lastDeploy: {
        start: "2025-11-29 18:20",
        end: "2025-11-29 18:23",
        summary: "AKS actualizado · Prometheus/Grafana/ELK up",
        status: "success",
      },
      deployments: [
        "2025-11-29 18:23 · Éxito · AKS actualizado",
        "2025-11-28 11:05 · Éxito · despliegue inicial plataforma",
      ],
    },
    {
      slug: "dev-gcp",
      name: "Desarrollo GCP",
      provider: "GCP",
      cluster: "GKE · nodo pequeño · autoscaling",
      retentionDays: 7,
      components: ["Prometheus", "Grafana"],
      status: "ok",
      lastDeploy: {
        start: "2025-11-28 19:35",
        end: "2025-11-28 19:40",
        summary: "Demo SRE lab",
        status: "success",
      },
      deployments: ["2025-11-28 19:40 · Éxito · demo SRE lab"],
    },
    {
      slug: "lab-kind",
      name: "Lab on-prem",
      provider: "Local",
      cluster: "kind · 1 control-plane + 2 workers",
      retentionDays: 7,
      components: ["Prometheus", "Grafana", "ELK"],
      status: "warn",
      lastDeploy: {
        start: "2025-11-29 12:10",
        end: "2025-11-29 12:11",
        summary: "kind cluster no accesible · timeout helmfile",
        status: "failed",
      },
      deployments: [
        "2025-11-29 12:11 · FALLO · kind cluster no accesible",
        "2025-11-28 09:10 · Éxito · despliegue inicial",
      ],
    },
  ],
  accounts: [
    { name: "aws-prod", provider: "AWS", id: "123456789012", region: "eu-west-1" },
    {
      name: "azure-main",
      provider: "Azure",
      id: "xxxx-azure-subscription-id",
      region: "westeurope",
    },
    {
      name: "gcp-dev",
      provider: "GCP",
      id: "project-id-dev",
      region: "europe-west1",
    },
  ],
  deployments: [
    {
      envSlug: "prod-aws",
      status: "success",
      start: "2025-11-30 10:02",
      end: "2025-11-30 10:05",
      summary: "[+] Configs generadas · helmfile sync OK",
    },
    {
      envSlug: "pre-azure",
      status: "success",
      start: "2025-11-29 18:20",
      end: "2025-11-29 18:23",
      summary: "AKS actualizado · Prometheus/Grafana/ELK up",
    },
    {
      envSlug: "lab-kind",
      status: "failed",
      start: "2025-11-29 12:10",
      end: "2025-11-29 12:11",
      summary: "kind cluster no accesible · timeout helmfile",
    },
  ],
  filters: {
    provider: "all",
    envSearch: "",
    accountsProvider: "all",
  },
  ui: {
    highContrast: false,
  },
  currentEnvSlug: null,
};

// --- Utilidades ---
function $(selector) {
  return document.querySelector(selector);
}
function $all(selector) {
  return Array.from(document.querySelectorAll(selector));
}

function toast(message, type = "ok") {
  const container = $("#toast-container");
  if (!container) return;
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  const icon = document.createElement("div");
  icon.className = "toast-icon";
  icon.textContent = type === "ok" ? "✅" : "⚠️";
  const text = document.createElement("div");
  text.textContent = message;
  el.appendChild(icon);
  el.appendChild(text);
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transform = "translateY(4px)";
  }, 2600);
  setTimeout(() => {
    el.remove();
  }, 3200);
}

function providerLabel(provider) {
  if (provider === "Local") return "On‑prem / Local";
  return provider;
}

function statusPill(status) {
  if (status === "ok" || status === "success") return '<span class="pill pill-ok">Healthy</span>';
  if (status === "failed" || status === "error") return '<span class="pill pill-error">Error</span>';
  return '<span class="pill pill-warn">Advertencia</span>';
}

// --- Navegación ---
function switchView(viewId) {
  $all(".view").forEach((v) => v.classList.remove("active"));
  const view = document.getElementById("view-" + viewId);
  if (view) view.classList.add("active");

  $all(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === viewId);
  });
}

function bindNav() {
  $all(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      switchView(btn.dataset.view);
    });
  });
}

// --- Render: Dashboard ---
function renderDashboardSelects() {
  const envSelect = $("#dashboard-env-select");
  const providerSelect = $("#dashboard-provider-select");
  if (!envSelect || !providerSelect) return;

  envSelect.innerHTML = "";
  const allOpt = document.createElement("option");
  allOpt.value = "";
  allOpt.textContent = "Todos";
  envSelect.appendChild(allOpt);

  demoState.envs.forEach((env) => {
    const opt = document.createElement("option");
    opt.value = env.slug;
    opt.textContent = `${env.name} (${env.provider})`;
    envSelect.appendChild(opt);
  });

  providerSelect.value = demoState.filters.provider || "all";
}

function renderDashboardSummary() {
  const filteredEnvs = demoState.envs.filter((e) => {
    if (demoState.filters.provider === "all") return true;
    return e.provider === demoState.filters.provider;
  });

  const cardEnv = $("#card-env-count .mini-value");
  const cardCloud = $("#card-cloud-count .mini-value");
  const cardLast = $("#card-last-deploy .mini-value");
  const cardLastDesc = $("#card-last-deploy .mini-desc");

  if (cardEnv) cardEnv.textContent = filteredEnvs.length.toString();
  if (cardCloud) cardCloud.textContent = demoState.accounts.length.toString();

  const last = demoState.deployments[0];
  if (last && cardLast && cardLastDesc) {
    cardLast.textContent = last.status === "success" ? "Éxito" : "Atención";
    cardLast.classList.remove("ok", "warn");
    cardLast.classList.add(last.status === "success" ? "ok" : "warn");
    cardLastDesc.textContent = `${last.envSlug} · ${last.end}`;
  } else if (cardLast && cardLastDesc) {
    cardLast.textContent = "–";
    cardLastDesc.textContent = "Sin despliegues aún";
  }
}

function renderDashboardTable() {
  const tbody = $("#dashboard-env-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const selectedSlug = $("#dashboard-env-select")?.value || "";
  const providerFilter = demoState.filters.provider;

  demoState.envs.forEach((env) => {
    if (providerFilter !== "all" && env.provider !== providerFilter) return;
    if (selectedSlug && env.slug !== selectedSlug) return;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><a href="#" data-env="${env.slug}" class="link-env-detail">${env.name}</a></td>
      <td>${providerLabel(env.provider)}</td>
      <td>${env.cluster}</td>
      <td>${statusPill(env.status)}</td>
      <td>${env.lastDeploy ? env.lastDeploy.end : "-"}</td>
    `;
    tbody.appendChild(tr);
  });

  // bind links
  $all(".link-env-detail").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const slug = link.getAttribute("data-env");
      if (!slug) return;
      demoState.currentEnvSlug = slug;
      switchView("environments");
      renderEnvironments();
      showEnvDetail(slug);
    });
  });
}

function renderDashboard() {
  renderDashboardSelects();
  renderDashboardSummary();
  renderDashboardTable();
}

// --- Render: Entornos ---
function renderEnvTable() {
  const tbody = $("#env-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  const providerFilter = demoState.filters.provider;
  const search = demoState.filters.envSearch.toLowerCase();

  demoState.envs.forEach((env) => {
    if (providerFilter !== "all" && env.provider !== providerFilter) return;
    if (search && !`${env.name} ${env.slug}`.toLowerCase().includes(search)) return;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><a href="#" data-env="${env.slug}" class="link-env">${env.name}</a></td>
      <td>${env.slug}</td>
      <td>${providerLabel(env.provider)}</td>
      <td>${env.cluster}</td>
      <td>${env.retentionDays} días</td>
      <td><button class="btn-primary btn-small" data-env="${env.slug}">Ver detalle</button></td>
    `;
    tbody.appendChild(tr);
  });

  // enlaces y botones
  $all(".link-env").forEach((a) => {
    a.addEventListener("click", (e) => {
      e.preventDefault();
      const slug = a.getAttribute("data-env");
      if (!slug) return;
      demoState.currentEnvSlug = slug;
      showEnvDetail(slug);
    });
  });
  $all("#env-table-body button[data-env]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const slug = btn.getAttribute("data-env");
      if (!slug) return;
      demoState.currentEnvSlug = slug;
      showEnvDetail(slug);
    });
  });
}

function showEnvDetail(slug) {
  const env = demoState.envs.find((e) => e.slug === slug);
  const card = $("#env-detail-card");
  if (!env || !card) return;

  const emptyText = $("#env-detail-empty");
  const body = card.querySelector(".env-detail-body");
  if (!body) return;

  emptyText && (emptyText.style.display = "none");
  body.classList.remove("hidden");

  $("#env-name").textContent = env.name;
  $("#env-slug").textContent = env.slug;
  $("#env-provider").textContent = providerLabel(env.provider);
  $("#env-cluster").textContent = env.cluster;
  $("#env-components").textContent = env.components.join(", ");
  $("#env-retention").textContent = `${env.retentionDays} días logs / 15 días métricas (demo)`;

  const ul = $("#env-deployments");
  ul.innerHTML = "";
  env.deployments.forEach((d) => {
    const li = document.createElement("li");
    li.textContent = d;
    ul.appendChild(li);
  });
}

function renderEnvironments() {
  // sincronizar filtros UI
  const providerSelect = $("#env-filter-provider");
  if (providerSelect) providerSelect.value = demoState.filters.provider;
  const searchInput = $("#env-filter-search");
  if (searchInput) searchInput.value = demoState.filters.envSearch;

  renderEnvTable();

  // si hay un entorno seleccionado, mostrarlo
  if (demoState.currentEnvSlug) {
    showEnvDetail(demoState.currentEnvSlug);
  }
}

// --- Render: Cuentas ---
function renderAccounts() {
  const tbody = $("#accounts-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  const filter = demoState.filters.accountsProvider;

  demoState.accounts.forEach((acc) => {
    if (filter !== "all" && acc.provider !== filter) return;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${acc.name}</td>
      <td>${acc.provider}</td>
      <td>${acc.id}</td>
      <td>${acc.region}</td>
    `;
    tbody.appendChild(tr);
  });
}

// --- Render: Despliegues ---
function renderDeployments() {
  const tbody = $("#deployments-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  demoState.deployments.forEach((dep) => {
    const env = demoState.envs.find((e) => e.slug === dep.envSlug);
    const tr = document.createElement("tr");
    const pill =
      dep.status === "success"
        ? '<span class="pill pill-ok">Éxito</span>'
        : '<span class="pill pill-warn">Atención</span>';
    tr.innerHTML = `
      <td>${env ? env.name : dep.envSlug}</td>
      <td>${pill}</td>
      <td>${dep.start}</td>
      <td>${dep.end}</td>
      <td><code>${dep.summary}</code></td>
    `;
    tbody.appendChild(tr);
  });
}

// --- Simular despliegue ---
function simulateDeployment() {
  const slug = demoState.currentEnvSlug;
  if (!slug) {
    toast("Selecciona un entorno antes de lanzar un despliegue.", "error");
    return;
  }
  const env = demoState.envs.find((e) => e.slug === slug);
  if (!env) return;

  // Pequeña "aleatoriedad" para demo
  const now = new Date();
  const start = new Date(now.getTime() - 2 * 60 * 1000); // hace 2 min
  const ok = Math.random() > 0.2; // 80% éxito
  const status = ok ? "success" : "failed";
  const summary = ok
    ? "helmfile sync OK · Prometheus/Grafana/ELK actualizados"
    : "Timeout al contactar con el cluster · revisar conectividad";

  const fmt = (d) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
      d.getDate()
    ).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(
      d.getMinutes()
    ).padStart(2, "0")}`;

  const deploy = {
    envSlug: slug,
    status,
    start: fmt(start),
    end: fmt(now),
    summary,
  };

  // prepend en histórico global
  demoState.deployments.unshift(deploy);

  // actualizar entorno
  env.lastDeploy = deploy;
  env.status = ok ? "ok" : "warn";
  env.deployments.unshift(`${deploy.end} · ${ok ? "Éxito" : "FALLO"} · ${summary}`);

  renderDashboard();
  renderDeployments();
  showEnvDetail(slug);

  toast(
    ok
      ? `Despliegue simulado en ${env.name} completado con éxito.`
      : `Despliegue simulado en ${env.name} con avisos. Revisa logs.`,
    ok ? "ok" : "error"
  );
}

// --- Modal de nuevo entorno ---
function openEnvModal() {
  $("#env-modal").classList.remove("hidden");
}
function closeEnvModal() {
  $("#env-modal").classList.add("hidden");
}

function bindEnvModal() {
  const form = $("#env-modal-form");
  const cancel = $("#env-modal-cancel");
  const backdrop = $("#env-modal .modal-backdrop");

  cancel?.addEventListener("click", () => {
    closeEnvModal();
  });
  backdrop?.addEventListener("click", () => {
    closeEnvModal();
  });

  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = $("#modal-env-name").value.trim();
    const slug = $("#modal-env-slug").value.trim();
    const provider = $("#modal-env-provider").value;
    const cluster = $("#modal-env-cluster").value;
    const retention = parseInt($("#modal-env-retention").value || "7", 10);

    if (!name || !slug) {
      toast("Rellena nombre y slug para crear el entorno.", "error");
      return;
    }
    if (demoState.envs.some((e) => e.slug === slug)) {
      toast("Ya existe un entorno con ese slug en la demo.", "error");
      return;
    }

    const env = {
      slug,
      name,
      provider,
      cluster,
      retentionDays: retention,
      components: ["Prometheus", "Grafana", "ELK"],
      status: "ok",
      lastDeploy: null,
      deployments: [],
    };
    demoState.envs.push(env);
    demoState.currentEnvSlug = slug;

    closeEnvModal();
    renderDashboard();
    renderEnvironments();
    toast(`Entorno simulado "${name}" añadido a la demo.`, "ok");
  });
}

// --- Ajustes demo ---
function applyHighContrast() {
  if (demoState.ui.highContrast) {
    document.documentElement.setAttribute("data-high-contrast", "true");
  } else {
    document.documentElement.removeAttribute("data-high-contrast");
  }
}

function randomizeStates() {
  demoState.envs.forEach((env) => {
    const r = Math.random();
    if (r < 0.7) env.status = "ok";
    else if (r < 0.9) env.status = "warn";
    else env.status = "error";
  });
  renderDashboard();
  renderEnvironments();
  toast("Estados de los entornos randomizados para la demo.", "ok");
}

function resetDemo() {
  // Para una demo simple, basta con recargar la página
  window.location.reload();
}


    // --- GitHub repos panel (demo usando API pública) ---
    async function loadGithubRepos(username) {
      const list = $("#github-repos-list");
      if (!list) return;
      if (!username) {
        list.innerHTML = '<li class="muted small">Introduce un usuario/organización válido.</li>';
        return;
      }
      list.innerHTML = '<li class="muted small">Cargando repos de ' + username + '...</li>';
      try {
        const resp = await fetch(
          "https://api.github.com/users/" +
            encodeURIComponent(username) +
            "/repos?sort=updated&per_page=10"
        );
        if (!resp.ok) {
          list.innerHTML =
            '<li class="muted small">No se pudo obtener la lista de repos (HTTP ' +
            resp.status +
            '). Puede deberse a límites de la API pública.</li>';
          return;
        }
        const data = await resp.json();
        if (!Array.isArray(data) || data.length === 0) {
          list.innerHTML =
            '<li class="muted small">No se encontraron repos públicos para ' +
            username +
            '.</li>';
          return;
        }
        list.innerHTML = "";
        data.forEach((repo) => {
          const li = document.createElement("li");
          const a = document.createElement("a");
          a.href = repo.html_url;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
          a.textContent = repo.full_name;
          li.appendChild(a);
          const span = document.createElement("span");
          span.className = "muted small";
          span.textContent = "  · " + (repo.description || "Sin descripción");
          li.appendChild(span);
          list.appendChild(li);
        });
      } catch (err) {
        console.error(err);
        list.innerHTML =
          '<li class="muted small">Error de red al consultar la API de GitHub.</li>';
      }
    }
    

    // --- Bindeos de eventos globales ---
function bindFiltersAndActions() {
  $("#dashboard-env-select")?.addEventListener("change", () => {
    renderDashboardTable();
  });
  $("#dashboard-provider-select")?.addEventListener("change", (e) => {
    demoState.filters.provider = e.target.value;
    $("#env-filter-provider").value = demoState.filters.provider;
    renderDashboard();
    renderEnvironments();
  });

  $("#env-filter-provider")?.addEventListener("change", (e) => {
    demoState.filters.provider = e.target.value;
    $("#dashboard-provider-select").value = demoState.filters.provider;
    renderDashboard();
    renderEnvironments();
  });

  $("#env-filter-search")?.addEventListener("input", (e) => {
    demoState.filters.envSearch = e.target.value;
    renderEnvironments();
  });

  $("#accounts-filter-provider")?.addEventListener("change", (e) => {
    demoState.filters.accountsProvider = e.target.value;
    renderAccounts();
  });

  $("#btn-simulate-deploy")?.addEventListener("click", () => {
    simulateDeployment();
  });

  $("#btn-env-new")?.addEventListener("click", () => {
    openEnvModal();
  });

  $("#btn-reset-demo")?.addEventListener("click", () => {
    resetDemo();
  });

  $("#btn-demo-randomize")?.addEventListener("click", () => {
    randomizeStates();
  });

  $("#toggle-high-contrast")?.addEventListener("change", (e) => {
    demoState.ui.highContrast = e.target.checked;
    applyHighContrast();
  });
}

// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
  bindNav();
  bindEnvModal();
  bindFiltersAndActions();
  applyHighContrast();

  renderDashboard();
  renderEnvironments();
  renderAccounts();
  renderDeployments();
});

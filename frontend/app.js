const API_BASE = "https://scuba-dives.onrender.com"; 

async function fetchWithAuth(input, init = {}) {
  const opts = { credentials: "include", ...init };
  let res = await fetch(input, opts);
  if (res.status === 401) {
    const r = await fetch(API_BASE + "/auth/refresh", { method: "POST", credentials: "include" });
    if (r.ok) {
      res = await fetch(input, opts);
    }
  }
  return res;
}

async function ensureLogin() {
  try {
    const res = await fetchWithAuth(API_BASE + "/auth/me");
    if (!res.ok) {
      window.location.href = "./auth.html";
      return null;
    }
    const me = await res.json();
    const emailSpan = document.getElementById("user-email");
    if (emailSpan) emailSpan.textContent = me.email;
    return me;
  } catch {
    window.location.href = "./auth.html";
    return null;
  }
}

async function logout() {
  await fetchWithAuth(API_BASE + "/auth/logout", { method: "POST" });
  window.location.href = "./auth.html";
}

function renderList(rows) {
  const box = document.getElementById("list");
  if (!box) return;
  if (!rows || rows.length === 0) {
    box.innerHTML = "<p class='muted'>暂无记录</p>";
    return;
  }
  box.innerHTML = rows.map(r => `
    <div class="item">
      <h3>${r.site || "-"} <span class="muted">（${r.country || "-"}）</span></h3>
      <div class="muted">${r.date || "-"} · 最大深度 ${r.max_depth || "-"} · 可见度 ${r.visibility || "-"}</div>
      <div class="split" style="margin-top:6px;">
        ${r.cylinder_pressure_start ? `<span class="pill">气压 ${r.cylinder_pressure_start} → ${r.cylinder_pressure_end || "-"}</span>` : ""}
        ${r.water_temp ? `<span class="pill">水温 ${r.water_temp}</span>` : ""}
        ${r.gas ? `<span class="pill">气体 ${r.gas}</span>` : ""}
        ${r.tank_type ? `<span class="pill">气瓶 ${r.tank_type}</span>` : ""}
        ${r.weight ? `<span class="pill">配重 ${r.weight}</span>` : ""}
      </div>
      ${r.notes ? `<div style="margin-top:6px;">${r.notes}</div>` : ""}
      <div class="row-actions">
        <button data-del="${r.id}" class="btn secondary">删除</button>
      </div>
    </div>
  `).join("");

  box.querySelectorAll(".btn.secondary[data-del]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-del");
      if (!id) return;
      const res = await fetchWithAuth(API_BASE + `/dives/${id}`, { method: "DELETE" });
      if (res.ok) loadList();
    });
  });
}

async function loadList() {
  const res = await fetchWithAuth(API_BASE + "/dives");
  if (!res.ok) {
    if (res.status === 401) window.location.href = "./auth.html";
    return;
  }
  const rows = await res.json();
  renderList(rows);
}

async function onCreate(e) {
  e.preventDefault();
  const saveMsg = document.getElementById("save-msg");
  if (saveMsg) { saveMsg.textContent = ""; }

  const data = {
    country: document.getElementById("country")?.value || null,
    site: document.getElementById("site")?.value || null,
    date: document.getElementById("date")?.value || null,
    entry_time: document.getElementById("entry_time")?.value || null,
    exit_time: document.getElementById("exit_time")?.value || null,
    bottom_time: document.getElementById("bottom_time")?.value || null,
    max_depth: document.getElementById("max_depth")?.value || null,
    avg_depth: document.getElementById("avg_depth")?.value || null,
    water_temp: document.getElementById("water_temp")?.value || null,
    visibility: document.getElementById("visibility")?.value || null,
    weather: document.getElementById("weather")?.value || null,
    cylinder_pressure_start: document.getElementById("cylinder_pressure_start")?.value || null,
    cylinder_pressure_end: document.getElementById("cylinder_pressure_end")?.value || null,
    gas: document.getElementById("gas")?.value || null,
    tank_type: document.getElementById("tank_type")?.value || null,
    weight: document.getElementById("weight")?.value || null,
    suit: document.getElementById("suit")?.value || null,
    computer: document.getElementById("computer")?.value || null,
    buddy: document.getElementById("buddy")?.value || null,
    guide: document.getElementById("guide")?.value || null,
    operator: document.getElementById("operator")?.value || null,
    notes: document.getElementById("notes")?.value || null,
    rating: document.getElementById("rating")?.value || null,
  };

  const res = await fetchWithAuth(API_BASE + "/dives", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (res.ok) {
    (document.getElementById("create-form") || {}).reset?.();
    if (saveMsg) { saveMsg.textContent = "已保存"; }
    loadList();
  } else if (res.status === 401) {
    window.location.href = "./auth.html";
  } else {
    const err = await res.json().catch(() => ({}));
    if (saveMsg) { saveMsg.textContent = err?.detail || "保存失败"; }
  }
}


window.addEventListener("DOMContentLoaded", async () => {
  const btnLogout = document.getElementById("btn-logout");
  if (btnLogout) btnLogout.addEventListener("click", logout);

  const me = await ensureLogin();
  if (!me) return;

  const form = document.getElementById("create-form");
  if (form) form.addEventListener("submit", onCreate);

  loadList();
});

async function logout(e) {
  if (e) e.preventDefault();
  await fetch(API_BASE + "/auth/logout", { method: "POST", credentials: "include" });
  location.replace("./auth.html");
}

document.getElementById("btn-logout")?.addEventListener("click", logout);

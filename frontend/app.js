// === 把后端 URL 改成你的域名或本地地址 ===
const API_BASE = "https://scuba-dives.onrender.com"; // 本地调试用 "http://127.0.0.1:8000"

// 通用 fetch：带 cookie，遇 401 自动 refresh 一次并重试
async function fetchWithAuth(input, init = {}) {
  const opts = { credentials: "include", ...init };
  let res = await fetch(input, opts);
  if (res.status === 401) {
    const r = await fetch(API_BASE + "/auth/refresh", { method: "POST", credentials: "include" });
    if (r.ok) res = await fetch(input, opts);
  }
  return res;
}

// 未登录则跳去登录页；已登录则显示邮箱
async function ensureLogin() {
  try {
    const res = await fetchWithAuth(API_BASE + "/auth/me");
    if (!res.ok) {
      location.replace("./auth.html");
      return null;
    }
    const me = await res.json();
    const emailSpan = document.getElementById("user-email");
    if (emailSpan) emailSpan.textContent = me.email;
    return me;
  } catch {
    location.replace("./auth.html");
    return null;
  }
}

// 退出
async function logout(e) {
  if (e) e.preventDefault();
  await fetchWithAuth(API_BASE + "/auth/logout", { method: "POST" });
  location.replace("./auth.html");
}

// 渲染列表（精简字段）
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
      <div class="muted">${r.date || "-"} · 最大深度 ${r.max_depth || "-"} m</div>
      <div style="margin-top:6px;">
        ${r.cylinder_pressure_start ? `<span class="pill">气压 ${r.cylinder_pressure_start} → ${r.cylinder_pressure_end || "-"}</span>` : ""}
        ${r.water_temp ? `<span class="pill">水温 ${r.water_temp} ℃</span>` : ""}
        ${r.gas ? `<span class="pill">气体 ${r.gas}</span>` : ""}
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

// 加载列表
async function loadList() {
  const res = await fetchWithAuth(API_BASE + "/dives");
  if (!res.ok) {
    if (res.status === 401) location.replace("./auth.html");
    return;
  }
  const rows = await res.json();
  renderList(rows);
}

// 前端校验：必须为整数的字段
function readInt(id, allowEmpty = true, min = null, max = null) {
  const el = document.getElementById(id);
  if (!el) return null;
  const v = el.value.trim();
  if (!v) return allowEmpty ? null : (function(){throw new Error(`请填写 ${id}`)})();
  const n = Number(v);
  if (!Number.isInteger(n)) throw new Error(`${id} 必须是整数`);
  if (min !== null && n < min) throw new Error(`${id} 不能小于 ${min}`);
  if (max !== null && n > max) throw new Error(`${id} 不能大于 ${max}`);
  return n;
}

// 保存新记录（只保留你需要的字段）
async function onCreate(e) {
  e.preventDefault();
  const saveMsg = document.getElementById("save-msg");
  if (saveMsg) { saveMsg.textContent = ""; saveMsg.className = "muted"; }

  try {
    const data = {
      country: document.getElementById("country")?.value || null,
      site: document.getElementById("site")?.value || null,
      date: document.getElementById("date")?.value || null,        // yyyy-mm-dd
      entry_time: document.getElementById("entry_time")?.value || null,
      exit_time: document.getElementById("exit_time")?.value || null,
      max_depth: readInt("max_depth", true, 0, 200),               // 整数校验
      water_temp: readInt("water_temp", true, -5, 40),             // 整数校验
      gas: document.getElementById("gas")?.value || null,
      cylinder_pressure_start: readInt("cylinder_pressure_start", true, 0, 400), // 整数校验
      cylinder_pressure_end: readInt("cylinder_pressure_end", true, 0, 400),     // 整数校验
      notes: document.getElementById("notes")?.value || null,
    };

    const res = await fetchWithAuth(API_BASE + "/dives", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (res.ok) {
      (document.getElementById("create-form") || {}).reset?.();
      if (saveMsg) { saveMsg.textContent = "已保存"; saveMsg.classList.add("ok"); }
      loadList();
    } else if (res.status === 401) {
      location.replace("./auth.html");
    } else {
      const err = await res.json().catch(() => ({}));
      throw new Error(err?.detail || "保存失败");
    }
  } catch (err) {
    if (saveMsg) { saveMsg.textContent = err.message || "保存失败"; saveMsg.classList.add("err"); }
  }
}

// 入口
window.addEventListener("DOMContentLoaded", async () => {
  document.getElementById("btn-logout")?.addEventListener("click", logout);
  const me = await ensureLogin();
  if (!me) return;
  document.getElementById("create-form")?.addEventListener("submit", onCreate);
  loadList();
});

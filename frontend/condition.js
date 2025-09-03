// ---- API 地址（可被 config.js 覆盖）----
const API_BASE = (window && window.API_BASE) ? window.API_BASE : "/api";

// ---- DOM ----
const q = document.getElementById("q");
const sugg = document.getElementById("suggest");
const dateEl = document.getElementById("date");
const daysEl = document.getElementById("days");
const btn = document.getElementById("btn");

// 默认日期设为今天
dateEl.valueAsDate = new Date();

// 当前选中的地点 {name, country, admin1, lat, lon}
let sel = null;

// ---- 地图 ----
let map = L.map('map').setView([20, 0], 2); // 初始世界视图
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(map);
let marker = null;

function setMarker(lat, lon, label) {
  if (!marker) {
    marker = L.marker([lat, lon]).addTo(map);
  } else {
    marker.setLatLng([lat, lon]);
  }
  marker.bindPopup(label).openPopup();
  map.setView([lat, lon], 8);
}

// ---- 搜索输入监听（已加防抖与容错）----
let typingTimer;

q.addEventListener("input", () => {
  clearTimeout(typingTimer);
  const text = q.value.trim();

  // 少于2个字符不搜
  if (text.length < 2) {
    sugg.style.display = "none";
    sel = null;
    return;
  }

  typingTimer = setTimeout(async () => {
    try {
      const url = `${API_BASE}/geocode?q=${encodeURIComponent(text)}`;
      const r = await fetch(url);
      if (!r.ok) { sugg.style.display = "none"; return; }
      const data = await r.json();

      // 渲染建议列表
      sugg.innerHTML = "";
      (data.results || []).forEach(item => {
        const div = document.createElement("div");
        const label = [item.name, item.admin1, item.country].filter(Boolean).join(" · ");
        div.textContent = label;
        div.addEventListener("click", () => {
          q.value = label;
          sel = item;
          sugg.style.display = "none";
          setMarker(item.lat, item.lon, label);
        });
        sugg.appendChild(div);
      });
      sugg.style.display = (data.results && data.results.length) ? "block" : "none";
      // 确保层级足够（避免被别的卡片遮挡）
      sugg.style.zIndex = 10;
    } catch (e) {
      console.error("geocode error:", e);
      sugg.style.display = "none";
    }
  }, 250); // 250ms 防抖
});

// ESC 关闭下拉
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") sugg.style.display = "none";
});

// 点击页面其他位置关闭下拉
document.addEventListener("click", (e) => {
  if (!sugg.contains(e.target) && e.target !== q) {
    sugg.style.display = "none";
  }
});

// ---- 查询按钮 ----
btn.addEventListener("click", async () => {
  if (!sel) { alert("请先选择地点"); return; }
  const params = new URLSearchParams({
    lat: sel.lat,
    lon: sel.lon,
    date: dateEl.value,
    days: daysEl.value
  });
  try {
    const r = await fetch(`${API_BASE}/conditions?${params.toString()}`);
    if (!r.ok) { alert("查询失败，请稍后再试"); return; }
    const data = await r.json();
    renderSummary(sel, data);
    renderDaily(data);
    renderHourly(data);
  } catch (e) {
    console.error("conditions error:", e);
    alert("网络错误，请检查后端是否已部署。");
  }
});

// ---- 渲染函数 ----
function renderSummary(place, data) {
  const cur = data.current_hint || {};
  const html = `
    <div><b>${place.name || ""}</b> ${place.admin1 || ""} ${place.country || ""}</div>
    <div>日期范围：${data.range.start} 至 ${data.range.end}</div>
    <div style="margin-top:8px; display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:6px;">
      <div>气温：${fmt(cur.temp_c, "°C")}</div>
      <div>风速：${fmt(cur.wind_speed, "m s⁻¹")}</div>
      <div>风向：${fmt(cur.wind_dir, "°")}</div>
      <div>能见度：${fmt(cur.visibility, "m")}</div>
      <div>浪高：${fmt(cur.wave_height, "m")}</div>
      <div>海温：${fmt(cur.water_temp, "°C")}</div>
    </div>
  `;
  document.getElementById("summaryBody").innerHTML = html;
}

function renderDaily(data) {
  const d = data.daily || {};
  const rows = (d.time || []).map((t, i) => `
    <tr>
      <td>${t}</td>
      <td>${fv(d.uv_index_max, i)}</td>
      <td>${fv(d.precipitation_sum, i)} mm</td>
      <td>${fv(d.wind_speed_10m_max, i)} m s⁻¹</td>
      <td>${fv(d.wind_gusts_10m_max, i)} m s⁻¹</td>
      <td>${fv(d.sunrise, i)} / ${fv(d.sunset, i)}</td>
    </tr>
  `).join("");
  document.getElementById("daily").innerHTML = `
    <div class="table">
      <table>
        <thead><tr>
          <th>日期</th><th>紫外线</th><th>日降水</th><th>最大风速</th><th>最大阵风</th><th>日出日落</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

function renderHourly(data) {
  const h = data.hourly || {};
  const N = Math.min(h.time.length, 24); // 只展示首日 24 小时
  const rows = Array.from({ length: N }).map((_, i) => `
    <tr>
      <td>${h.time[i]}</td>
      <td>${fv(h.temp_c, i)} °C</td>
      <td>${fv(h.wind_speed, i)} m s⁻¹</td>
      <td>${fv(h.precip, i)} mm</td>
      <td>${fv(h.cloud, i)} %</td>
      <td>${fv(h.visibility, i)} m</td>
      <td>${fv(h.wave_height, i)} m</td>
      <td>${fv(h.wave_period, i)} s</td>
      <td>${fv(h.water_temp, i)} °C</td>
    </tr>
  `).join("");
  document.getElementById("hourly").innerHTML = `
    <div class="table">
      <table>
        <thead><tr>
          <th>时间</th><th>气温</th><th>风速</th><th>降水</th><th>云量</th><th>能见度</th>
          <th>浪高</th><th>周期</th><th>海温</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

// ---- 小工具 ----
function fmt(x, unit) { return (x === null || x === undefined) ? "无" : `${x} ${unit}`; }
function fv(arr, i) { return (arr && arr[i] !== undefined && arr[i] !== null) ? arr[i] : "—"; }

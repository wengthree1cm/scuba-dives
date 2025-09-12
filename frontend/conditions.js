const API_BASE = "https://scuba-dives.onrender.com/api";

const MPA_GEOJSON_URL = "https://scuba-dives-data.s3.us-east-1.amazonaws.com/mpa.geojson";

const q = document.getElementById("q");
const sugg = document.getElementById("suggest");
const dateEl = document.getElementById("date");
const daysEl = document.getElementById("days");
const btn = document.getElementById("btn");

dateEl.valueAsDate = new Date();

let sel = null;

let map = L.map('map').setView([20, 0], 2); 
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


let mpaGeoJson = null;
let mpaLayer = null;

function ensureMpaBanner() {
  let el = document.getElementById('mpa-banner');
  if (!el) {
    el = document.createElement('div');
    el.id = 'mpa-banner';
    el.style.cssText = 'display:none;margin:8px 0;padding:10px 12px;border-radius:8px;background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;font-weight:600;';
    const summary = document.getElementById('summaryBody');
    if (summary && summary.parentElement) {
      summary.parentElement.parentElement.insertAdjacentElement('beforebegin', el);
    } else {
      document.body.prepend(el);
    }
  }
  return el;
}
function showMpaBanner(text) {
  const el = ensureMpaBanner();
  el.textContent = text;
  el.style.display = 'block';
}
function hideMpaBanner() {
  const el = ensureMpaBanner();
  el.style.display = 'none';
}

async function loadMpaLayer(mapInstance) {
  try {
    const res = await fetch(MPA_GEOJSON_URL, { cache: 'no-store' });
    if (!res.ok) return;
    mpaGeoJson = await res.json();

    mpaLayer = L.geoJSON(mpaGeoJson, {
      style: { color: '#10b981', weight: 1, fillOpacity: 0.08 }
    }).addTo(mapInstance);
  } catch (e) {
    console.warn('MPA geojson 加载失败：', e);
  }
}

function checkMpaHit(lat, lon) {
  if (!mpaGeoJson) return { hit: false, names: [] };
  if (typeof turf === 'undefined' || !turf || !turf.booleanPointInPolygon) {
    console.warn('未检测到 turf.js，保护区判断已跳过。');
    return { hit: false, names: [] };
  }
  const pt = turf.point([lon, lat]); 
  const names = [];

  const feats = mpaGeoJson.features || [];
  for (const f of feats) {
    try {
      if (turf.booleanPointInPolygon(pt, f)) {
        const props = f.properties || {};
        names.push(props.name || props.NAME || 'Protected Area');
      }
    } catch { /* Ignore bad shape */ }
  }
  return { hit: names.length > 0, names };
}

loadMpaLayer(map);

let typingTimer;

q.addEventListener("input", () => {
  clearTimeout(typingTimer);
  const text = q.value.trim();

  if (text.length < 2) {
    sugg.style.display = "none";
    sel = null;
    return;
  }

  typingTimer = setTimeout(async () => {
    try {
      const qText = text.toLowerCase();
      const url = `${API_BASE}/geocode?q=${encodeURIComponent(qText)}&language=en`;

      const r = await fetch(url);
      if (!r.ok) { sugg.style.display = "none"; return; }
      const data = await r.json();

      sugg.innerHTML = "";
      const items = (data.results || []);
      items.forEach(item => {
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

      sugg.style.display = items.length ? "block" : "none";
      sugg.style.zIndex = 10000; 
    } catch (e) {
      console.error("geocode error:", e);
      sugg.style.display = "none";
    }
  }, 250); 
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") sugg.style.display = "none";
});

document.addEventListener("click", (e) => {
  if (!sugg.contains(e.target) && e.target !== q) {
    sugg.style.display = "none";
  }
});

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

    const res = checkMpaHit(sel.lat, sel.lon);
    if (res.hit) {
      showMpaBanner(`⚠ 当前点位位于海洋保护/禁渔区：${res.names.join('、')}。请遵守当地规定。`);
    } else {
      hideMpaBanner();
    }

  } catch (e) {
    console.error("conditions error:", e);
    alert("网络错误，请检查后端是否已部署。");
  }
});

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
  const N = Math.min(h.time.length, 24); 
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

function fmt(x, unit) { return (x === null || x === undefined) ? "无" : `${x} ${unit}`; }
function fv(arr, i) { return (arr && arr[i] !== undefined && arr[i] !== null) ? arr[i] : "—"; }

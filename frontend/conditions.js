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
    console.warn('MPA geojson load failed：', e);
  }
}

function checkMpaHit(lat, lon) {
  if (!mpaGeoJson) return { hit: false, names: [] };
  if (typeof turf === 'undefined' || !turf || !turf.booleanPointInPolygon) {
    console.warn('did not detect turf.js');
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
  if (!sel) { alert("Please select location"); return; }
  const params = new URLSearchParams({
    lat: sel.lat,
    lon: sel.lon,
    date: dateEl.value,
    days: daysEl.value
  });
  try {
    const r = await fetch(`${API_BASE}/conditions?${params.toString()}`);
    if (!r.ok) { alert("failed search, please try later"); return; }
    const data = await r.json();
    renderSummary(sel, data);
    renderDaily(data);
    renderHourly(data);

    const res = checkMpaHit(sel.lat, sel.lon);
    if (res.hit) {
      showMpaBanner(`⚠ current location is in protected area：${res.names.join('、')} please follow the local rules`);
    } else {
      hideMpaBanner();
    }

  } catch (e) {
    console.error("conditions error:", e);
    alert("network error, check if deployed");
  }
});

function renderSummary(place, data) {
  const cur = data.current_hint || {};
  const html = `
    <div><b>${place.name || ""}</b> ${place.admin1 || ""} ${place.country || ""}</div>
    <div>Date range：${data.range.start} to ${data.range.end}</div>
    <div style="margin-top:8px; display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:6px;">
      <div>Air temperature：${fmt(cur.temp_c, "°C")}</div>
      <div>Air speed：${fmt(cur.wind_speed, "m s⁻¹")}</div>
      <div>Air direction：${fmt(cur.wind_dir, "°")}</div>
      <div>Visibility：${fmt(cur.visibility, "m")}</div>
      <div>Wave height：${fmt(cur.wave_height, "m")}</div>
      <div>Water temperature：${fmt(cur.water_temp, "°C")}</div>
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
          <th>Date</th><th>UV rays</th><th>daily precipitation</th><th>Max air speed</th><th>Maximum Wind Gust</th><th>Sunrise & Sunset</th>
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
          <th>Time</th><th>Air temperature</th><th>Air speed</th><th>Precipitation</th><th>Cloud</th><th>Visibility</th>
          <th>Wave Height</th><th>cycle</th><th>Water temperature</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

function fmt(x, unit) { return (x === null || x === undefined) ? "None" : `${x} ${unit}`; }
function fv(arr, i) { return (arr && arr[i] !== undefined && arr[i] !== null) ? arr[i] : "—"; }

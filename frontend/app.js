const API_PREFIX = '/dive-logs';

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

const form = $('#create-form');
const listEl = $('#list');
const emptyEl = $('#empty');
const searchInput = $('#search-input');
const refreshBtn = $('#refresh-btn');
const toastEl = $('#toast');

function toast(msg, type='info'){
  toastEl.textContent = msg;
  toastEl.className = 'toast' + (type==='error' ? ' error' : '');
  requestAnimationFrame(()=> toastEl.classList.add('show'));
  setTimeout(()=> toastEl.classList.remove('show'), 1800);
}

function isoFromLocal(dtLocal){
  // datetime-local 是本地时间，没有时区，转 ISO（UTC）
  if(!dtLocal) return null;
  const d = new Date(dtLocal);
  return d.toISOString();
}

function fmtLocal(iso){
  try{
    const d = new Date(iso);
    return d.toLocaleString();
  }catch{ return iso; }
}

async function createLog(payload){
  const res = await fetch(API_PREFIX, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  if(!res.ok){
    const t = await res.text();
    throw new Error(t || 'Create failed');
  }
  return res.json();
}

async function fetchLogs(){
  const res = await fetch(`${API_PREFIX}?skip=0&limit=500`);
  if(!res.ok) throw new Error('Load failed');
  return res.json();
}

async function deleteLog(id){
  const res = await fetch(`${API_PREFIX}/${id}`, { method:'DELETE' });
  if(!res.ok){
    const t = await res.text();
    throw new Error(t || 'Delete failed');
  }
  return true;
}

function renderLogs(items){
  const q = (searchInput.value || '').trim().toLowerCase();
  const filtered = items.filter(x=>{
    const hay = [
      x.country, x.location, x.site_name, x.buddy, String(x.dive_number || '')
    ].filter(Boolean).join(' ').toLowerCase();
    return hay.includes(q);
  });

  listEl.innerHTML = '';
  if(filtered.length === 0){
    emptyEl.classList.remove('hidden');
    return;
  }
  emptyEl.classList.add('hidden');

  for(const x of filtered){
    const card = document.createElement('div');
    card.className = 'log-card';

    const left = document.createElement('div');
    const right = document.createElement('div');
    right.className = 'actions-row';

    // 标题 + 元信息
    const title = document.createElement('div');
    title.className = 'title';
    title.textContent = `${x.country} · ${x.location} · ${x.site_name}`;

    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.innerHTML = `
      <span class="badge">#${x.dive_number}</span>
      <span class="kv"><span class="k">时间</span><span class="v">${fmtLocal(x.dive_time)}</span></span>
      <span class="kv"><span class="k">Buddy</span><span class="v">${x.buddy || '-'}</span></span>
      <span class="kv"><span class="k">最大深度</span><span class="v">${x.max_depth_m ?? '-'} m</span></span>
      <span class="kv"><span class="k">水下时间</span><span class="v">${x.bottom_time_min ?? '-'} min</span></span>
      <span class="kv"><span class="k">压力</span><span class="v">${x.air_start ?? '-'} → ${x.air_end ?? '-'}</span></span>
    `;

    const notes = document.createElement('div');
    notes.className = 'kv';
    if(x.notes){
      notes.innerHTML = `<span class="k">备注</span><span class="v">${x.notes}</span>`;
    }

    left.appendChild(title);
    left.appendChild(meta);
    if(x.notes) left.appendChild(notes);

    // 删除按钮
    const del = document.createElement('button');
    del.className = 'del';
    del.textContent = '删除';
    del.addEventListener('click', async ()=>{
      if(!confirm('确认删除这条潜水记录吗？')) return;
      try{
        await deleteLog(x.id);
        toast('已删除');
        await load();
      }catch(e){
        toast('删除失败', 'error');
        console.error(e);
      }
    });
    right.appendChild(del);

    card.appendChild(left);
    card.appendChild(right);
    listEl.appendChild(card);
  }
}

async function load(){
  try{
    const data = await fetchLogs();
    renderLogs(data);
  }catch(e){
    console.error(e);
    toast('加载失败', 'error');
  }
}

form.addEventListener('submit', async (ev)=>{
  ev.preventDefault();
  const fd = new FormData(form);

  const payload = {
    dive_time: isoFromLocal(fd.get('dive_time')),
    dive_number: Number(fd.get('dive_number')),
    country: (fd.get('country')||'').trim(),
    location: (fd.get('location')||'').trim(),
    site_name: (fd.get('site_name')||'').trim(),
    buddy: (fd.get('buddy')||'').trim() || null,
    max_depth_m: Number(fd.get('max_depth_m')),
    bottom_time_min: Number(fd.get('bottom_time_min')),
    air_start: fd.get('air_start') ? Number(fd.get('air_start')) : null,
    air_end: fd.get('air_end') ? Number(fd.get('air_end')) : null,
    notes: (fd.get('notes')||'').trim() || null,
  };

  try{
    await createLog(payload);
    toast('已保存');
    form.reset();
    await load();
  }catch(e){
    console.error(e);
    toast('保存失败：' + (e.message || ''), 'error');
  }
});

searchInput.addEventListener('input', ()=>{
  // 实时过滤（基于已有缓存，不再额外请求）
  // 这里直接复用最近一次数据：简单起见重新拉取
  load();
});
refreshBtn.addEventListener('click', load);

// 初始加载
load();

// API endpoints
const API = {
    satellites: 'http://localhost:8080',
    weather: 'http://localhost:8001',
    astro: 'http://localhost:8002',
    missions: 'http://localhost:8003',
    users: 'http://localhost:8004'
};

// State
let state = {
    currentPage: 'dashboard',
    satellites: [],
    weather: null,
    objects: [],
    missions: [],
    apod: null,
    serviceStatus: {}
};

// Navigation
function navigate(page) {
    state.currentPage = page;
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    const el = document.getElementById('page-' + page);
    const nav = document.getElementById('nav-' + page);
    if (el) { el.classList.add('active'); el.classList.add('fade-in'); }
    if (nav) nav.classList.add('active');
    // Load data for the page
    if (page === 'dashboard') loadDashboard();
    else if (page === 'satellites') loadSatellites();
    else if (page === 'weather') loadWeather();
    else if (page === 'astro') loadAstroObjects();
    else if (page === 'missions') loadMissions();
}

// Fetch helpers
function authHeaders() {
    const h = {'Content-Type': 'application/json'};
    const token = localStorage.getItem('authToken');
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
}

async function fetchJSON(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error('Fetch error:', url, e);
        return null;
    }
}

async function checkService(name, url) {
    try {
        const res = await fetch(url);
        state.serviceStatus[name] = res.ok ? 'online' : 'error';
    } catch { state.serviceStatus[name] = 'offline'; }
}

// ===== DASHBOARD =====
async function loadDashboard() {
    updateStatusIndicators();

    // Load satellites
    const tleData = await fetchJSON(API.satellites + '/fetch-tle');
    if (tleData && tleData.data) {
        state.satellites = tleData.data;
        document.getElementById('dash-sat-count').textContent = tleData.count || tleData.data.length;
        const satList = document.getElementById('dash-sat-list');
        satList.innerHTML = state.satellites.slice(0, 3).map(s => `
            <div class="flex justify-between items-center border-b border-[#414751]/20 pb-2">
                <span class="data-font text-sm text-[#c1c7d3]">${s.name}</span>
                <span class="data-font text-sm text-[#a4c9ff]">ID: ${s.norad_id}</span>
            </div>
        `).join('');
    } else {
        document.getElementById('dash-sat-count').textContent = '—';
    }

    // Load weather
    const wxData = await fetchJSON(API.weather + '/noaa-kp-index');
    if (wxData && wxData.latest_kp_index) {
        state.weather = wxData;
        const kp = wxData.latest_kp_index.Kp;
        document.getElementById('dash-kp').textContent = kp.toFixed(1);
        document.getElementById('dash-kp-label').textContent = getKpLabel(kp);
        const pct = Math.min(kp / 9 * 100, 100);
        document.getElementById('dash-kp-bar').style.width = pct + '%';
    }

    // Load APOD
    const apodData = await fetchJSON(API.missions + '/apod');
    if (apodData && apodData.url) {
        state.apod = apodData;
        document.getElementById('dash-apod-img').src = apodData.url;
        document.getElementById('dash-apod-title').textContent = apodData.title || 'NASA APOD';
    }

    // System health
    await Promise.all([
        checkService('satellite-tracker', API.satellites + '/'),
        checkService('space-weather', API.weather + '/'),
        checkService('astro-objects', API.astro + '/'),
        checkService('mission-data', API.missions + '/'),
        checkService('user-service', API.users + '/')
    ]);
    renderSystemHealth();
}

function getKpLabel(kp) {
    if (kp < 2) return 'Quiet';
    if (kp < 4) return 'Unsettled';
    if (kp < 5) return 'Active';
    if (kp < 6) return 'Minor Storm';
    if (kp < 7) return 'Moderate Storm';
    if (kp < 8) return 'Strong Storm';
    return 'Severe Storm';
}

function renderSystemHealth() {
    const container = document.getElementById('system-health');
    const services = [
        { name: 'Satellite Tracker', key: 'satellite-tracker', tech: 'FastAPI', port: 8080 },
        { name: 'Space Weather', key: 'space-weather', tech: 'FastAPI', port: 8001 },
        { name: 'Astro Objects', key: 'astro-objects', tech: 'FastAPI', port: 8002 },
        { name: 'Mission Data', key: 'mission-data', tech: 'FastAPI', port: 8003 },
        { name: 'User Service', key: 'user-service', tech: 'FastAPI', port: 8004 }
    ];
    container.innerHTML = services.map(s => {
        const status = state.serviceStatus[s.key] || 'unknown';
        const dotColor = status === 'online' ? 'bg-[#66dd8b]' : 'bg-[#ffb4ab]';
        const statusText = status === 'online' ? 'HEALTHY' : 'DOWN';
        const statusClass = status === 'online' ? 'text-[#66dd8b]' : 'text-[#ffb4ab]';
        return `
        <div class="mb-4">
            <div class="flex justify-between items-center mb-2">
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full ${dotColor} ${status === 'online' ? 'breathing-dot' : ''}"></div>
                    <span class="data-font text-base text-[#dee2ec]">${s.name}</span>
                </div>
                <span class="label-caps bg-[#30353d] px-2 py-0.5 rounded text-[#c1c7d3]">${s.tech}</span>
            </div>
            <div class="flex gap-2">
                <div class="flex-1 bg-[#252a32] p-2 rounded border border-[#414751]/20">
                    <div class="label-caps text-[#c1c7d3] mb-1">STATUS</div>
                    <div class="data-font text-sm ${statusClass}">${statusText}</div>
                </div>
                <div class="flex-1 bg-[#252a32] p-2 rounded border border-[#414751]/20">
                    <div class="label-caps text-[#c1c7d3] mb-1">PORT</div>
                    <div class="data-font text-sm text-[#dee2ec]">${s.port}</div>
                </div>
            </div>
        </div>`;
    }).join('');
}

function updateStatusIndicators() {
    Promise.all([
        checkService('nasa', API.missions + '/'),
        checkService('celestrak', API.satellites + '/')
    ]).then(() => {
        const nasaEl = document.getElementById('status-nasa');
        const stEl = document.getElementById('status-spacetrack');
        if (nasaEl) nasaEl.className = state.serviceStatus.nasa === 'online' ? 'text-[#66dd8b] font-bold' : 'text-[#ffb4ab] font-bold';
        if (stEl) stEl.className = state.serviceStatus.celestrak === 'online' ? 'text-[#66dd8b] font-bold' : 'text-[#ffb4ab] font-bold';
    });
}

// ===== SATELLITES =====
async function loadSatellites() {
    document.getElementById('sat-loading').classList.remove('hidden');
    const data = await fetchJSON(API.satellites + '/fetch-tle');
    document.getElementById('sat-loading').classList.add('hidden');
    if (data && data.data && data.data.length > 0) {
        state.satellites = data.data;
        renderSatelliteTable(data.data);
        if (data.data.length > 0) renderTelemetry(data.data[0]);
    } else {
        document.getElementById('sat-table-body').innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-[#c1c7d3]">No satellite data available. Celestrak may be rate-limiting.</td></tr>';
    }
}

function renderSatelliteTable(sats) {
    const tbody = document.getElementById('sat-table-body');
    tbody.innerHTML = sats.map((s, i) => `
        <tr class="data-row border-b border-[#414751]/10 cursor-pointer transition-colors ${i === 0 ? 'bg-[#a4c9ff]/5 border-l-2 border-l-[#a4c9ff]' : ''}" onclick="renderTelemetry(state.satellites[${i}])">
            <td class="px-6 py-3 flex items-center gap-3">
                <span class="material-symbols-outlined text-base ${i === 0 ? 'text-[#a4c9ff]' : 'text-[#c1c7d3]'}">satellite_alt</span>
                <span class="${i === 0 ? 'font-bold text-[#a4c9ff]' : ''}">${s.name}</span>
            </td>
            <td class="px-6 py-3 text-[#c1c7d3]">${s.norad_id}</td>
            <td class="px-6 py-3 data-font text-sm">${s.tle_line1 ? s.tle_line1.substring(0, 30) + '...' : 'N/A'}</td>
            <td class="px-6 py-3 text-center"><span class="inline-block w-2 h-2 rounded-full bg-[#66dd8b] shadow-[0_0_8px_rgba(102,221,139,0.5)]"></span></td>
        </tr>
    `).join('');
}

function renderTelemetry(sat) {
    document.getElementById('tel-name').textContent = sat.name;
    document.getElementById('tel-norad').textContent = 'NORAD ' + sat.norad_id;
    document.getElementById('tel-tle1').textContent = sat.tle_line1;
    document.getElementById('tel-tle2').textContent = sat.tle_line2;
    // Parse basic orbital elements from TLE
    try {
        const incl = sat.tle_line2.substring(8, 16).trim();
        const raan = sat.tle_line2.substring(17, 25).trim();
        const ecc = '0.' + sat.tle_line2.substring(26, 33).trim();
        const meanMotion = sat.tle_line2.substring(52, 63).trim();
        document.getElementById('tel-incl').textContent = incl + '°';
        document.getElementById('tel-raan').textContent = raan + '°';
        document.getElementById('tel-ecc').textContent = ecc;
        document.getElementById('tel-mm').textContent = meanMotion + ' rev/day';
    } catch (e) {
        console.error('TLE parse error', e);
    }
}

// ===== SPACE WEATHER =====
async function loadWeather() {
    const data = await fetchJSON(API.weather + '/noaa-kp-index');
    if (data && data.latest_kp_index) {
        state.weather = data;
        const kp = data.latest_kp_index.Kp;
        document.getElementById('wx-kp-value').textContent = kp.toFixed(2);
        document.getElementById('wx-kp-label').textContent = getKpLabel(kp);
        document.getElementById('wx-kp-time').textContent = data.latest_kp_index.time_tag;
        document.getElementById('wx-source').textContent = data.source || 'NOAA SWPC';

        // Kp severity color
        const kpEl = document.getElementById('wx-kp-value');
        if (kp >= 5) kpEl.className = 'metric-value text-[#ffb4ab]';
        else if (kp >= 4) kpEl.className = 'metric-value text-[#ffb953]';
        else kpEl.className = 'metric-value text-[#66dd8b]';

        // Render Kp scale
        renderKpScale(kp);
    }
}

function renderKpScale(kp) {
    const container = document.getElementById('wx-kp-scale');
    container.innerHTML = '';
    for (let i = 0; i <= 9; i++) {
        const colors = ['#66dd8b','#66dd8b','#66dd8b','#66dd8b','#ffb953','#ffb953','#ffb4ab','#ffb4ab','#ff5449','#ff5449'];
        const active = i <= Math.floor(kp);
        container.innerHTML += `<div class="flex-1 h-3 rounded-sm mx-0.5 transition-all" style="background:${active ? colors[i] : '#252a32'};opacity:${active ? 1 : 0.3}"></div>`;
    }
}

// ===== ASTRO OBJECTS =====
async function loadAstroObjects() {
    const data = await fetchJSON(API.astro + '/objects');
    if (data && Array.isArray(data)) {
        state.objects = data;
        renderObjectsTable(data);
    } else {
        document.getElementById('obj-table-body').innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-[#c1c7d3]">No objects in database. Add one using the form.</td></tr>';
    }
}

function renderObjectsTable(objects) {
    const tbody = document.getElementById('obj-table-body');
    if (!objects.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-[#c1c7d3]">No objects yet. Add one below.</td></tr>';
        return;
    }
    tbody.innerHTML = objects.map(o => `
        <tr class="data-row border-b border-[#414751]/10">
            <td class="px-6 py-3 text-[#a4c9ff] font-bold">${o.name}</td>
            <td class="px-6 py-3">${o.object_type}</td>
            <td class="px-6 py-3 data-font text-sm">${o.right_ascension}</td>
            <td class="px-6 py-3 data-font text-sm">${o.declination}</td>
            <td class="px-6 py-3 data-font text-sm">${o.distance_ly ? o.distance_ly + ' ly' : '—'}</td>
            <td class="px-4 py-3"><button onclick="deleteObject(${o.id})" class="text-[#ffb4ab] hover:text-[#ff5449] text-sm">✕</button></td>
        </tr>
    `).join('');
}

async function addAstroObject(e) {
    e.preventDefault();
    const form = e.target;
    const body = {
        name: form.name.value,
        object_type: form.object_type.value,
        right_ascension: form.ra.value,
        declination: form.dec.value,
        distance_ly: form.distance.value ? parseFloat(form.distance.value) : null
    };
    try {
        const res = await fetch(API.astro + '/objects/', {
            method: 'POST', headers: authHeaders(), body: JSON.stringify(body)
        });
        if (res.ok) { form.reset(); loadAstroObjects(); }
        else if (res.status === 401) { alert('Please login first'); }
    } catch (e) { console.error(e); }
}

// ===== MISSIONS =====
async function loadMissions() {
    const [missionsData, apodData, neoData] = await Promise.all([
        fetchJSON(API.missions + '/missions'),
        fetchJSON(API.missions + '/apod'),
        fetchJSON(API.missions + '/neo')
    ]);
    if (missionsData && Array.isArray(missionsData)) {
        state.missions = missionsData;
        renderMissionsTable(missionsData);
    }
    if (apodData) {
        state.apod = apodData;
        document.getElementById('mission-apod-img').src = apodData.url || '';
        document.getElementById('mission-apod-title').textContent = apodData.title || '';
        document.getElementById('mission-apod-desc').textContent = apodData.explanation ? apodData.explanation.substring(0, 200) + '...' : '';
    }
    // NEO data
    if (neoData && neoData.data) {
        renderNeoTable(neoData.data);
    }
}

function renderMissionsTable(missions) {
    const tbody = document.getElementById('mission-table-body');
    if (!missions.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-[#c1c7d3]">No missions yet. Add one below.</td></tr>';
        return;
    }
    tbody.innerHTML = missions.map(m => {
        const statusColor = m.status === 'active' ? 'text-[#66dd8b]' : m.status === 'planned' ? 'text-[#ffb953]' : 'text-[#c1c7d3]';
        return `
        <tr class="data-row border-b border-[#414751]/10">
            <td class="px-6 py-3 text-[#a4c9ff] font-bold">${m.name}</td>
            <td class="px-6 py-3">${m.agency}</td>
            <td class="px-6 py-3 data-font text-sm">${m.launch_date || '—'}</td>
            <td class="px-6 py-3 ${statusColor} font-bold uppercase data-font text-sm">${m.status}</td>
            <td class="px-6 py-3 text-sm text-[#c1c7d3]">${m.description || '—'}</td>
            <td class="px-4 py-3"><button onclick="deleteMission(${m.id})" class="text-[#ffb4ab] hover:text-[#ff5449] text-sm">✕</button></td>
        </tr>`;
    }).join('');
}

function renderNeoTable(neos) {
    const tbody = document.getElementById('neo-table-body');
    if (!tbody) return;
    if (!neos.length) { tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-[#c1c7d3]">No NEOs today</td></tr>'; return; }
    tbody.innerHTML = neos.map(n => {
        const hazClass = n.is_potentially_hazardous ? 'text-[#ffb4ab]' : 'text-[#66dd8b]';
        return `<tr class="data-row border-b border-[#414751]/10">
            <td class="px-4 py-2 text-[#a4c9ff]">${n.name}</td>
            <td class="px-4 py-2 data-font text-xs">${Math.round(n.estimated_diameter_m.min)}-${Math.round(n.estimated_diameter_m.max)} m</td>
            <td class="px-4 py-2 data-font text-xs">${parseFloat(n.close_approach).toFixed(4)} AU</td>
            <td class="px-4 py-2 data-font text-xs">${parseFloat(n.velocity_kmps).toFixed(1)} km/s</td>
            <td class="px-4 py-2 ${hazClass} font-bold text-xs">${n.is_potentially_hazardous ? 'YES' : 'No'}</td>
        </tr>`;
    }).join('');
}

async function addMission(e) {
    e.preventDefault();
    const form = e.target;
    const body = { name: form.name.value, agency: form.agency.value, launch_date: form.launch_date.value || null, status: form.status.value, description: form.description.value || null };
    try {
        const res = await fetch(API.missions + '/missions/', { method: 'POST', headers: authHeaders(), body: JSON.stringify(body) });
        if (res.ok) { form.reset(); loadMissions(); }
        else if (res.status === 401) { alert('Please login first'); }
    } catch (e) { console.error(e); }
}

async function deleteMission(id) {
    if (!localStorage.getItem('authToken')) { alert('Увійдіть в систему, щоб видаляти записи'); return; }
    if (!confirm('Видалити цю місію?')) return;
    const res = await fetch(API.missions + '/missions/' + id, { method: 'DELETE', headers: authHeaders() });
    if (res.status === 401) { alert('Сесія закінчилась, увійдіть знову'); logoutUser(); return; }
    loadMissions();
}

async function deleteObject(id) {
    if (!localStorage.getItem('authToken')) { alert('Увійдіть в систему, щоб видаляти записи'); return; }
    if (!confirm('Видалити цей об\'єкт?')) return;
    const res = await fetch(API.astro + '/objects/' + id, { method: 'DELETE', headers: authHeaders() });
    if (res.status === 401) { alert('Сесія закінчилась, увійдіть знову'); logoutUser(); return; }
    loadAstroObjects();
}

// ===== SPACE WEATHER - DONKI =====
async function loadDonkiEvents() {
    const [cme, flr, gst] = await Promise.all([
        fetchJSON(API.weather + '/donki/cme'),
        fetchJSON(API.weather + '/donki/flr'),
        fetchJSON(API.weather + '/donki/gst')
    ]);
    const container = document.getElementById('wx-events');
    if (!container) return;
    let html = '';
    if (flr && flr.data) {
        flr.data.slice(0, 3).forEach(f => {
            html += `<div class="p-3 border border-[#414751]/20 rounded bg-[#171c23]/50">
                <div class="flex justify-between"><span class="font-bold text-sm">Solar Flare ${f.classType || ''}</span><span class="status-badge ${f.classType && f.classType.startsWith('X') ? 'status-error' : 'status-warn'}">${f.classType || 'N/A'}</span></div>
                <div class="data-font text-xs text-[#c1c7d3] mt-1">Peak: ${f.peakTime || '—'}</div></div>`;
        });
    }
    if (cme && cme.data) {
        cme.data.slice(0, 3).forEach(c => {
            html += `<div class="p-3 border border-[#414751]/20 rounded bg-[#171c23]/50">
                <div class="flex justify-between"><span class="font-bold text-sm">CME</span><span class="status-badge status-warn">CME</span></div>
                <div class="data-font text-xs text-[#c1c7d3] mt-1">${c.startTime || '—'} | ${c.sourceLocation || '—'}</div></div>`;
        });
    }
    if (gst && gst.data) {
        gst.data.slice(0, 2).forEach(g => {
            html += `<div class="p-3 border border-[#414751]/20 rounded bg-[#171c23]/50">
                <div class="flex justify-between"><span class="font-bold text-sm">Geomagnetic Storm</span><span class="status-badge status-error">GST</span></div>
                <div class="data-font text-xs text-[#c1c7d3] mt-1">${g.startTime || '—'}</div></div>`;
        });
    }
    container.innerHTML = html || '<p class="text-[#c1c7d3] text-sm">No recent DONKI events</p>';
}

async function loadKpChart() {
    const data = await fetchJSON(API.weather + '/kp-history');
    if (!data || !data.data) return;
    const canvas = document.getElementById('kp-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const entries = data.data;
    const w = canvas.width = canvas.offsetWidth;
    const h = canvas.height = canvas.offsetHeight || 200;
    
    let activeIndex = -1;

    function drawChart() {
        ctx.clearRect(0, 0, w, h);
        
        // Draw grid
        ctx.strokeStyle = 'rgba(65, 71, 81, 0.15)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 9; i++) {
            ctx.beginPath();
            ctx.moveTo(40, h - 30 - i * (h - 50) / 9);
            ctx.lineTo(w - 20, h - 30 - i * (h - 50) / 9);
            ctx.stroke();
            
            // Draw Y-axis labels
            ctx.fillStyle = 'rgba(193, 199, 211, 0.6)';
            ctx.font = '10px "JetBrains Mono", monospace';
            ctx.fillText('Kp ' + i, 10, h - 26 - i * (h - 50) / 9);
        }

        const plotW = w - 60;
        const plotH = h - 50;

        if (entries.length < 2) return;

        // Draw line with glowing gradient
        const grad = ctx.createLinearGradient(40, 0, w - 20, 0);
        grad.addColorStop(0, '#66dd8b');
        grad.addColorStop(0.5, '#ffb953');
        grad.addColorStop(1, '#ff5449');

        ctx.beginPath();
        entries.forEach((e, i) => {
            const x = 40 + (i / (entries.length - 1)) * plotW;
            const y = h - 30 - (e.Kp / 9) * plotH;
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        });

        ctx.strokeStyle = grad;
        ctx.lineWidth = 3;
        ctx.shadowColor = 'rgba(164, 201, 255, 0.3)';
        ctx.shadowBlur = 8;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Draw Area Fill
        ctx.lineTo(40 + plotW, h - 30);
        ctx.lineTo(40, h - 30);
        ctx.closePath();
        const fillGrad = ctx.createLinearGradient(0, 20, 0, h - 30);
        fillGrad.addColorStop(0, 'rgba(164, 201, 255, 0.15)');
        fillGrad.addColorStop(1, 'rgba(164, 201, 255, 0.0)');
        ctx.fillStyle = fillGrad;
        ctx.fill();

        // X-axis time labels
        const labelInterval = Math.max(1, Math.floor(entries.length / 4));
        entries.forEach((e, i) => {
            if (i % labelInterval === 0 || i === entries.length - 1) {
                const x = 40 + (i / (entries.length - 1)) * plotW;
                ctx.fillStyle = 'rgba(193, 199, 211, 0.6)';
                ctx.font = '9px "JetBrains Mono", monospace';
                const date = new Date(e.time_tag);
                const timeStr = date.toLocaleDateString(undefined, {month:'short', day:'numeric'}) + ' ' + date.toLocaleTimeString(undefined, {hour:'2-digit', minute:'2-digit', hour12:false});
                ctx.fillText(timeStr, x - 25, h - 10);
            }
        });

        // Interactive Highlight
        if (activeIndex !== -1 && activeIndex < entries.length) {
            const activeEntry = entries[activeIndex];
            const x = 40 + (activeIndex / (entries.length - 1)) * plotW;
            const y = h - 30 - (activeEntry.Kp / 9) * plotH;

            ctx.strokeStyle = 'rgba(164, 201, 255, 0.25)';
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(x, 20);
            ctx.lineTo(x, h - 30);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = activeEntry.Kp >= 5 ? '#ff5449' : activeEntry.Kp >= 4 ? '#ffb953' : '#66dd8b';
            ctx.shadowColor = ctx.fillStyle;
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(x, y, 2.5, 0, Math.PI * 2);
            ctx.fill();

            // Tooltip box
            ctx.fillStyle = 'rgba(27, 32, 39, 0.95)';
            ctx.strokeStyle = 'rgba(164, 201, 255, 0.4)';
            ctx.lineWidth = 1;
            
            const tooltipW = 140;
            const tooltipH = 45;
            let tx = x + 15;
            let ty = y - 50;
            
            if (tx + tooltipW > w) tx = x - tooltipW - 15;
            if (ty < 10) ty = y + 15;

            ctx.beginPath();
            ctx.roundRect(tx, ty, tooltipW, tooltipH, 4);
            ctx.fill();
            ctx.stroke();

            ctx.fillStyle = '#dee2ec';
            ctx.font = 'bold 11px "Inter", sans-serif';
            ctx.fillText('Index: Kp ' + activeEntry.Kp.toFixed(2), tx + 8, ty + 18);
            
            ctx.fillStyle = '#a4c9ff';
            ctx.font = '9px "JetBrains Mono", monospace';
            const fullDate = new Date(activeEntry.time_tag).toLocaleString();
            ctx.fillText(fullDate, tx + 8, ty + 34);
        }
    }

    canvas.onmousemove = function(e) {
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const plotW = w - 60;
        const pct = (mouseX - 40) / plotW;
        let index = Math.round(pct * (entries.length - 1));
        if (index < 0) index = 0;
        if (index >= entries.length) index = entries.length - 1;

        if (index !== activeIndex) {
            activeIndex = index;
            drawChart();
        }
    };

    canvas.onmouseleave = function() {
        activeIndex = -1;
        drawChart();
    };

    drawChart();
}

// Override loadWeather to also load DONKI + chart
const _origLoadWeather = loadWeather;
loadWeather = async function() {
    await _origLoadWeather();
    loadDonkiEvents();
    setTimeout(loadKpChart, 100);
};

// ===== AUTH =====
let authToken = localStorage.getItem('authToken');
let authUser = localStorage.getItem('authUser');

function updateAuthUI() {
    const authSection = document.getElementById('auth-section');
    const userSection = document.getElementById('user-section');
    if (!authSection) return;
    if (authToken) {
        authSection.style.display = 'none';
        if (userSection) { userSection.style.display = 'block'; document.getElementById('user-name').textContent = authUser || 'User'; }
    } else {
        authSection.style.display = 'block';
        if (userSection) userSection.style.display = 'none';
    }
}

async function loginUser(e) {
    e.preventDefault();
    const form = e.target;
    const body = { username: form.username.value, password: form.password.value };
    try {
        const res = await fetch(API.users + '/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
        if (res.ok) {
            const data = await res.json();
            authToken = data.access_token;
            authUser = data.username;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('authUser', authUser);
            updateAuthUI();
            form.reset();
            document.getElementById('auth-error').textContent = '';
        } else {
            document.getElementById('auth-error').textContent = 'Invalid credentials';
        }
    } catch (e) { document.getElementById('auth-error').textContent = 'Connection error'; }
}

async function registerUser(e) {
    e.preventDefault();
    const form = e.target;
    const body = { username: form.reg_username.value, email: form.reg_email.value, password: form.reg_password.value };
    try {
        const res = await fetch(API.users + '/register', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
        if (res.ok) {
            document.getElementById('reg-msg').textContent = 'Registered! Please login.';
            document.getElementById('reg-msg').className = 'text-[#66dd8b] text-sm mt-2';
            form.reset();
        } else {
            const err = await res.json();
            document.getElementById('reg-msg').textContent = err.detail || 'Error';
            document.getElementById('reg-msg').className = 'text-[#ffb4ab] text-sm mt-2';
        }
    } catch (e) { document.getElementById('reg-msg').textContent = 'Connection error'; }
}

function logoutUser() {
    authToken = null; authUser = null;
    localStorage.removeItem('authToken'); localStorage.removeItem('authUser');
    updateAuthUI();
}

// ===== SEARCH =====
function filterTable(inputId, tableBodyId) {
    const query = document.getElementById(inputId).value.toLowerCase();
    const rows = document.getElementById(tableBodyId).querySelectorAll('tr');
    rows.forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
    });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    navigate('dashboard');
    updateAuthUI();
});


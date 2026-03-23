import re
import os

with open('gym_tracker_website.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Auth & Dashboard screens
auth_screen = """
<!-- AUTH SCREEN -->
<div id="scr-auth" class="scr on" style="justify-content:center; padding:20px;">
  <div style="text-align:center; margin-bottom:40px;">
    <div class="ff" style="font-size:48px; color:var(--acc); letter-spacing:.1em">GYM TRACKER</div>
    <div style="color:var(--tx2); font-size:14px">Dein perfekter Trainingsbegleiter</div>
  </div>
  <div id="auth-login">
    <input type="text" id="log-user" class="si" style="margin-bottom:10px" placeholder="Email oder Benutzername">
    <input type="password" id="log-pass" class="si" style="margin-bottom:10px" placeholder="Passwort">
    <button class="btn btn-p" id="btn-login" style="margin-top:10px">Login</button>
    <div style="text-align:center; margin-top:20px; color:var(--tx2); font-size:13px">
      Noch kein Account? <span id="btn-goto-reg" style="color:var(--acc); cursor:pointer; font-weight:600">Registrieren</span>
    </div>
  </div>
  <div id="auth-reg" style="display:none">
    <input type="text" id="reg-user" class="si" style="margin-bottom:10px" placeholder="Benutzername">
    <input type="email" id="reg-email" class="si" style="margin-bottom:10px" placeholder="Email">
    <input type="password" id="reg-pass" class="si" style="margin-bottom:10px" placeholder="Passwort">
    <button class="btn btn-p" id="btn-reg" style="margin-top:10px">Registrieren</button>
    <div style="text-align:center; margin-top:20px; color:var(--tx2); font-size:13px">
      Bereits einen Account? <span id="btn-goto-log" style="color:var(--acc); cursor:pointer; font-weight:600">Login</span>
    </div>
  </div>
  <div id="auth-verify" style="display:none">
    <div style="color:var(--tx2); font-size:13px; margin-bottom:10px; text-align:center">Bitte prüfe deine Server-Konsole für den Bestätigungscode.</div>
    <input type="email" id="ver-email" class="si" style="margin-bottom:10px" placeholder="Email">
    <input type="text" id="ver-token" class="si" style="margin-bottom:10px" placeholder="Bestätigungscode">
    <button class="btn btn-p" id="btn-verify" style="margin-top:10px">Bestätigen</button>
  </div>
  <div style="margin-top:30px; text-align:center">
    <button class="btn btn-s" id="btn-offline-mode" style="padding:10px">Offline Modus (Lokal weiter nutzen)</button>
  </div>
</div>

<!-- DASHBOARD SCREEN -->
<div id="scr-dashboard" class="scr">
  <div class="hdr"><span class="hdr-title">DASHBOARD</span></div>
  <div class="sa">
    <div class="sec-hdr"><span class="sec-title">Statistiken (7 Tage)</span></div>
    <div class="sg" style="grid-template-columns:1fr 1fr">
      <div class="sb"><div class="sv" id="dash-wk-week">0</div><div class="sl">Workouts</div></div>
      <div class="sb"><div class="sv" id="dash-avg-dur">0m</div><div class="sl">Ø Dauer</div></div>
    </div>
  </div>
</div>
"""

html = html.replace('<!-- HOME -->', auth_screen + '\n<!-- HOME -->')

# 2. Add Timer Bar UI and CSS
timer_css = """
/* TIMER BAR */
.timer-bar{position:fixed;bottom:var(--nav);left:50%;transform:translateX(-50%);width:100%;max-width:480px;background:var(--acc);color:#000;padding:10px 14px;display:none;align-items:center;justify-content:space-between;z-index:90;font-weight:600;font-size:14px;border-top-left-radius:12px;border-top-right-radius:12px;}
.timer-bar.active{display:flex}
.timer-close{width:24px;height:24px;background:rgba(0,0,0,0.1);border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer}
"""
html = html.replace('</style>', timer_css + '\n</style>')

timer_html = """
<!-- TIMER BAR -->
<div id="timer-bar" class="timer-bar">
  <span>Rest Timer: <span id="timer-val" style="font-family:'Bebas Neue',sans-serif;font-size:18px;letter-spacing:1px;margin-left:5px">00:00</span></span>
  <div class="timer-close" id="btn-timer-close">✕</div>
</div>

<!-- TIMER MODAL -->
<div id="m-timer" class="moverlay">
  <div class="modal">
    <div class="mhandle"></div>
    <div class="mtitle">Rest Timer</div>
    <div style="font-size:12px;color:var(--tx2);margin-bottom:14px" id="m-timer-rec">Empfohlen: 2:00</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px">
      <button class="btn btn-s t-opt" data-t="30">30s</button>
      <button class="btn btn-s t-opt" data-t="60">60s</button>
      <button class="btn btn-s t-opt" data-t="90">90s</button>
      <button class="btn btn-s t-opt" data-t="120">2m</button>
      <button class="btn btn-s t-opt" data-t="150">2.5m</button>
      <button class="btn btn-s t-opt" data-t="180">3m</button>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:14px">
      <input type="number" id="t-custom" class="si" placeholder="Sekunden" style="margin:0; padding:8px">
      <button class="btn btn-p" id="btn-timer-custom" style="width:auto">Start</button>
    </div>
    <button class="btn btn-s" onclick="cm('m-timer')">Schließen</button>
  </div>
</div>
"""
html = html.replace('<!-- MODALS -->', timer_html + '\n<!-- MODALS -->')

# 3. Add Dashboard to Nav
nav_patch = """
  <button class="nbtn" data-s="dashboard"><div class="nico">📊</div><span>Dash</span></button>
"""
html = html.replace('<span>Verlauf</span></button>', '<span>Verlauf</span></button>' + nav_patch)

# 4. Timer Button in Workout Screen Header
timer_btn = """
      <button id="btn-timer-open" class="hdr-btn" style="color:var(--orange);font-weight:bold;margin-right:4px">⏱</button>
"""
html = html.replace('<button id="btn-warmup"', timer_btn + '      <button id="btn-warmup"')

# 5. Hide main screens on boot
html = html.replace('<div id="scr-home" class="scr on">', '<div id="scr-home" class="scr">')

# 6. Add Cloud Sync to Settings
sync_ui = """
    <div class="div" style="margin-top:14px"></div>
    <div class="sec-hdr"><span class="sec-title">Cloud Sync</span></div>
    <div class="card" style="margin-top:0">
      <div id="sync-status" style="font-size:12px;color:var(--tx2);margin-bottom:10px">Nicht angemeldet.</div>
      <button class="btn btn-p" id="btn-sync-now" style="display:none; margin-bottom:8px">Jetzt Synchronisieren</button>
      <button class="btn btn-s" id="btn-logout" style="display:none">Logout</button>
    </div>
"""
html = html.replace('<div class="sec-hdr"><span class="sec-title">Startdatum</span></div>', sync_ui + '\n    <div class="sec-hdr"><span class="sec-title">Startdatum</span></div>')

# 7. JavaScript Patches
js_patch = """
// =======================================================
// CLOUD API & AUTH
// =======================================================
const API_URL = 'http://localhost:3000/api';
let authToken = localStorage.getItem('gtrk_token') || null;

async function apiCall(endpoint, method='POST', body=null) {
  const headers = { 'Content-Type': 'application/json' };
  if (authToken) headers['Authorization'] = authToken;
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(API_URL + endpoint, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'API Error');
    return data;
  } catch (err) {
    toast(err.message);
    throw err;
  }
}

function checkAuthState() {
  if (authToken) {
    document.getElementById('scr-auth').classList.remove('on');
    show('home');
    document.getElementById('sync-status').textContent = 'Eingeloggt. Verbunden mit Cloud.';
    document.getElementById('btn-sync-now').style.display = 'block';
    document.getElementById('btn-logout').style.display = 'block';
    syncFromServer();
  } else {
    // Wenn nicht eingeloggt, zeige Auth-Screen
    SCRIDS.forEach(s => { const el = document.getElementById('scr-'+s); if(el) el.classList.remove('on'); });
    document.querySelector('.bnav').style.display = 'none';
    document.getElementById('scr-auth').classList.add('on');
    document.getElementById('sync-status').textContent = 'Offline Modus aktiv.';
    document.getElementById('btn-sync-now').style.display = 'none';
    document.getElementById('btn-logout').style.display = 'none';
  }
}

async function syncToServer() {
  if (!authToken) return;
  try {
    await apiCall('/sync', 'POST', {
      log: S.log,
      cycleStartIndex: S.cycleStartIndex,
      cycleStartDate: S.cycleStartDate,
      tips: S.tips
    });
    toast('Cloud Sync: Gespeichert ✓');
  } catch (e) {}
}

async function syncFromServer() {
  if (!authToken) return;
  try {
    const data = await apiCall('/sync', 'GET');
    S.log = data.log || [];
    S.cycleStartIndex = data.cycleStartIndex || 0;
    S.cycleStartDate = data.cycleStartDate || null;
    if(data.tips) S.tips = data.tips;
    saveLocally(); // save locally to keep cache fresh
    renderHome();
    toast('Cloud Sync: Geladen ✓');
  } catch (e) {}
}

// Override default save to also sync
const originalSave = save;
save = function() {
  originalSave();
  syncToServer();
};
function saveLocally() { originalSave(); }

// UI Bindings for Auth
document.getElementById('btn-goto-reg').onclick = () => { document.getElementById('auth-login').style.display='none'; document.getElementById('auth-reg').style.display='block'; };
document.getElementById('btn-goto-log').onclick = () => { document.getElementById('auth-reg').style.display='none'; document.getElementById('auth-login').style.display='block'; };

document.getElementById('btn-reg').onclick = async () => {
  const u = document.getElementById('reg-user').value.trim();
  const e = document.getElementById('reg-email').value.trim();
  const p = document.getElementById('reg-pass').value.trim();
  if(!u||!e||!p) return toast('Bitte alle Felder ausfüllen');
  try {
    const res = await apiCall('/register', 'POST', {username:u, email:e, password:p});
    toast(res.message, 4000);
    document.getElementById('auth-reg').style.display='none';
    document.getElementById('auth-verify').style.display='block';
    document.getElementById('ver-email').value = e;
  } catch(err){}
};

document.getElementById('btn-verify').onclick = async () => {
  const e = document.getElementById('ver-email').value.trim();
  const t = document.getElementById('ver-token').value.trim();
  if(!e||!t) return toast('Bitte Token eingeben');
  try {
    const res = await apiCall('/verify', 'POST', {email:e, token:t});
    toast(res.message);
    document.getElementById('auth-verify').style.display='none';
    document.getElementById('auth-login').style.display='block';
  } catch(err){}
};

document.getElementById('btn-login').onclick = async () => {
  const u = document.getElementById('log-user').value.trim();
  const p = document.getElementById('log-pass').value.trim();
  if(!u||!p) return toast('Bitte ausfüllen');
  try {
    const res = await apiCall('/login', 'POST', {ident:u, password:p});
    authToken = res.token;
    localStorage.setItem('gtrk_token', authToken);
    toast('Login erfolgreich!');
    checkAuthState();
  } catch(err){}
};

document.getElementById('btn-offline-mode').onclick = () => {
  authToken = null;
  document.getElementById('scr-auth').classList.remove('on');
  show('home');
  document.querySelector('.bnav').style.display = 'flex';
  toast('Offline Modus aktiv');
};

document.getElementById('btn-logout').onclick = () => {
  authToken = null;
  localStorage.removeItem('gtrk_token');
  checkAuthState();
};
document.getElementById('btn-sync-now').onclick = syncToServer;

// =======================================================
// TIMER LOGIC
// =======================================================
let timerInt = null;
let timerEnd = null;
const beep = () => {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    osc.type = 'sine'; osc.frequency.setValueAtTime(440, ctx.currentTime);
    osc.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + 0.5);
    if(navigator.vibrate) navigator.vibrate([200,100,200]);
  } catch(e){}
};

function startTimer(sec) {
  cm('m-timer');
  timerEnd = Date.now() + sec * 1000;
  document.getElementById('timer-bar').classList.add('active');
  if(timerInt) clearInterval(timerInt);
  timerInt = setInterval(() => {
    let rem = Math.max(0, Math.ceil((timerEnd - Date.now())/1000));
    let m = Math.floor(rem/60), s = rem%60;
    document.getElementById('timer-val').textContent = `${m}:${s<10?'0':''}${s}`;
    if(rem <= 0) {
      clearInterval(timerInt);
      document.getElementById('timer-bar').classList.remove('active');
      beep(); toast('Pause vorbei!');
    }
  }, 1000);
}

document.getElementById('btn-timer-open').onclick = () => {
  if (WS && WS.exs && WS.exs.length > 0 && WS.exs[WS.idx]) {
    let ex = WS.exs[WS.idx];
    document.getElementById('m-timer-rec').textContent = `Empfohlen für ${ex.name}: 1:30`;
  }
  om('m-timer');
};
document.querySelectorAll('.t-opt').forEach(b => b.onclick = () => startTimer(parseInt(b.dataset.t)));
document.getElementById('btn-timer-custom').onclick = () => {
  let v = parseInt(document.getElementById('t-custom').value);
  if(v > 0) startTimer(v);
};
document.getElementById('btn-timer-close').onclick = () => {
  clearInterval(timerInt); document.getElementById('timer-bar').classList.remove('active');
};

// Dashboard Stats
function renderDashboard() {
  let now = Date.now();
  let weekAgoStr = new Date(now - 7*86400000).toISOString().split('T')[0];
  let wksWeek = S.log.filter(e => e.type === 'training' && e.date >= weekAgoStr);
  document.getElementById('dash-wk-week').textContent = wksWeek.length;
  // Durations mock logic
  document.getElementById('dash-avg-dur').textContent = (wksWeek.length > 0 ? '75m' : '0m');
}
"""

html = html.replace('let detailDate=null;', 'let detailDate=null;\n' + js_patch)

# Dashboard routing
dashboard_routing = """
  if(name==='dashboard') renderDashboard();
"""
html = html.replace("if(name==='settings'){renderCal();", dashboard_routing + "\n  if(name==='settings'){renderCal();")
html = html.replace("const SCRIDS=['home','workout','timeline','td','edit','exd','settings'];", "const SCRIDS=['auth','home','workout','timeline','td','edit','exd','settings','dashboard'];")

# Initialization override
html = html.replace('renderHome();\n});', 'checkAuthState();\n});')

with open('gym_tracker_website.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patch applied successfully.")

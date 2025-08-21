# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.plannings.router import router as planning_router

app = FastAPI(title="CSI API", version="2.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API
app.include_router(planning_router)

# Health
@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

# ---------- UI inline : page d’accueil ----------
@app.get("/", include_in_schema=False)
async def home(_: Request):
    html_lines = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>CSI • Analyse des plannings</title>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<link rel='icon' href='data:,'>",
        "<style>",
        ":root{--bg:#0b1020;--card:#111833;--text:#e6e9f2;--muted:#9aa3b2;--accent:#6aa1ff;--err:#ef4444}",
        "*{box-sizing:border-box} body{margin:0;background:linear-gradient(180deg,#0b1020,#0e1630);}",
        ".wrap{max-width:880px;margin:48px auto;padding:0 20px;color:var(--text);font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}",
        ".card{background:var(--card);border:1px solid #1b254a;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.3);padding:24px}",
        "h1{margin:0 0 12px;font-size:28px} p.muted{color:var(--muted);margin:0 0 16px}",
        "label{display:block;margin:12px 0 6px;color:#c8d2ea}",
        "input[type=url]{width:100%;padding:12px 14px;border-radius:12px;border:1px solid #26325f;background:#0d1330;color:#eaf1ff;outline:none}",
        ".row{display:flex;gap:12px;margin-top:16px}",
        "button{cursor:pointer;border:1px solid #2a3a75;background:#1a2a6a;color:#eaf1ff;padding:12px 16px;border-radius:12px}",
        "button:hover{background:#21347e}",
        ".err{color:var(--err);margin-top:8px;display:none}",
        "small{color:var(--muted)}",
        "</style>",
        "<div class='wrap'><div class='card'>",
        "<h1>Analyse des plannings</h1>",
        "<p class='muted'>Colle l’URL de la page planning puis clique <b>Analyser</b>. Tu seras redirigé vers la page d’analyse.</p>",
        "<label for='planning-url'>URL du planning</label>",
        "<input id='planning-url' type='url' placeholder='https://exemple.tld/planning' />",
        "<div class='row'>",
        "<button id='btn-analyze'>Analyser</button>",
        "<a href='/docs' target='_blank' style='align-self:center;color:var(--accent);text-decoration:none'>Docs API →</a>",
        "</div>",
        "<div id='error-status' class='err'>❌ Erreur</div>",
        "<p><small>Ou appelle directement l’API <code>POST /plannings/analyze</code> (voir Docs).</small></p>",
        "</div></div>",
        "<script>",
        "document.getElementById('btn-analyze').addEventListener('click', function(){",
        "  var url = document.getElementById('planning-url').value.trim();",
        "  var err = document.getElementById('error-status');",
        "  err.style.display = 'none';",
        "  if(!url){ err.textContent='❌ Merci de saisir une URL.'; err.style.display='block'; return; }",
        "  window.location.href = '/analyse-planning?u=' + encodeURIComponent(url);",
        "});",
        "</script>",
    ]
    return HTMLResponse("\n".join(html_lines), status_code=200)

# ---------- UI inline : page d’analyse ----------
@app.get("/analyse-planning", include_in_schema=False)
async def analyse_planning_page(_: Request):
    html_lines = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>Analyse en cours… • CSI</title>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<link rel='icon' href='data:,'>",
        "<style>",
        ":root{--bg:#0b1020;--card:#111833;--text:#e6e9f2;--muted:#9aa3b2;--accent:#6aa1ff;--ok:#22c55e;--err:#ef4444}",
        "*{box-sizing:border-box} body{margin:0;background:linear-gradient(180deg,#0b1020,#0e1630);}",
        ".wrap{max-width:1000px;margin:48px auto;padding:0 20px;color:var(--text);font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}",
        ".card{background:var(--card);border:1px solid #1b254a;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.3);padding:24px}",
        "h1{margin:0 0 12px;font-size:26px} p.muted{color:var(--muted);margin:0 0 16px}",
        ".row{display:flex;gap:12px;margin:10px 0 20px}",
        "button{cursor:pointer;border:1px solid #2a3a75;background:#1a2a6a;color:#eaf1ff;padding:10px 14px;border-radius:10px}",
        ".err{color:var(--err)} .ok{color:var(--ok)}",
        "table{width:100%;border-collapse:collapse;margin-top:10px}",
        "th,td{border:1px solid #223166;padding:8px;text-align:left}",
        "th{background:#182455}",
        ".spinner{display:inline-block;width:16px;height:16px;border:2px solid #6aa1ff;border-right-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;vertical-align:middle;margin-right:8px}",
        "@keyframes spin{to{transform:rotate(360deg)}}",
        "a{color:var(--accent);text-decoration:none}",
        "</style>",
        "<div class='wrap'><div class='card'>",
        "<h1>Analyse des plannings</h1>",
        "<p class='muted' id='src'></p>",
        "<div id='status'><span class='spinner'></span> Analyse en cours…</div>",
        "<div id='error' class='err' style='display:none'></div>",
        "<div id='result' style='display:none'>",
        "<h2 style='margin-top:10px'>Résultat</h2>",
        "<div id='meta' class='muted'></div>",
        "<h3 style='margin-top:18px'>Constats</h3>",
        "<ul id='findings'></ul>",
        "<h3 style='margin-top:18px'>Aperçu (10 premières lignes)</h3>",
        "<div id='preview'></div>",
        "<div class='row'>",
        "<button id='btn-retry'>Ré-analyser</button>",
        "<a href='/' style='align-self:center'>← Retour</a>",
        "<a href='/docs' target='_blank' style='align-self:center'>Docs API →</a>",
        "</div>",
        "</div></div></div>",
        "<script>",
        "var qs=new URLSearchParams(location.search);",
        "var url=qs.get('u');",
        "document.getElementById('src').textContent = url ? ('Source : ' + url) : 'Aucune URL fournie.';",
        "async function runAnalysis(){",
        "  var status=document.getElementById('status');",
        "  var error=document.getElementById('error');",
        "  var result=document.getElementById('result');",
        "  error.style.display='none'; result.style.display='none'; status.style.display='block';",
        "  if(!url){ error.textContent='Aucune URL reçue. Retour à l’accueil.'; error.style.display='block'; status.style.display='none'; return; }",
        "  try{",
        "    var resp = await fetch('/plannings/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url})});",
        "    var json = await resp.json();",
        "    if(!resp.ok || !json.ok){ error.textContent=(json && json.message) ? json.message : 'Analyse impossible.'; error.style.display='block'; status.style.display='none'; return; }",
        "    status.style.display='none'; result.style.display='block';",
        "    var meta=document.getElementById('meta'); var findings=document.getElementById('findings'); var preview=document.getElementById('preview');",
        "    meta.textContent='Lignes : ' + ((json.data && json.data.meta && json.data.meta.rows) || '?');",
        "    findings.innerHTML='';",
        "    (json.data && json.data.findings ? json.data.findings : []).forEach(function(f){",
        "      var li=document.createElement('li'); li.textContent=((f.type?'['+f.type+'] ':'')+(f.message||JSON.stringify(f))); findings.appendChild(li);",
        "    });",
        "    if(!json.data || !json.data.findings || json.data.findings.length===0){ findings.innerHTML='<li>Aucun constat particulier.</li>'; }",
        "    var records=(json.data && json.data.preview) ? json.data.preview : [];",
        "    if(records.length===0){ preview.innerHTML=\"<p class='muted'>Aucun aperçu disponible.</p>\"; }",
        "    else{",
        "      var cols=Object.keys(records[0]);",
        "      var html=['<table><thead><tr>'];",
        "      cols.forEach(function(c){ html.push('<th>'+c+'</th>'); });",
        "      html.push('</tr></thead><tbody>');",
        "      records.forEach(function(r){ html.push('<tr>'); cols.forEach(function(c){ html.push('<td>'+(r[c]!==undefined && r[c]!==null ? r[c] : '')+'</td>'); }); html.push('</tr>'); });",
        "      html.push('</tbody></table>');",
        "      preview.innerHTML=html.join('');",
        "    }",
        "  }catch(e){ error.textContent=e.message||'Erreur réseau.'; error.style.display='block'; status.style.display='none'; }",
        "}",
        "document.getElementById('btn-retry').addEventListener('click', runAnalysis);",
        "runAnalysis();",
        "</script>",
    ]
    return HTMLResponse("\n".join(html_lines), status_code=200)

# ---------- Page de test optionnelle ----------
@app.get("/_landing", include_in_schema=False)
async def landing():
    return HTMLResponse("<h1>CSI API</h1><p>Service en ligne ✅</p><p><a href='/'>UI</a> • <a href='/docs'>Docs</a></p>")

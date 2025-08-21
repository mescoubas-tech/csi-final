# app/main.py
VERSION = "CSI-2.2.1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.plannings.router import router as planning_router

VERSION = "CSI-2.2.0-inline"

app = FastAPI(title="CSI API", version=VERSION)

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

# Health: montre aussi la version pour vérifier le déploiement
@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok", "version": VERSION}
    import time
START_TS = time.time()

@app.get("/health", include_in_schema=False)
async def health():
    return {
        "status": "ok",
        "version": VERSION,
        "uptime_s": int(time.time() - START_TS),
    }

# UI inline (page d’accueil)
@app.get("/", include_in_schema=False)
async def home():
    html = (
        "<!doctype html><meta charset='utf-8'>"
        "<title>CSI • Analyse des plannings</title>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<link rel='icon' href='data:,'>"
        "<style>"
        "body{margin:0;background:linear-gradient(180deg,#0b1020,#0e1630);font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#e6e9f2}"
        ".wrap{max-width:880px;margin:48px auto;padding:0 20px}"
        ".card{background:#111833;border:1px solid #1b254a;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.3);padding:24px}"
        "h1{margin:0 0 12px;font-size:28px}"
        "label{display:block;margin:12px 0 6px;color:#c8d2ea}"
        "input[type=url]{width:100%;padding:12px 14px;border-radius:12px;border:1px solid #26325f;background:#0d1330;color:#eaf1ff;outline:none}"
        ".row{display:flex;gap:12px;margin-top:16px}"
        "button{cursor:pointer;border:1px solid #2a3a75;background:#1a2a6a;color:#eaf1ff;padding:12px 16px;border-radius:12px}"
        ".muted{color:#9aa3b2}.err{color:#ef4444;display:none;margin-top:8px}"
        ".ver{font-size:12px;color:#9aa3b2;margin-top:10px}"
        "a{color:#6aa1ff;text-decoration:none}"
        "</style>"
        "<div class='wrap'><div class='card'>"
        "<h1>Analyse des plannings</h1>"
        "<p class='muted'>Colle l’URL du planning puis clique <b>Analyser</b>.</p>"
        "<label for='planning-url'>URL du planning</label>"
        "<input id='planning-url' type='url' placeholder='https://exemple.tld/planning' />"
        "<div class='row'>"
        "<button id='btn-analyze'>Analyser</button>"
        "<a href='/docs' target='_blank'>Docs API →</a>"
        "</div>"
        "<div id='error-status' class='err'></div>"
        f"<div class='ver'>Version: {VERSION}</div>"
        "</div></div>"
        "<script>"
        "document.getElementById('btn-analyze').addEventListener('click',function(){"
        " var url=document.getElementById('planning-url').value.trim();"
        " var err=document.getElementById('error-status'); err.style.display='none';"
        " if(!url){err.textContent='❌ Merci de saisir une URL.';err.style.display='block';return;}"
        " window.location.href='/analyse-planning?u='+encodeURIComponent(url);"
        "});"
        "</script>"
    )
    return HTMLResponse(html, status_code=200)

# UI inline (page d’analyse)
@app.get("/analyse-planning", include_in_schema=False)
async def analyse_planning_page():
    html = (
        "<!doctype html><meta charset='utf-8'>"
        "<title>Analyse • CSI</title>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<link rel='icon' href='data:,'>"
        "<style>"
        "body{margin:0;background:linear-gradient(180deg,#0b1020,#0e1630);font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#e6e9f2}"
        ".wrap{max-width:1000px;margin:48px auto;padding:0 20px}"
        ".card{background:#111833;border:1px solid #1b254a;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.3);padding:24px}"
        "h1{margin:0 0 12px;font-size:26px}.muted{color:#9aa3b2}"
        ".row{display:flex;gap:12px;margin:10px 0 20px}"
        "button{cursor:pointer;border:1px solid #2a3a75;background:#1a2a6a;color:#eaf1ff;padding:10px 14px;border-radius:10px}"
        ".err{color:#ef4444}.ok{color:#22c55e}"
        "table{width:100%;border-collapse:collapse;margin-top:10px}"
        "th,td{border:1px solid #223166;padding:8px;text-align:left} th{background:#182455}"
        ".spinner{display:inline-block;width:16px;height:16px;border:2px solid #6aa1ff;border-right-color:transparent;border-radius:50%;animation:spin .8s linear infinite;vertical-align:middle;margin-right:8px}"
        "@keyframes spin{to{transform:rotate(360deg)}}" 
        "a{color:#6aa1ff;text-decoration:none}"
        "</style>"
        "<div class='wrap'><div class='card'>"
        "<h1>Analyse des plannings</h1>"
        "<p class='muted' id='src'></p>"
        "<div id='status'><span class='spinner'></span> Analyse en cours…</div>"
        "<div id='error' class='err' style='display:none'></div>"
        "<div id='result' style='display:none'>"
        "<h2 style='margin-top:10px'>Résultat</h2>"
        "<div id='meta' class='muted'></div>"
        "<h3 style='margin-top:18px'>Constats</h3><ul id='findings'></ul>"
        "<h3 style='margin-top:18px'>Aperçu (10 premières lignes)</h3><div id='preview'></div>"
        "<div class='row'>"
        "<button id='btn-retry'>Ré-analyser</button>"
        "<a href='/'>← Retour</a> <a href='/docs' target='_blank'>Docs API →</a>"
        "</div></div></div></div>"
        "<script>"
        "var qs=new URLSearchParams(location.search);var url=qs.get('u');"
        "document.getElementById('src').textContent=url?('Source : '+url):'Aucune URL fournie.';"
        "async function run(){"
        " var status=document.getElementById('status'),error=document.getElementById('error'),result=document.getElementById('result');"
        " error.style.display='none';result.style.display='none';status.style.display='block';"
        " if(!url){error.textContent='Aucune URL reçue.';error.style.display='block';status.style.display='none';return;}"
        " try{"
        "  var resp=await fetch('/plannings/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url})});"
        "  var json=await resp.json();"
        "  if(!resp.ok||!json.ok){error.textContent=(json&&json.message)?json.message:'Analyse impossible.';error.style.display='block';status.style.display='none';return;}"
        "  status.style.display='none';result.style.display='block';"
        "  var meta=document.getElementById('meta'),findings=document.getElementById('findings'),preview=document.getElementById('preview');"
        "  meta.textContent='Lignes : '+((json.data&&json.data.meta&&json.data.meta.rows)||'?');"
        "  findings.innerHTML='';(json.data&&json.data.findings?json.data.findings:[]).forEach(function(f){"
        "    var li=document.createElement('li');li.textContent=((f.type?'['+f.type+'] ':'')+(f.message||JSON.stringify(f)));findings.appendChild(li);"
        "  });if(!json.data||!json.data.findings||json.data.findings.length===0){findings.innerHTML='<li>Aucun constat particulier.</li>';}"
        "  var rows=(json.data&&json.data.preview)||[];if(rows.length===0){preview.innerHTML=\"<p class='muted'>Aucun aperçu disponible.</p>\";}else{"
        "    var cols=Object.keys(rows[0]);var html=['<table><thead><tr>'];cols.forEach(function(c){html.push('<th>'+c+'</th>')});"
        "    html.push('</tr></thead><tbody>');rows.forEach(function(r){html.push('<tr>');cols.forEach(function(c){html.push('<td>'+(r[c]??'')+'</td>')});html.push('</tr>')});"
        "    html.push('</tbody></table>');preview.innerHTML=html.join('');}"
        " }catch(e){error.textContent=e.message||'Erreur réseau.';error.style.display='block';status.style.display='none';}"
        "}"
        "document.getElementById('btn-retry').addEventListener('click',run);run();"
        "</script>"
    )
    return HTMLResponse(html, status_code=200)

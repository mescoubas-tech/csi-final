from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.plannings.router import router as planning_router

app = FastAPI(title="CSI API", version="2.0.0")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None

app.include_router(planning_router)

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
async def home(request: Request):
    index_path = TEMPLATES_DIR / "index.html"
    if templates and index_path.exists():
        return templates.TemplateResponse("index.html", {"request": request})
    html_parts = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>CSI API</title>",
        "<style>body{font:16px/1.6 system-ui;padding:32px}</style>",
        "<h1>CSI API</h1>",
        "<p>UI non trouvée (app/templates/index.html absent).</p>",
        "<ul>",
        "<li>Vérifie que <code>app/templates/index.html</code> est commité.</li>",
        "<li>Vérifie que <code>app/static/</code> existe.</li>",
        "<li><a href='/docs'>Docs OpenAPI</a></li>",
        "</ul>",
    ]
    return HTMLResponse("\n".join(html_parts), status_code=200)

@app.get("/analyse-planning", include_in_schema=False)
async def analyse_planning_page(request: Request):
    page_path = TEMPLATES_DIR / "analyse_planning.html"
    if templates and page_path.exists():
        return templates.TemplateResponse("analyse_planning.html", {"request": request})
    return HTMLResponse(
        "<p>Page d’analyse introuvable (app/templates/analyse_planning.html).</p>",
        status_code=200,
    )

@app.get("/_landing", include_in_schema=False)
async def landing():
    return HTMLResponse(
        "<h1>CSI API</h1><p>Service en ligne ✅</p><p><a href='/'>UI</a> • <a href='/docs'>Docs</a></p>"
    )

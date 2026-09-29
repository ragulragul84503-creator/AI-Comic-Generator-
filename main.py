"""
ComicCraft — AI Comic Story Creator
FastAPI Application Entrypoint
"""

import os
import time
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.story_generator import (
    generate_comic,
    get_sample_comic,
    SURPRISE_PROMPTS,
    SAMPLE_COMICS_DATA
)
from services.image_generator import (
    generate_panel_illustration,
    generate_style_preview_image,
    STYLE_PRESETS,
    SETTING_SCENERY
)
from services.pdf_generator import generate_comic_pdf, PDF_OUTPUT_DIR

app = FastAPI(
    title="ComicCraft — AI Comic Story Creator",
    description="Turn simple ideas into 5-panel illustrated comics with AI",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Jinja2 Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Pydantic Request Models
class ComicGenerationRequest(BaseModel):
    story_prompt: str = Field(..., min_length=5, max_length=1000)
    character_name: str = Field(..., min_length=1, max_length=100)
    setting: str = Field(..., min_length=2, max_length=100)
    custom_setting: Optional[str] = None
    tone: str = Field(default="Adventure")
    art_style: str = Field(default="Comic Book")
    panels_count: int = Field(default=5, ge=4, le=8)


class TestImageRequest(BaseModel):
    prompt: str = Field(..., min_length=2)
    art_style: str = Field(default="Comic Book")
    setting: Optional[str] = "City"
    character_name: Optional[str] = "Hero"


class ExportPdfRequest(BaseModel):
    comic_data: Dict[str, Any]


# ==========================================
# PAGE ROUTES
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """
    Renders the unified ComicCraft web application.
    Includes Landing Hero, Create Workspace, Comic Preview, How It Works,
    Features, Sample Gallery, About Section, and Modal Systems.
    """
    style_list = []
    for name, data in STYLE_PRESETS.items():
        style_list.append({
            "name": name,
            "badge": data["badge"],
            "accent": data["accent"],
            "aesthetic": data["aesthetic"],
            "preview_image": generate_style_preview_image(name)
        })

    tones = [
        {"name": "Adventure", "icon": "🧭", "desc": "Heroic quests and brave exploration"},
        {"name": "Funny", "icon": "😂", "desc": "Slapstick humor and witty banter"},
        {"name": "Dramatic", "icon": "⚡", "desc": "High stakes, tension, and emotional depth"},
        {"name": "Light-hearted", "icon": "☀️", "desc": "Cheerful, uplifting, feel-good moments"},
        {"name": "Emotional", "icon": "❤️", "desc": "Touching relationships and heartfelt choices"},
        {"name": "Mysterious", "icon": "🔍", "desc": "Puzzles, cryptids, and enigmatic secrets"},
        {"name": "Epic", "icon": "👑", "desc": "Colossal battles and mythic horizons"}
    ]

    settings = [
        "Enchanted Forest",
        "School",
        "City",
        "Space",
        "Future World",
        "Medieval Kingdom",
        "Custom"
    ]

    # Sample comics summaries
    samples = []
    for sid, sdata in SAMPLE_COMICS_DATA.items():
        samples.append({
            "id": sid,
            "title": sdata["title"],
            "character": sdata["character"],
            "setting": sdata["setting"],
            "tone": sdata["tone"],
            "art_style": sdata["art_style"],
            "summary": sdata["summary"],
            "badge": sdata["badge"],
            "icon": sdata["thumbnail_icon"]
        })

    is_live_gemini = bool(os.getenv("GEMINI_API_KEY"))
    is_live_stability = bool(os.getenv("STABILITY_API_KEY"))

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "styles": style_list,
            "tones": tones,
            "settings": settings,
            "samples": samples,
            "is_live_gemini": is_live_gemini,
            "is_live_stability": is_live_stability
        }
    )


@app.get("/export-success", response_class=HTMLResponse)
async def export_success_page(
    request: Request,
    title: Optional[str] = "Your AI Comic",
    pdf_url: Optional[str] = None
):
    """
    Dedicated Export Success page for direct links or redirect flows.
    """
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "title": title,
            "pdf_url": pdf_url or "#"
        }
    )


# ==========================================
# API ENDPOINTS
# ==========================================

@app.post("/generate-comic/json")
async def generate_comic_json(req: ComicGenerationRequest):
    """
    Main comic generation JSON API.
    Builds outline, dialogue, illustrations, and structured comic document.
    """
    try:
        final_setting = req.custom_setting if (req.setting == "Custom" and req.custom_setting) else req.setting
        
        comic = generate_comic(
            story_prompt=req.story_prompt,
            character_name=req.character_name,
            setting=final_setting,
            tone=req.tone,
            art_style=req.art_style,
            panels_count=req.panels_count
        )
        return JSONResponse(status_code=200, content={
            "success": True,
            "comic": comic
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": f"Failed to generate comic: {str(e)}"
        })


@app.post("/generate")
async def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    custom_setting: Optional[str] = Form(None),
    tone: str = Form("Adventure"),
    art_style: str = Form("Comic Book"),
    panels_count: int = Form(5)
):
    """
    Form submission handler compatible with the original project endpoint.
    Returns JSON response for asynchronous frontend or handles direct requests.
    """
    final_setting = custom_setting if (setting == "Custom" and custom_setting) else setting

    try:
        comic = generate_comic(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=final_setting,
            tone=tone,
            art_style=art_style,
            panels_count=panels_count
        )
        return JSONResponse(status_code=200, content={
            "success": True,
            "comic": comic
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e)
        })


@app.post("/test-image")
async def test_image_endpoint(req: TestImageRequest):
    """
    Test illustration generation for an individual prompt or style.
    """
    try:
        res = generate_panel_illustration(
            panel_number=1,
            panel_title="Style Test",
            character_name=req.character_name or "Hero",
            setting=req.setting or "City",
            tone="Adventure",
            art_style=req.art_style,
            scene_description=req.prompt,
            image_prompt=req.prompt
        )
        return JSONResponse(status_code=200, content={
            "success": True,
            "image": res["image_url"],
            "source": res.get("source", "Vector AI Engine"),
            "mode": res.get("mode", "demo")
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.post("/api/export-pdf")
async def api_export_pdf(req: ExportPdfRequest):
    """
    Generates a full comic book PDF on the server using fpdf2 and returns the download URL.
    """
    try:
        pdf_path = generate_comic_pdf(req.comic_data)
        filename = os.path.basename(pdf_path)
        download_url = f"/download-pdf/{filename}"
        return JSONResponse(status_code=200, content={
            "success": True,
            "filename": filename,
            "pdf_url": download_url
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": f"PDF Export Failed: {str(e)}"
        })


@app.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    """
    Streams the generated PDF file for download or in-browser preview.
    """
    safe_name = os.path.basename(filename)
    file_path = os.path.join(PDF_OUTPUT_DIR, safe_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested PDF file not found.")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_name,
        headers={"Content-Disposition": f'inline; filename="{safe_name}"'}
    )


@app.get("/api/sample-comics/{sample_id}")
async def api_sample_comic(sample_id: str):
    """
    Returns complete comic panels for a curated Made With ComicCraft story.
    """
    comic = get_sample_comic(sample_id)
    if not comic:
        raise HTTPException(status_code=404, detail="Sample comic not found.")
    return JSONResponse(status_code=200, content={"success": True, "comic": comic})


@app.get("/api/surprise-prompt")
async def api_surprise_prompt():
    """
    Returns a creative pre-configured surprise prompt.
    """
    import random
    choice = random.choice(SURPRISE_PROMPTS)
    return JSONResponse(status_code=200, content=choice)


@app.get("/api/health")
async def health_check():
    """
    Liveness and operational status endpoint.
    """
    return {
        "status": "healthy",
        "app": "ComicCraft AI",
        "gemini_api_active": bool(os.getenv("GEMINI_API_KEY")),
        "stability_api_active": bool(os.getenv("STABILITY_API_KEY")),
        "engine": "Hybrid (Live API / Fallback Vector Engine)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

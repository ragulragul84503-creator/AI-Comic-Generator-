# ComicCraft — AI Comic Story Creator

ComicCraft is a production-quality web application that transforms simple story ideas into complete, multi-panel illustrated comic books with sequential storylines, character dialogue, narrator captions, and high-resolution PDF export.

---

## 🌟 Key Features

- **Sequential AI Story Synthesis**: Automatically crafts 4, 5, 6, or 8-panel story arcs (Setup, Inciting Discovery, Rising Action, Climax, Resolution).
- **Character Dialogue & Narration**: Generates voiceover narrative captions and in-character speech balloons.
- **7 Distinct Art Styles**:
  - **Anime** (Cel-shaded, luminous lighting)
  - **Comic Book** (Bold ink, Ben-Day dot screentone)
  - **Cartoon** (Rounded fluid shapes, saturated hues)
  - **Pixel Art** (16-bit retro arcade aesthetic)
  - **Realistic** (Cinematic chiaroscuro graphic novel)
  - **Manga** (High-contrast ink, speed lines)
  - **Fantasy** (Ethereal runes, mystical glowing dust)
- **7 Story Tones**: Adventure, Funny, Dramatic, Light-hearted, Emotional, Mysterious, Epic.
- **Multi-Setting Support**: Enchanted Forest, School, City, Space, Future World, Medieval Kingdom, or custom user-defined settings.
- **Interactive Two-Column Workspace**: Left-hand configuration form with character counters, inline validation, and "Surprise Me" prompt generator; Right-hand reactive live preview.
- **Multi-Stage AI Generation Experience**: Animated comic book loader with live progress bar and checklist (Outline &rarr; Dialogue &rarr; Artwork &rarr; PDF Preparation).
- **Comic Preview Canvas**: Sequential comic frames with yellow narration captions, dialogue balloons, inline text editor, and image export.
- **Professional PDF Export**: Built using `fpdf2` and `Pillow`, producing print-ready comic book documents with titles, issue headers, illustrations, captions, and speech tags.
- **Celebration Confetti & Export Success**: Zero-dependency canvas confetti burst and dedicated success screen.
- **Robust Fallback & Demo Mode**: Fully functional offline or without API keys using high-resolution procedural vector rendering, with seamless live API integration for Google Gemini and Stability AI when keys are present.

---

## 🏗️ Architecture & Conceptual Tech Stack

```text
User Input (Prompt, Character, Setting, Tone, Style)
   │
   ▼
FastAPI Application (Python 3.11)
   ├── Story Engine (Gemini 1.5 Flash Outline + Gemini Pro Narration/Dialogue / Procedural Engine)
   ├── Image Engine (Stable Diffusion SDXL / Procedural Vector Illustration Engine)
   └── Document Engine (fpdf2 + Pillow Comic Formatter)
   │
   ▼
Interactive Frontend (HTML5, Modern CSS, Jinja2, Responsive JavaScript)
   ├── Live Reactive Workspace
   ├── Stage-by-Stage Generation Modal
   ├── Interactive Panel Canvas (Inline Edit & Regen)
   └── PDF Export & Celebration View
```

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `jinja2`, `python-multipart`, `fpdf2`, `pillow`, `pydantic`, `requests`

### 2. Launching the Server
Simply run the included `run.bat` or run via terminal:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
Visit:
```
http://127.0.0.1:8000
```

---

## 🔑 Optional API Keys (Live Production Mode)

ComicCraft works out-of-the-box in **Demo / Fallback Studio Mode** without any keys. To enable live cloud generative AI models, set these environment variables:

```powershell
$env:GEMINI_API_KEY = "your_google_gemini_api_key"
$env:STABILITY_API_KEY = "your_stability_ai_api_key"
```

---

## 📡 API Endpoints

- `GET /` — Main web application interface
- `POST /generate-comic/json` — Primary JSON generation endpoint
- `POST /generate` — Form-compatible comic generation endpoint
- `POST /api/export-pdf` — Compiles comic data into an A4 comic book PDF
- `GET /download-pdf/{filename}` — Streams generated PDF file
- `POST /test-image` — Generates a single panel illustration or style test
- `GET /api/sample-comics/{id}` — Returns complete panels for sample stories
- `GET /api/surprise-prompt` — Returns a creative pre-configured prompt
- `GET /export-success` — Standalone export celebration page
- `GET /api/health` — Service healthcheck

---

## 🎨 Design Philosophy
- **Colors**: Near-black charcoal (`#0D0F14`), Bright Comic Yellow (`#FFE600`), White (`#FFFFFF`), Electric Blue (`#38BDF8`), Purple (`#8B5CF6`).
- **Typography**: Bangers (Comic headers), Comic Neue (Captions & Dialogue), Plus Jakarta Sans (SaaS UI controls).
- **Styling**: Modern neo-brutalist comic borders (`border: 3px solid #000; box-shadow: 6px 6px 0px #000;`), subtle halftone screentones, and speech balloon tails.

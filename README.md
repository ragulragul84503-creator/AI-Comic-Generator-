# ComicCraft - AI Comic Story Creator

## Project Description
ComicCraft is an AI-powered creative web application that transforms a user's simple story idea into a complete, multi-panel comic book. By connecting generative AI narrative design with visual comic illustration and automated document formatting, ComicCraft produces:
- **5-Panel Story Outline**: Chronologically paced narrative beats (Setup, Discovery, Conflict, Climax, Resolution).
- **Narration**: Evocative narrator captions formatted in classic comic caption boxes.
- **Character Dialogue**: Contextual character speech formatted in dynamic comic speech bubbles.
- **Comic Illustrations**: High-resolution, stylized artwork rendered for every panel matching the selected art style and setting.
- **Multi-Panel Preview**: A sequential comic reading canvas with live hover actions and in-browser caption/dialogue editing.
- **PDF Export**: Print-ready comic book documents generated using FPDF with titles, character metadata, panels, and running page numbers.

The application includes a fully functional **Demo & Fallback Studio Mode** that produces complete comics with high-resolution vector comic art without requiring active API keys, while also seamlessly connecting to live Google Gemini and Hugging Face / Stability AI services when keys are provided.

---

## Features
- **AI Story Generation**: Generates coherent, dramatic comic story arcs from brief text prompts.
- **5-Panel Comic Generation**: Structured 5-panel story progression (also supports 4, 6, and 8 panels).
- **Character Customization**: Name your protagonist and watch dialogue dynamically adapt to their persona.
- **Setting Selection**: Choose from curated worlds (*Enchanted Forest, School, City, Space, Future World, Medieval Kingdom*) or specify custom locations.
- **Story Tone Selection**: Tailor narrative mood across 7 tones (*Adventure, Funny, Dramatic, Light-hearted, Emotional, Mysterious, Epic*).
- **Art Style Selection**: Visual preview selection for 7 distinct art aesthetics (*Anime, Comic Book, Cartoon, Pixel Art, Realistic Graphic Novel, Manga, Fantasy*).
- **AI-Generated Illustrations**: Tailored artwork for each panel with character silhouettes, atmospheric lighting, and scene framing.
- **Comic Preview**: Review complete stories sequentially, edit dialogue and narration in real time, or regenerate individual scene artwork.
- **PDF Export**: Single-click PDF export delivering a beautifully formatted multi-page comic book.
- **FastAPI Backend**: Asynchronous Python backend with structured validation, clean error handling, and RESTful endpoints.
- **Responsive Frontend**: Modern comic-inspired neo-brutalist and SaaS UI, fully responsive across mobile, tablet, and desktop devices.
- **Surprise Me Prompt Generator**: Instant one-click inspiration generator populating creative story concepts.
- **Export Success Celebration**: Visual celebration view featuring confetti animations.

---

## Technology Stack
- **Python**: Core backend programming language (3.10+).
- **FastAPI**: Modern, high-performance web framework for APIs and page routing.
- **Jinja2**: Server-side templating engine for seamless HTML rendering.
- **Gemini AI**: Google Gemini models (Gemini Flash for outline synthesis, Gemini Pro for narration and dialogue).
- **Stable Diffusion / Hugging Face Diffusers**: Text-to-image AI generation for comic illustrations (with vector fallback engine).
- **Pillow**: Python imaging library for raster handling, image formatting, and asset optimization.
- **FPDF (fpdf2)**: Multi-page document generation engine compiling comic layouts, frames, and dialogue boxes into PDF.
- **HTML**: Accessible, semantic HTML5 structure.
- **CSS**: Custom responsive design system featuring comic halftone patterns, bold panel borders, and speech balloon tails.
- **JavaScript**: Client-side state machine handling form validation, real-time live preview, multi-stage loading modals, and PDF download flows.

---

## Project Structure
```text
AI-Comic-Generator-/
│
├── main.py                     # FastAPI application entrypoint & REST API routes
│
├── services/
│   ├── story_generator.py      # Outline, dialogue, & narration engine (Gemini & procedural)
│   ├── image_generator.py      # Art style generator (Stable Diffusion & vector engine)
│   └── pdf_generator.py        # FPDF comic book layout compiler & document exporter
│
├── templates/
│   ├── base.html               # Jinja2 base layout with global navigation & footer
│   ├── index.html              # Main application view (Hero, Workspace, Reader, Showcase)
│   └── export_success.html     # Dedicated export success & celebration screen
│
├── static/
│   ├── css/
│   │   └── style.css           # Neo-brutalist comic SaaS design system & responsive rules
│   └── js/
│       ├── app.js              # Application state machine, live preview & API client
│       └── confetti.js         # Canvas confetti animation for export success
│
├── generated_pdfs/             # Output directory for exported comic PDFs (.gitkeep tracked)
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables and API keys
├── .gitignore                  # Git exclusions for secrets, bytecode, and temporary files
├── run.bat                     # Windows one-click server launch script
└── README.md                   # Complete project documentation
```

---

## Installation

### 1. Prerequisites
- Python 3.10, 3.11, or newer
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/ragulragul84503-creator/AI-Comic-Generator-.git
cd AI-Comic-Generator-
```

### 3. Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Variables
ComicCraft runs in **Demo / Fallback Studio Mode** without any API keys required. To enable live cloud generative AI models, copy `.env.example` to `.env` and provide your API keys:

```bash
cp .env.example .env
```

Configure your keys in `.env`:
```ini
# Google Gemini API Key (Gemini Flash outline & Gemini Pro narration/dialogue)
GEMINI_API_KEY=your_api_key_here

# Hugging Face or Stability AI Key (for live cloud image generation)
HF_API_KEY=your_api_key_here
STABILITY_API_KEY=your_api_key_here

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=True
```

> [!WARNING]
> Never commit your real `.env` file or API keys to GitHub. The `.gitignore` file is configured to exclude all `.env` files.

---

## Running the Project

### Start the FastAPI Server
To run the server with auto-reload:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or on Windows, simply double-click:
```bat
run.bat
```

### Access the Application
- **Web Interface**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative API Documentation (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the main ComicCraft web interface |
| `POST` | `/generate-comic/json` | Primary JSON endpoint to generate structured comic outline, dialogue, and artwork |
| `POST` | `/generate` | Form-encoded comic generation endpoint |
| `POST` | `/api/export-pdf` | Compiles comic data into a formatted A4 PDF file |
| `GET` | `/download-pdf/{filename}` | Streams generated PDF file for download or preview |
| `POST` | `/test-image` | Generates a single panel illustration or style test |
| `GET` | `/api/sample-comics/{id}` | Returns pre-curated sample comics (e.g. *fox-portal*, *last-space-explorer*, *mystery-midnight*) |
| `GET` | `/api/surprise-prompt` | Generates random creative prompt parameters |
| `GET` | `/export-success` | Standalone export celebration page |
| `GET` | `/api/health` | Operational health and API status check |

---

## Usage
The end-to-end user journey follows these steps:

1. **Enter Story Details**:
   - Provide a story prompt (e.g., *"A brave fox discovers a glowing portal inside an enchanted forest..."*).
   - Enter the main character's name (e.g., *"Leo"*).
   - Select a setting, story tone, and visual art style.
   - *(Optional)* Click `🎲 Surprise Me` to auto-populate creative story ideas.
2. **Click "Generate My Comic"**:
   - The animated AI generation modal appears, tracking live progress across 6 distinct stages.
3. **Review the Comic Preview**:
   - Review all 5 panels sequentially with their titles, illustrations, narration captions, and speech balloons.
   - Hover over any panel to regenerate the illustration, edit the text, or download the image.
4. **Export as PDF**:
   - Click `📥 Download PDF` to compile and download your comic book.
   - An export celebration view appears with confetti and quick re-download links.

---

## Future Improvements
- **User Accounts & Authentication**: Enable user sign-in to save and manage comics.
- **Comic Libraries & Community Feed**: Public gallery for creators to share and vote on stories.
- **Multi-Page & Long-Form Stories**: Support for 12, 24, and multi-chapter graphic novels.
- **Saved Projects & Drafts**: LocalStorage and database persistence for unfinished stories.
- **More Art Styles**: Support for Watercolor, Cyberpunk Synthwave, Oil Painting, and Claymation.
- **Custom Character Consistency**: Fine-tuned LoRA or IP-Adapter character embedding for identical character appearances across panels.
- **Cloud Deployment**: Production Dockerfile and Terraform scripts for AWS, GCP, or Hugging Face Spaces.

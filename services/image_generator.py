"""
ComicCraft Image Generation Service
Supports:
1. Stability AI / Stable Diffusion API (when STABILITY_API_KEY is configured)
2. High-fidelity Procedural Comic Illustration Engine (Demo/Fallback Mode)
   Generates rich, resolution-independent SVG comic illustrations with comic ink borders,
   halftone screentones, stylized backgrounds, atmospheric lighting, and character silhouettes
   tailored to the requested Art Style and Setting.
"""

import os
import re
import base64
import hashlib
from typing import Dict, Any, Optional

# Style metadata & color palettes
STYLE_PRESETS = {
    "Anime": {
        "accent": "#FF4B82",
        "bg_gradient": ("#1E1B4B", "#4338CA", "#EC4899"),
        "line_color": "#0F172A",
        "glow": "#F472B6",
        "aesthetic": "Vibrant anime cinematic lighting, cel-shaded tones, ethereal lens flares, crisp outlines",
        "badge": "Anime Shonen / Shojo"
    },
    "Comic Book": {
        "accent": "#FFE600",
        "bg_gradient": ("#0F172A", "#1E293B", "#F59E0B"),
        "line_color": "#000000",
        "glow": "#FBBF24",
        "aesthetic": "Bold American comic book ink, Ben-Day dot halftone shading, dramatic angular perspective",
        "badge": "Classic Modern Comic"
    },
    "Cartoon": {
        "accent": "#06B6D4",
        "bg_gradient": ("#164E63", "#0284C7", "#38BDF8"),
        "line_color": "#083344",
        "glow": "#67E8F9",
        "aesthetic": "Playful Saturday-morning cartoon, rounded fluid shapes, bold saturated hues, expressive action lines",
        "badge": "Cartoon Animation"
    },
    "Pixel Art": {
        "accent": "#10B981",
        "bg_gradient": ("#022C22", "#065F46", "#10B981"),
        "line_color": "#022C22",
        "glow": "#34D399",
        "aesthetic": "16-bit retro pixel art, dithering gradients, pixel grid definition, nostalgic arcade aesthetic",
        "badge": "16-Bit Retro Pixel"
    },
    "Realistic": {
        "accent": "#F59E0B",
        "bg_gradient": ("#1C1917", "#292524", "#78716C"),
        "line_color": "#0C0A09",
        "glow": "#D97706",
        "aesthetic": "Cinematic realism, high-dynamic-range chiaroscuro lighting, subtle atmospheric smoke, depth of field",
        "badge": "Cinematic Graphic Novel"
    },
    "Manga": {
        "accent": "#E2E8F0",
        "bg_gradient": ("#09090B", "#18181B", "#27272A"),
        "line_color": "#000000",
        "glow": "#FAFAFA",
        "aesthetic": "Authentic Japanese manga, high-contrast black & white screentone crosshatching, dynamic speed lines",
        "badge": "Seinen / Shonen Manga"
    },
    "Fantasy": {
        "accent": "#A855F7",
        "bg_gradient": ("#2E1065", "#581C87", "#9333EA"),
        "line_color": "#1E1B4B",
        "glow": "#C084FC",
        "aesthetic": "Ethereal high fantasy illustration, mystical runes, magical glowing dust, ornate gothic motifs",
        "badge": "Epic Mythic Fantasy"
    }
}

SETTING_SCENERY = {
    "Enchanted Forest": {
        "elements": ["ancient bioluminescent trees", "floating spore motes", "emerald canopy", "twisted roots", "glowing flora"],
        "primary_hue": "#064E3B",
        "secondary_hue": "#059669",
        "sky_color": "#022C22",
        "ambient": "mystical woodland whispers and glowing forest moss"
    },
    "School": {
        "elements": ["high school corridor lockers", "tall sunlit windows", "chalkboard banners", "school gate", "courtyard cherry blossoms"],
        "primary_hue": "#1E3A8A",
        "secondary_hue": "#3B82F6",
        "sky_color": "#93C5FD",
        "ambient": "bustling academy halls and late afternoon golden hour sunlight"
    },
    "City": {
        "elements": ["towering neon skyscraper spires", "rain-slicked streets", "holographic billboards", "steam vents", "glowing overpasses"],
        "primary_hue": "#0F172A",
        "secondary_hue": "#6366F1",
        "sky_color": "#1E1B4B",
        "ambient": "cyberpunk metropolis lights cutting through heavy night mist"
    },
    "Space": {
        "elements": ["distant spiral galaxies", "deep orbital spacecraft hull", "planetary rings", "meteor trails", "star nebula clouds"],
        "primary_hue": "#0B0F19",
        "secondary_hue": "#312E81",
        "sky_color": "#030712",
        "ambient": "silent cosmic void punctuated by radiant stellar nebulae"
    },
    "Future World": {
        "elements": ["floating magnetic sky-towers", "antigravity transit tubes", "solar crystal spires", "drone swarms", "neon sky-lanes"],
        "primary_hue": "#111827",
        "secondary_hue": "#0D9488",
        "sky_color": "#134E4A",
        "ambient": "hyper-advanced utopian metropolis with shimmering energy conduits"
    },
    "Medieval Kingdom": {
        "elements": ["towering stone fortress battlements", "fluttering royal pennants", "misty mountain peaks", "torchlit archways", "cobblestone ramparts"],
        "primary_hue": "#292524",
        "secondary_hue": "#B45309",
        "sky_color": "#451A03",
        "ambient": "majestic iron-and-stone stronghold against a dramatic dusk horizon"
    },
    "Custom": {
        "elements": ["dynamic dramatic landscape", "atmospheric horizon", "imposing architecture", "energy currents", "epic skies"],
        "primary_hue": "#18181B",
        "secondary_hue": "#8B5CF6",
        "sky_color": "#09090B",
        "ambient": "vivid customized world tailored to the narrative"
    }
}


def generate_panel_svg(
    panel_number: int,
    panel_title: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    scene_description: str,
    action_type: str = "action"
) -> str:
    """
    Generates a beautifully composed, scalable comic illustration SVG.
    Includes atmospheric gradients, landscape silhouettes, energy effects,
    comic speed lines, halftone dot overlays, and character presence.
    """
    style_info = STYLE_PRESETS.get(art_style, STYLE_PRESETS["Comic Book"])
    setting_info = SETTING_SCENERY.get(setting, SETTING_SCENERY["Custom"])

    c_glow = style_info["glow"]
    c_accent = style_info["accent"]
    g_start, g_mid, g_end = style_info["bg_gradient"]
    s_prim = setting_info["primary_hue"]
    s_sec = setting_info["secondary_hue"]

    # Deterministic hash for variation based on scene
    h_seed = int(hashlib.md5(f"{panel_number}_{panel_title}_{setting}_{art_style}".encode()).hexdigest()[:6], 16)
    float_offset = (h_seed % 30) - 15

    # Manga style is grayscale / high contrast
    is_manga = (art_style == "Manga")
    if is_manga:
        g_start, g_mid, g_end = ("#09090B", "#18181B", "#3F3F46")
        c_glow = "#FFFFFF"
        c_accent = "#E4E4E7"
        s_prim = "#18181B"
        s_sec = "#27272A"

    # Action stage styling based on panel number
    # 1: Establishing / Intro, 2: Encounter, 3: Conflict / Climax, 4: Pivot, 5: Resolution
    if panel_number == 1:
        badge_text = "ESTABLISHING SCENE"
        char_scale = 0.8
        char_x = 240
        speed_opacity = 0.05
    elif panel_number == 2:
        badge_text = "INCITING MOMENT"
        char_scale = 0.95
        char_x = 260
        speed_opacity = 0.15
    elif panel_number == 3:
        badge_text = "RISING ACTION"
        char_scale = 1.1
        char_x = 280
        speed_opacity = 0.35
    elif panel_number == 4:
        badge_text = "CLIMACTIC PEAK"
        char_scale = 1.25
        char_x = 290
        speed_opacity = 0.45
    else:
        badge_text = "EPIC RESOLUTION"
        char_scale = 1.0
        char_x = 270
        speed_opacity = 0.2

    # Scenery shapes depending on setting
    scenery_svg = ""
    if setting == "Enchanted Forest":
        scenery_svg = f"""
        <!-- Ancient Trees & Glowing Spores -->
        <path d="M -20 400 Q 80 180 120 120 Q 150 180 180 400 Z" fill="{s_prim}" opacity="0.85"/>
        <path d="M 420 400 Q 480 160 520 80 Q 560 160 620 400 Z" fill="{s_prim}" opacity="0.85"/>
        <path d="M 120 400 Q 200 240 240 180 Q 280 240 340 400 Z" fill="{s_sec}" opacity="0.5"/>
        <circle cx="160" cy="140" r="18" fill="{c_glow}" opacity="0.65" filter="url(#blur-glow)"/>
        <circle cx="480" cy="190" r="14" fill="{c_accent}" opacity="0.55" filter="url(#blur-glow)"/>
        <circle cx="280" cy="90" r="6" fill="#FFFFFF" opacity="0.8" filter="url(#blur-glow)"/>
        <!-- Mystical Portal Arch -->
        <ellipse cx="300" cy="270" rx="90" ry="130" fill="none" stroke="{c_glow}" stroke-width="4" stroke-dasharray="8 4" opacity="0.8" filter="url(#blur-glow)"/>
        <ellipse cx="300" cy="270" rx="75" ry="115" fill="none" stroke="{c_accent}" stroke-width="2" opacity="0.6"/>
        """
    elif setting == "Space":
        scenery_svg = f"""
        <!-- Planetary Sphere & Celestial Rings -->
        <circle cx="460" cy="140" r="90" fill="url(#planet-grad)" opacity="0.9"/>
        <ellipse cx="460" cy="140" rx="140" ry="25" fill="none" stroke="{c_accent}" stroke-width="5" transform="rotate(-20 460 140)" opacity="0.8"/>
        <!-- Star Field -->
        <circle cx="80" cy="60" r="2.5" fill="#FFFFFF" opacity="0.9"/>
        <circle cx="140" cy="110" r="1.5" fill="#FFFFFF" opacity="0.7"/>
        <circle cx="220" cy="40" r="3" fill="{c_glow}" opacity="0.9" filter="url(#blur-glow)"/>
        <circle cx="340" cy="80" r="2" fill="#FFFFFF" opacity="0.8"/>
        <circle cx="530" cy="260" r="1.5" fill="#FFFFFF" opacity="0.6"/>
        <!-- Spacecraft / Station silhouette -->
        <polygon points="60,260 140,240 180,265 140,290" fill="{s_sec}" opacity="0.8"/>
        <polygon points="140,250 200,265 140,280" fill="{c_glow}" opacity="0.4" filter="url(#blur-glow)"/>
        """
    elif setting == "City":
        scenery_svg = f"""
        <!-- Neon City Skyline -->
        <rect x="30" y="160" width="80" height="240" fill="{s_prim}" opacity="0.9"/>
        <rect x="130" y="100" width="100" height="300" fill="#090D16" opacity="0.95"/>
        <rect x="250" y="180" width="90" height="220" fill="{s_prim}" opacity="0.85"/>
        <rect x="360" y="120" width="110" height="280" fill="#090D16" opacity="0.95"/>
        <rect x="490" y="190" width="80" height="210" fill="{s_prim}" opacity="0.9"/>
        <!-- Neon Window Grids -->
        <line x1="150" y1="130" x2="210" y2="130" stroke="{c_glow}" stroke-width="2" opacity="0.7"/>
        <line x1="150" y1="160" x2="210" y2="160" stroke="{c_accent}" stroke-width="2" opacity="0.7"/>
        <line x1="380" y1="150" x2="450" y2="150" stroke="{c_glow}" stroke-width="2" opacity="0.6"/>
        <line x1="380" y1="180" x2="450" y2="180" stroke="{c_accent}" stroke-width="2" opacity="0.8"/>
        <!-- Holographic Beam -->
        <polygon points="180,100 230,0 240,0 185,100" fill="{c_glow}" opacity="0.3" filter="url(#blur-glow)"/>
        """
    elif setting == "Future World":
        scenery_svg = f"""
        <!-- Cybernetic Architecture & Spire Domes -->
        <path d="M 0 320 Q 150 220 300 240 Q 450 260 600 310 L 600 400 L 0 400 Z" fill="{s_prim}" opacity="0.9"/>
        <ellipse cx="300" cy="180" rx="180" ry="70" fill="none" stroke="{c_glow}" stroke-width="3" opacity="0.5"/>
        <line x1="300" y1="40" x2="300" y2="280" stroke="{c_accent}" stroke-width="4" opacity="0.8" filter="url(#blur-glow)"/>
        <!-- Flying transport vehicle -->
        <polygon points="120,120 180,110 200,125 140,135" fill="{c_glow}" opacity="0.7"/>
        <line x1="120" y1="125" x2="60" y2="128" stroke="{c_accent}" stroke-width="3" opacity="0.6" filter="url(#blur-glow)"/>
        """
    elif setting == "Medieval Kingdom":
        scenery_svg = f"""
        <!-- Castle Walls & Fortress Turrets -->
        <polygon points="80,180 80,240 140,240 140,180 120,150 100,150" fill="{s_prim}" opacity="0.9"/>
        <polygon points="460,160 460,240 540,240 540,160 510,130 490,130" fill="{s_prim}" opacity="0.9"/>
        <rect x="140" y="210" width="320" height="190" fill="{s_sec}" opacity="0.85"/>
        <path d="M 260 400 L 260 320 Q 300 290 340 320 L 340 400 Z" fill="#0C0A09"/>
        <!-- Torches / Banners -->
        <line x1="110" y1="150" x2="110" y2="110" stroke="#78716C" stroke-width="3"/>
        <polygon points="110,110 150,120 110,135" fill="{c_accent}" opacity="0.9"/>
        <circle cx="270" cy="320" r="5" fill="#F59E0B" filter="url(#blur-glow)"/>
        <circle cx="330" cy="320" r="5" fill="#F59E0B" filter="url(#blur-glow)"/>
        """
    elif setting == "School":
        scenery_svg = f"""
        <!-- High School Campus Hall & Archway -->
        <rect x="60" y="140" width="480" height="260" fill="{s_prim}" opacity="0.85"/>
        <rect x="120" y="170" width="70" height="110" fill="#E0F2FE" opacity="0.5"/>
        <rect x="230" y="170" width="70" height="110" fill="#E0F2FE" opacity="0.5"/>
        <rect x="340" y="170" width="70" height="110" fill="#E0F2FE" opacity="0.5"/>
        <rect x="450" y="170" width="70" height="110" fill="#E0F2FE" opacity="0.5"/>
        <polygon points="30,140 300,60 570,140" fill="{s_sec}" opacity="0.95"/>
        <!-- Sunbeam slant through windows -->
        <polygon points="150,170 280,400 210,400 120,200" fill="#FEF08A" opacity="0.25"/>
        """
    else:
        scenery_svg = f"""
        <!-- Dynamic Horizon Landscape -->
        <path d="M 0 300 Q 150 200 300 250 Q 450 300 600 240 L 600 400 L 0 400 Z" fill="{s_prim}" opacity="0.9"/>
        <circle cx="300" cy="160" r="70" fill="{c_glow}" opacity="0.5" filter="url(#blur-glow)"/>
        """

    # Dynamic Character Silhouette based on action stage and style
    char_svg = f"""
    <!-- Character Presence: {character_name} -->
    <g transform="translate({char_x + float_offset}, 260) scale({char_scale})">
        <!-- Aura / Glow -->
        <circle cx="0" cy="-60" r="45" fill="{c_glow}" opacity="0.3" filter="url(#blur-glow)"/>
        
        <!-- Cloak / Body Silhouette -->
        <path d="M -30 -30 C -45 10, -50 70, -40 110 L 40 110 C 50 70, 45 10, 30 -30 Z" fill="{style_info['line_color']}" stroke="{c_accent}" stroke-width="2.5"/>
        
        <!-- Torso & Core Action Lines -->
        <polygon points="-18,-25 18,-25 14,40 -14,40" fill="{s_sec}" opacity="0.9"/>
        <line x1="0" y1="-25" x2="0" y2="40" stroke="{c_accent}" stroke-width="2"/>
        
        <!-- Head & Hair Silhouette -->
        <ellipse cx="0" cy="-60" rx="20" ry="24" fill="{style_info['line_color']}" stroke="{c_accent}" stroke-width="2"/>
        <polygon points="-24,-72 0,-92 24,-72 16,-55 -16,-55" fill="{c_accent}" opacity="0.85"/>
        
        <!-- Eyes / Focal Visor Glow -->
        <line x1="-10" y1="-62" x2="-3" y2="-62" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
        <line x1="3" y1="-62" x2="10" y2="-62" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
        
        <!-- Active Arm / Energy Focus Gesture -->
        <path d="M 24 -15 Q 55 -30 75 -50" fill="none" stroke="{style_info['line_color']}" stroke-width="8" stroke-linecap="round"/>
        <circle cx="75" cy="-50" r="14" fill="{c_glow}" opacity="0.85" filter="url(#blur-glow)"/>
        <circle cx="75" cy="-50" r="6" fill="#FFFFFF"/>
    </g>
    """

    # Halftone & Comic Texture Pattern
    halftone_pattern = ""
    if art_style in ["Comic Book", "Cartoon", "Manga"]:
        halftone_pattern = f"""
        <pattern id="halftone" width="12" height="12" patternUnits="userSpaceOnUse">
            <circle cx="6" cy="6" r="1.8" fill="{c_accent}" opacity="0.16"/>
        </pattern>
        <rect width="600" height="400" fill="url(#halftone)" pointer-events="none"/>
        """

    # Comic Speed / Impact Lines for climactic panels
    speed_lines = ""
    if speed_opacity > 0.1:
        speed_lines = f"""
        <g opacity="{speed_opacity}" stroke="{c_glow}" stroke-width="2" stroke-linecap="round">
            <line x1="0" y1="0" x2="220" y2="180"/>
            <line x1="600" y1="0" x2="380" y2="180"/>
            <line x1="0" y1="400" x2="220" y2="220"/>
            <line x1="600" y1="400" x2="380" y2="220"/>
            <line x1="300" y1="0" x2="300" y2="140"/>
            <line x1="0" y1="200" x2="160" y2="200"/>
            <line x1="600" y1="200" x2="440" y2="200"/>
        </g>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%" class="comic-panel-svg">
    <defs>
        <linearGradient id="sky-grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="{g_start}" />
            <stop offset="50%" stop-color="{g_mid}" />
            <stop offset="100%" stop-color="{g_end}" />
        </linearGradient>
        <linearGradient id="planet-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{c_glow}" />
            <stop offset="100%" stop-color="{s_prim}" />
        </linearGradient>
        <radialGradient id="sun-burst" cx="50%" cy="40%" r="60%">
            <stop offset="0%" stop-color="{c_glow}" stop-opacity="0.4" />
            <stop offset="100%" stop-color="{g_start}" stop-opacity="0" />
        </radialGradient>
        <filter id="blur-glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <filter id="comic-drop" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="3" dy="3" stdDeviation="0" flood-color="#000000" flood-opacity="0.9"/>
        </filter>
    </defs>

    <!-- Background Sky -->
    <rect width="600" height="400" fill="url(#sky-grad)" />
    <rect width="600" height="400" fill="url(#sun-burst)" />

    <!-- Scenery Layers -->
    {scenery_svg}

    <!-- Halftone Texture Overlay -->
    {halftone_pattern}

    <!-- Dynamic Speed Lines -->
    {speed_lines}

    <!-- Character Layer -->
    {char_svg}

    <!-- Comic Ink Vignette & Border Frame -->
    <rect x="4" y="4" width="592" height="392" fill="none" stroke="{style_info['line_color']}" stroke-width="8" />
    <rect x="8" y="8" width="584" height="384" fill="none" stroke="{c_accent}" stroke-width="2" opacity="0.6"/>

    <!-- Scene Stage Indicator Tag -->
    <g transform="translate(18, 22)">
        <rect x="0" y="0" width="150" height="24" rx="4" fill="#111318" stroke="#FFE600" stroke-width="1.5" filter="url(#comic-drop)"/>
        <text x="75" y="16" fill="#FFE600" font-family="'Impact', 'Arial Black', sans-serif" font-size="11" letter-spacing="1" text-anchor="middle" font-weight="bold">{badge_text}</text>
    </g>

    <!-- Art Style Stamp -->
    <g transform="translate(450, 22)">
        <rect x="0" y="0" width="130" height="24" rx="4" fill="#111318" opacity="0.9" stroke="{c_glow}" stroke-width="1"/>
        <text x="65" y="16" fill="#F8FAFC" font-family="sans-serif" font-size="10" font-weight="600" text-anchor="middle">{art_style.upper()} ART</text>
    </g>
</svg>"""

    # Return as base64 data URI for direct SVG rendering
    encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{encoded}"


def generate_style_preview_image(style_name: str) -> str:
    """
    Generates a dedicated high-impact preview card image for the art style selector.
    """
    return generate_panel_svg(
        panel_number=3,
        panel_title=f"{style_name} Studio Showcase",
        character_name="Hero",
        setting="City" if style_name in ["Comic Book", "Anime"] else "Enchanted Forest",
        tone="Epic",
        art_style=style_name,
        scene_description=f"Previewing the visual aesthetic of {style_name} style.",
        action_type="preview"
    )


def generate_panel_illustration(
    panel_number: int,
    panel_title: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    scene_description: str,
    image_prompt: str
) -> Dict[str, Any]:
    """
    Primary image generation dispatcher.
    If STABILITY_API_KEY is present in environment, calls Stability AI.
    Otherwise, cleanly utilizes the procedural high-fidelity comic illustration engine.
    """
    stability_key = os.getenv("STABILITY_API_KEY")

    if stability_key:
        try:
            import requests
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {stability_key}",
            }
            body = {
                "steps": 30,
                "width": 768,
                "height": 512,
                "seed": 0,
                "cfg_scale": 7,
                "samples": 1,
                "text_prompts": [
                    {
                        "text": f"{image_prompt}, {art_style} style, comic panel art, sharp details, masterwork illustration",
                        "weight": 1
                    },
                    {
                        "text": "bad anatomy, blurry, watermarks, text, low quality",
                        "weight": -1
                    }
                ],
            }
            response = requests.post(url, headers=headers, json=body, timeout=25)
            if response.status_code == 200:
                data = response.json()
                base64_img = data["artifacts"][0]["base64"]
                return {
                    "image_url": f"data:image/png;base64,{base64_img}",
                    "source": "Stability AI SDXL",
                    "mode": "live"
                }
        except Exception as e:
            print(f"[Warning] Stability API call failed: {e}. Falling back to high-fidelity procedural engine.")

    # High-fidelity procedural comic engine (Demo/Fallback Mode)
    svg_data_uri = generate_panel_svg(
        panel_number=panel_number,
        panel_title=panel_title,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
        scene_description=scene_description
    )

    return {
        "image_url": svg_data_uri,
        "source": "ComicCraft Vector AI Engine",
        "mode": "demo"
    }

"""
ComicCraft Story Generation Service
Supports:
1. Google Gemini Flash (outline) & Gemini Pro (narration/dialogue) when GEMINI_API_KEY is provided
2. Context-Aware Procedural Comic Story Engine (Demo/Fallback Mode)
   Synthesizes dynamic, coherent multi-panel storylines, dramatic dialogue,
   and visual prompts from user inputs.
"""

import os
import json
import random
from typing import Dict, Any, List, Optional
from services.image_generator import generate_panel_illustration

SURPRISE_PROMPTS = [
    {
        "prompt": "A courageous young alchemist discovers a celestial crystal that opens a doorway between floating cloud islands.",
        "character": "Valen",
        "setting": "Enchanted Forest",
        "tone": "Adventure",
        "art_style": "Anime",
        "panels_count": 5
    },
    {
        "prompt": "An eccentric cyber-detective investigates mysterious power surges leaking from an abandoned orbital elevator.",
        "character": "Kaelen Voss",
        "setting": "City",
        "tone": "Mysterious",
        "art_style": "Comic Book",
        "panels_count": 5
    },
    {
        "prompt": "A lone robotic ranger wanders across an ancient starship graveyard searching for the last operational memory core.",
        "character": "Unit 7-Echo",
        "setting": "Space",
        "tone": "Emotional",
        "art_style": "Realistic",
        "panels_count": 5
    },
    {
        "prompt": "A student accidentally drinks a potions club experiment that allows them to hear the inner thoughts of school gargoyles.",
        "character": "Maya Lin",
        "setting": "School",
        "tone": "Funny",
        "art_style": "Cartoon",
        "panels_count": 5
    },
    {
        "prompt": "A royal knight discovers an ancient dragon egg guarded by mechanical clockwork sentinels beneath the throne room.",
        "character": "Seraphina",
        "setting": "Medieval Kingdom",
        "tone": "Epic",
        "art_style": "Fantasy",
        "panels_count": 5
    },
    {
        "prompt": "A rogue courier with cybernetic wings escapes through neon skyscrapers while delivering a forbidden memory chip.",
        "character": "Ren",
        "setting": "Future World",
        "tone": "Dramatic",
        "art_style": "Manga",
        "panels_count": 5
    }
]

# Curated Made-With-ComicCraft sample comics
SAMPLE_COMICS_DATA = {
    "fox-portal": {
        "id": "fox-portal",
        "title": "The Fox and the Portal",
        "character": "Leo the Fox",
        "setting": "Enchanted Forest",
        "tone": "Adventure",
        "art_style": "Anime",
        "panels_count": 5,
        "summary": "A spirited woodland fox stumbles upon an ancient luminescent archway humming with planar energy.",
        "badge": "Anime • Adventure",
        "thumbnail_icon": "🦊",
        "panels": [
            {
                "number": 1,
                "title": "Into the Deep Woods",
                "scene_description": "Leo wanders deep past the ancient elder willows into an unexplored sunlit clearing.",
                "caption": "The forest was silent, save for a gentle, rhythmic hum vibrating beneath the moss.",
                "dialogue": 'LEO: "Nobody has ventured past the Silver Brook in generations... what is that glow?"',
                "image_prompt": "A sleek golden fox peering through glowing bioluminescent fern leaves toward an azure stone archway in an enchanted forest, anime art style, cinematic rim lighting."
            },
            {
                "number": 2,
                "title": "The Shimmering Gateway",
                "scene_description": "Leo steps onto ancient rune-inscribed paving stones surrounding a spiraling portal of starlight.",
                "caption": "A celestial circle of azure light spun softly, casting dancing ripples over ancient glyphs.",
                "dialogue": 'LEO: "It feels warm... like sunshine after a winter frost."',
                "image_prompt": "Golden fox approaching an upright circular portal of swirling starlight and floating motes, ancient carved stone circle, lush fantasy forest, anime style."
            },
            {
                "number": 3,
                "title": "The Celestial Whisper",
                "scene_description": "A spectral butterfly emerges from the portal, brushing against Leo's whiskers with a spark of lightning.",
                "caption": "Without warning, the rift expanded, revealing visions of floating islands beyond the clouds.",
                "dialogue": 'PORTAL VOICE: "Seeker of the wild, the realms have waited for your pawstep."',
                "image_prompt": "Dramatic close up of an anime-style fox face illuminated by electric blue lightning and glowing spectral butterfly wings, speed lines, vibrant colors."
            },
            {
                "number": 4,
                "title": "The Leap Across Worlds",
                "scene_description": "Leo crouches and leaps boldly into the swirling vortex as the forest ground falls away.",
                "caption": "With fearless determination, he launched himself forward into the unknown horizon.",
                "dialogue": 'LEO: "Whatever is on the other side... I’m ready!"',
                "image_prompt": "Anime fox leaping in mid-air toward a glowing vortex of stars and clouds, dynamic flying angle, wind streaks, heroic composition."
            },
            {
                "number": 5,
                "title": "Skies of Tomorrow",
                "scene_description": "Leo lands softly upon a floating emerald cloud island overlooking infinite twin suns.",
                "caption": "A new chapter had begun in a realm where paws tread upon clouds.",
                "dialogue": 'LEO: "This isn’t the end of our forest... it’s the beginning of everything."',
                "image_prompt": "Panoramic view of a fox sitting atop a floating green meadow in the sky, twin suns setting on horizon, floating airships, triumphant anime landscape."
            }
        ]
    },
    "last-space-explorer": {
        "id": "last-space-explorer",
        "title": "The Last Space Explorer",
        "character": "Commander Eva Cruz",
        "setting": "Space",
        "tone": "Epic",
        "art_style": "Comic Book",
        "panels_count": 5,
        "summary": "At the edge of mapped space, a lone pilot intercepts an anomalous transmission from inside a dying star.",
        "badge": "Comic Book • Epic Sci-Fi",
        "thumbnail_icon": "🚀",
        "panels": [
            {
                "number": 1,
                "title": "Event Horizon Vector",
                "scene_description": "Commander Cruz navigates her recon ship through the gravitational shears of Sector Zero.",
                "caption": "Three hundred light years beyond civilization, radar scopes began screaming with anomalous telemetry.",
                "dialogue": 'EVA: "Deep-space beacon locked. If this reading is accurate, physics just took a vacation."',
                "image_prompt": "Retro-modern American comic book art of a sleek deep-space exploration craft skimming purple nebulae clouds, heavy inking and Ben-Day dots."
            },
            {
                "number": 2,
                "title": "The Ancient Megastructure",
                "scene_description": "A colossal Dyson ring emerges from the stellar flare, dwarfing the explorer vessel.",
                "caption": "It was not a derelict asteroid, but an artificial ring of unthinkably ancient origin.",
                "dialogue": 'EVA: "Command said this sector was empty. They lied... or they never survived to report it."',
                "image_prompt": "Gargantuan alien ring structure encircling a pulsating yellow star, comic book style, bold shadow lines, intense dramatic lighting."
            },
            {
                "number": 3,
                "title": "Systems Breach",
                "scene_description": "Warning klaxons flash red inside the cockpit as a tractor beam locks onto the navigation core.",
                "caption": "Automatic fail-safes melted under an ancient alien handshake protocol.",
                "dialogue": 'EVA: "Manual overrides are frozen! It’s not attacking us... it’s welcoming us aboard."',
                "image_prompt": "Cockpit interior with red emergency lights, astronaut with helmet reflection showing alien glyphs, dynamic comic framing."
            },
            {
                "number": 4,
                "title": "The Chamber of Stars",
                "scene_description": "Cruz steps out into a cathedral-sized hall where miniature galaxies float in suspension.",
                "caption": "Every stellar birth across the millennium was catalogued within the silent vault.",
                "dialogue": 'EVA: "We spent centuries searching for the builders... and they left behind the entire universe’s blueprint."',
                "image_prompt": "Astronaut standing on an obsidian walkway surrounded by holographic miniature spinning galaxies, bold comic book shadows, vibrant neon contrasts."
            },
            {
                "number": 5,
                "title": "The First Signal",
                "scene_description": "Eva initiates a long-range relay transmitter aimed back toward Earth.",
                "caption": "A transmission was sent back to humanity that would alter their history forever.",
                "dialogue": 'EVA: "Earth Station, this is Cruz. Pack your bags. We are not alone, and never have been."',
                "image_prompt": "Heroic comic panel of astronaut looking out at an expansive star-field as a golden signal beam shoots into the cosmic void, triumphant finish."
            }
        ]
    },
    "mystery-midnight": {
        "id": "mystery-midnight",
        "title": "Mystery at Midnight",
        "character": "Detective Silas Drake",
        "setting": "City",
        "tone": "Mysterious",
        "art_style": "Manga",
        "panels_count": 5,
        "summary": "Rain-soaked streets and whispered rumors lead a hard-boiled detective to an underground clockwork speakeasy.",
        "badge": "Manga • Noir Mystery",
        "thumbnail_icon": "🕵️",
        "panels": [
            {
                "number": 1,
                "title": "Rain on Iron Street",
                "scene_description": "Detective Drake stands beneath a flickering neon streetlight, trench coat soaked in rain.",
                "caption": "Midnight in the lower wards had a bitter taste—like wet soot and unspoken alibis.",
                "dialogue": 'SILAS: "The clock on the cathedral struck thirteen. In this town, that’s never a coincidence."',
                "image_prompt": "Classic noir manga panel, detective in trench coat smoking beneath a flickering streetlamp in heavy rain, stark black and white ink, screentone shading."
            },
            {
                "number": 2,
                "title": "The Ciphered Ticket",
                "scene_description": "Silas examines a brass punch-card marked with the seal of the secretive Obsidian Guild.",
                "caption": "A dead informant’s pocket held only one clue: an invitation without an address.",
                "dialogue": 'SILAS: "Only one watchmaker in the district cuts brass gears with this kind of precision."',
                "image_prompt": "Manga close-up of gloved hand holding a punched brass card with ornate gears, rain droplets, high contrast screentone crosshatching."
            },
            {
                "number": 3,
                "title": "The Shadowed Alley",
                "scene_description": "Drake follows an elusive cloaked figure slipping between narrow steam-filled backstreets.",
                "caption": "Footsteps echoed across wet cobblestones, always three paces ahead of justice.",
                "dialogue": 'SILAS: "Hold it right there! The guild’s run ends tonight!"',
                "image_prompt": "Dramatic manga speed lines, detective chasing silhouette with flowing cape through dark brick alley, steam vents blowing white smoke."
            },
            {
                "number": 4,
                "title": "The Clocktower Ambush",
                "scene_description": "Inside the gargantuan gear chamber, mechanical pendulums swing violently between the combatants.",
                "caption": "Time was literally ticking as the pendulum swung within inches of Drake’s head.",
                "dialogue": 'SHADOW FIGURE: "You’re too late, detective. The mechanism is already unwinding!"',
                "image_prompt": "Epic manga action panel inside a massive clockwork tower, giant interlocking cogwheels, intense action pose with motion blurs."
            },
            {
                "number": 5,
                "title": "The Key Revealed",
                "scene_description": "Silas pins the mechanism with his iron cane, catching the falling chronometer key in his palm.",
                "caption": "The clock froze. The city below slept on, oblivious to the catastrophe averted.",
                "dialogue": 'SILAS: "Case closed. And tell your patron... time just caught up with him."',
                "image_prompt": "Manga style final panel, detective holding an ornate key with smoke drifting from the stopped gears, triumphant grin under fedora brim."
            }
        ]
    }
}


def _generate_procedural_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    panels_count: int = 5
) -> Dict[str, Any]:
    """
    Context-aware procedural story synthesis engine.
    Crafts realistic narrative beats tailored to the user's prompt, character, tone, and setting.
    """
    # Clean inputs
    char = character_name.strip() or "The Protagonist"
    sett = setting.strip() or "Unknown Realm"
    t_val = tone.strip() or "Adventure"
    style = art_style.strip() or "Comic Book"
    prompt = story_prompt.strip()

    # Generate an evocative comic title
    title_prefixes = {
        "Adventure": ["The Chronicles of", "The Journey of", "Beyond the Horizon:", "The Legend of"],
        "Funny": ["The Hilarious Misadventures of", "Oops! Featuring", "The Chaotic Days of", "Double Trouble:"],
        "Dramatic": ["Shattered Vows:", "The Cost of Tomorrow:", "Echoes of the Fall:", "Tears in"],
        "Mysterious": ["The Riddle of", "Whispers in the Dark:", "The Secret of", "Shadows Over"],
        "Epic": ["The Rising of", "Dawn of the Ages:", "The Ascendance of", "Battle for"],
        "Light-hearted": ["Sunny Days with", "The Wonder Journey of", "A Day to Remember:", "Adventures with"],
        "Emotional": ["Memories of", "The Promise of", "Where Hearts Meet:", "A Song for"]
    }
    prefix = random.choice(title_prefixes.get(t_val, ["The Tale of"]))
    comic_title = f"{prefix} {char}"

    # Generate sequential narrative stages
    # 1: Establishing / Call to Action
    # 2: The Discovery / Inciting Event
    # 3: The Rising Conflict / Challenge
    # 4: Climax / Decisive Moment
    # 5: Resolution / Triumph or Cliffhanger
    # Extra panels for 6 or 8 panels
    narrative_templates = [
        {
            "stage": "setup",
            "title_variants": [
                f"Beginnings at {sett}",
                f"The Call to {sett}",
                f"A Quiet Day Turns Strange",
                f"The Awakening of {char}"
            ],
            "captions": [
                f"Every great legend begins in an unexpected corner of {sett}.",
                f"For {char}, what started as an ordinary day in {sett} was about to change forever.",
                f"Silence draped over {sett}, concealing the mysterious tremor that was soon to arrive.",
                f"The journey of {char} commenced when the signs first appeared."
            ],
            "dialogues": [
                f'{char.upper()}: "Something in the air feels different today... like an unseen storm approaching."',
                f'{char.upper()}: "If the rumors about {sett} are true, then I have to see it with my own eyes."',
                f'{char.upper()}: "No turning back now. The map pointed right here."',
                f'{char.upper()}: "Just another quiet morning... or so I thought."'
            ],
            "image_prompts": [
                f"Establishing shot of {char} standing at the edge of {sett}, looking toward the glowing horizon, {style} style, dramatic framing.",
                f"{char} carefully observing ancient artifacts and glowing runes within {sett}, atmospheric lighting, {style} style.",
                f"Wide landscape of {sett} with {char} in the foreground looking up at the sky, cinematic depth of field, {style} aesthetic."
            ]
        },
        {
            "stage": "discovery",
            "title_variants": [
                "The Ancient Relic",
                "A Sudden Discovery",
                "Unlocking the Mystery",
                "The First Encounter"
            ],
            "captions": [
                f"Drawn by an enigmatic hum, {char} uncovered a secret buried for centuries.",
                f"Before them lay the anomaly—pulsing with raw, untamed energy.",
                f"The puzzle pieces started falling into place, revealing a path none dared tread.",
                f"An unexpected glow illuminated the shadows of {sett}."
            ],
            "dialogues": [
                f'{char.upper()}: "Look at this craftsmanship! It’s still functioning after all this time!"',
                f'{char.upper()}: "Could this really be the key everyone has been searching for?"',
                f'{char.upper()}: "It’s reacting to my touch! Stand back!"',
                f'{char.upper()}: "Whatever happens next, we’re committed."'
            ],
            "image_prompts": [
                f"{char} discovering an ornate glowing artifact in {sett}, sparkling energy particles, {style} art style, expressive face.",
                f"Close up of {char}'s hands brushing moss and dust off a humming celestial device in {sett}, {style} comic illustration.",
                f"Magical light erupting from a newly opened chamber in {sett}, illuminating {char}'s determined expression, {style} style."
            ]
        },
        {
            "stage": "conflict",
            "title_variants": [
                "The Sudden Ambush",
                "Rising Peril",
                "The Trial Begins",
                "Against the Clock"
            ],
            "captions": [
                f"The ground shook violently as guardians awakened to defend {sett}.",
                f"Danger arrived swift and merciless, testing {char}'s resolve to the limit.",
                f"There was no time to calculate the odds—only time to react.",
                f"An ominous force surged forward, threatening to swallow everything in sight."
            ],
            "dialogues": [
                f'{char.upper()}: "Incoming! I’m not backing down from this fight!"',
                f'{char.upper()}: "We have to hold the line until the surge stabilizes!"',
                f'{char.upper()}: "Is that all you’ve got? I came prepared!"',
                f'{char.upper()}: "Hold on tight—this is about to get turbulent!"'
            ],
            "image_prompts": [
                f"Dynamic action shot of {char} dodging falling debris and energy blasts in {sett}, speed lines, intense {style} comic style.",
                f"{char} unleashing a countermeasure against shadowy obstacles in {sett}, glowing power aura, {style} graphic panel.",
                f"Dramatic duel scene where {char} stands firm amidst swirling elemental forces in {sett}, bold ink lines, {style} art."
            ]
        },
        {
            "stage": "climax",
            "title_variants": [
                "The Turning Point",
                "The Decisive Strike",
                "The Heart of the Storm",
                "Power Unleashed"
            ],
            "captions": [
                f"With one final surge of bravery, {char} channeled the full force of the discovery.",
                f"All odds were stacked against them, but failure was simply not an option.",
                f"In this single heartbeat, the true fate of {sett} was decided.",
                f"The energy peaked into a blinding corona that pierced the night sky."
            ],
            "dialogues": [
                f'{char.upper()}: "This ends now! For everyone counting on us!"',
                f'{char.upper()}: "I see the weakness in the core—everyone clear the area!"',
                f'{char.upper()}: "All or nothing! Let’s show them what we’re made of!"',
                f'{char.upper()}: "We did it... the barrier is shattering!"'
            ],
            "image_prompts": [
                f"Climactic peak panel, {char} performing a heroic surge of power shattering the barrier in {sett}, lens flares, {style} comic masterpiece.",
                f"Blinding burst of radiant energy illuminating {char}'s triumphant stance in {sett}, {style} comic book action lines.",
                f"Heroic shot of {char} leaping through the exploding energy core, epic angle and dynamic composition in {style} style."
            ]
        },
        {
            "stage": "resolution",
            "title_variants": [
                "A New Dawn",
                "Victory at Last",
                "The Legend Continues",
                "Peace Restored"
            ],
            "captions": [
                f"As the dust settled over {sett}, the sun crested the mountains with renewed brilliance.",
                f"The peril had passed, leaving behind a world forever changed for the better.",
                f"A triumphant chapter closed, but {char}'s name would echo across the lands forever.",
                f"With quiet pride, {char} looked forward to the next adventure waiting over the horizon."
            ],
            "dialogues": [
                f'{char.upper()}: "We did what they said was impossible. Tomorrow is ours."',
                f'{char.upper()}: "This is just one step on a much longer journey... and I can’t wait."',
                f'{char.upper()}: "{sett} is finally safe. Let’s head home."',
                f'{char.upper()}: "Whenever danger calls again, we’ll be ready."'
            ],
            "image_prompts": [
                f"Triumphant sunrise panel of {char} overlooking a restored peaceful {sett}, golden light rays, serene and inspiring {style} illustration.",
                f"{char} walking confidently toward the horizon with a satisfied smile, dramatic rim light, {style} graphic novel style.",
                f"Wide celebratory scene showing {sett} shining brightly under clear skies as {char} raises a triumphant fist, {style} style."
            ]
        }
    ]

    # Handle 4, 5, 6, 8 panel layouts
    if panels_count == 4:
        selected_stages = [narrative_templates[0], narrative_templates[1], narrative_templates[3], narrative_templates[4]]
    elif panels_count == 6:
        selected_stages = [
            narrative_templates[0],
            narrative_templates[1],
            narrative_templates[2],
            narrative_templates[2], # escalation
            narrative_templates[3],
            narrative_templates[4]
        ]
    elif panels_count == 8:
        selected_stages = [
            narrative_templates[0],
            narrative_templates[1],
            narrative_templates[1],
            narrative_templates[2],
            narrative_templates[2],
            narrative_templates[3],
            narrative_templates[3],
            narrative_templates[4]
        ]
    else: # 5 panels standard
        selected_stages = narrative_templates

    panels = []
    for idx, stage in enumerate(selected_stages, start=1):
        # Incorporate user prompt details into narration and scene
        p_title = random.choice(stage["title_variants"])
        caption_base = random.choice(stage["captions"])
        dialogue = random.choice(stage["dialogues"])
        img_prompt = random.choice(stage["image_prompts"])

        # Add prompt context to scene description
        prompt_snippet = prompt[:80] + ("..." if len(prompt) > 80 else "")
        scene_desc = f"{char} in {sett}. Context: {prompt_snippet}. {stage['stage'].capitalize()} stage of the story."

        panels.append({
            "number": idx,
            "title": p_title,
            "scene_description": scene_desc,
            "caption": caption_base,
            "dialogue": dialogue,
            "image_prompt": img_prompt
        })

    return {
        "title": comic_title,
        "character": char,
        "setting": sett,
        "tone": t_val,
        "art_style": style,
        "panels_count": len(panels),
        "panels": panels,
        "source": "ComicCraft Procedural Narrative Engine",
        "mode": "demo"
    }


def generate_comic(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    panels_count: int = 5
) -> Dict[str, Any]:
    """
    Primary workflow coordinator:
    1. Generate outline & story structure (Gemini or procedural context engine)
    2. Generate artwork for each panel (Stability AI or procedural vector engine)
    3. Assemble complete ComicCraft document model
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    is_live = bool(gemini_key)

    # 1. Generate Story Outline & Dialogue
    if is_live:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt_instruction = f"""
            You are a master comic book writer and storyboard artist.
            Create a structured {panels_count}-panel comic outline based on:
            - Story Prompt: {story_prompt}
            - Character: {character_name}
            - Setting: {setting}
            - Tone: {tone}
            - Art Style: {art_style}

            Return ONLY valid JSON matching this schema:
            {{
                "title": "Comic Title",
                "panels": [
                    {{
                        "number": 1,
                        "title": "Panel Title",
                        "scene_description": "Detailed visual scene description",
                        "caption": "Narrator voiceover caption",
                        "dialogue": "CHARACTER: \\"Spoken line\\"",
                        "image_prompt": "Prompt for text-to-image generator describing visual scene in {art_style} style"
                    }}
                ]
            }}
            """
            response = model.generate_content(prompt_instruction)
            text = response.text.strip()
            # Clean markdown codeblocks if returned
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text.strip())
            comic_data = {
                "title": data.get("title", f"The Story of {character_name}"),
                "character": character_name,
                "setting": setting,
                "tone": tone,
                "art_style": art_style,
                "panels_count": len(data.get("panels", [])),
                "panels": data.get("panels", []),
                "source": "Google Gemini Flash",
                "mode": "live"
            }
        except Exception as e:
            print(f"[Warning] Gemini API call failed: {e}. Falling back to procedural engine.")
            comic_data = _generate_procedural_outline(story_prompt, character_name, setting, tone, art_style, panels_count)
    else:
        comic_data = _generate_procedural_outline(story_prompt, character_name, setting, tone, art_style, panels_count)

    # 2. Generate artwork for every panel
    for panel in comic_data["panels"]:
        img_res = generate_panel_illustration(
            panel_number=panel["number"],
            panel_title=panel["title"],
            character_name=comic_data["character"],
            setting=comic_data["setting"],
            tone=comic_data["tone"],
            art_style=comic_data["art_style"],
            scene_description=panel.get("scene_description", ""),
            image_prompt=panel.get("image_prompt", "")
        )
        panel["image"] = img_res["image_url"]
        panel["image_source"] = img_res.get("source", "Vector Engine")

    return comic_data


def get_sample_comic(sample_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns pre-baked sample comic with full illustrations.
    """
    sample = SAMPLE_COMICS_DATA.get(sample_id)
    if not sample:
        return None

    # Clone sample and populate illustrations
    result = dict(sample)
    result["panels"] = []
    for p in sample["panels"]:
        p_copy = dict(p)
        img_res = generate_panel_illustration(
            panel_number=p["number"],
            panel_title=p["title"],
            character_name=sample["character"],
            setting=sample["setting"],
            tone=sample["tone"],
            art_style=sample["art_style"],
            scene_description=p.get("scene_description", ""),
            image_prompt=p.get("image_prompt", "")
        )
        p_copy["image"] = img_res["image_url"]
        result["panels"].append(p_copy)

    return result

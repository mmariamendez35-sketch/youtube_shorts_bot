# config.py
"""Configuration constants for the autonomous YouTube Shorts bot.
Oraciones que transforman – Videos cortos y largos con oraciones poderosas.
"""
import os
from pathlib import Path

# --- Channel details -------------------------------------------------------
CHANNEL_NAME = "Oraciones que transforman"
NICHE = "Oraciones poderosas diarias que generan fe, esperanza y transformación espiritual"
LANGUAGE = "es"

# --- Schedule (UTC-5, Colombia) --------------------------------------------
# Shorts: 4 per day | Long videos: 1 per day
SHORTS_CRON = "0 13,17,22,2 * * *"   # 8am, 12pm, 5pm, 9pm COL
LONG_VIDEO_CRON = "0 15 * * *"        # 10am COL – 1 long video/day

# --- Video formats ----------------------------------------------------------
SHORT_MAX_WORDS = 60
SHORT_MAX_DURATION = 58       # seconds (YouTube Shorts limit = 60s)

LONG_MIN_SEGMENTS = 6         # min chapters in a long video
LONG_MAX_SEGMENTS = 12        # max chapters
LONG_WORDS_PER_SEGMENT = 80   # ~35-40 seconds of speech each
LONG_VIDEO_TARGET_MINUTES = 10  # target duration in minutes

# --- OpenRouter settings ---------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODELS = [
    "openrouter/free",
    "liquid/lfm-2.5-2.6b:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
]
MODEL_TIMEOUT = 20

# --- TTS settings ----------------------------------------------------------
TTS_LANGUAGE = "es"
TTS_SLOW = False
MAX_TTS_RETRIES = 3

# --- FFmpeg / Video settings -----------------------------------------------
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
MUSIC_FILE = "assets/music.mp3"

# Ken Burns effect ranges (randomized per slide)
KB_ZOOM_MIN = 1.0
KB_ZOOM_MAX = 1.25
KB_PAN_RANGE = 50   # max pixels of pan

# Transition duration between slides (seconds)
TRANSITION_DURATION = 1.0

# --- Visual styles (rotated to avoid repetition) ---------------------------
GRADIENT_PALETTES = [
    ("1a0a2e", "3d1e6d"),   # deep purple
    ("0a1628", "1e3a5f"),   # dark navy
    ("1a0000", "4a0e0e"),   # dark crimson
    ("0a2818", "1a5032"),   # dark forest
    ("2d1b00", "6b3a00"),   # dark amber
    ("1a1a2e", "16213e"),   # midnight blue
    ("0d0d0d", "2a2a2a"),   # charcoal
    ("1b0a28", "4a1a6d"),   # royal purple
    ("0a1a1a", "1a3a3a"),   # dark teal
    ("28100a", "5a2814"),   # dark bronze
]

SUBTITLE_STYLES = [
    "Fontsize=24,PrimaryColour=&HFFFFFFFF,OutlineColour=&H80000000,Outline=2,Shadow=1,Alignment=2,MarginV=100",
    "Fontsize=22,PrimaryColour=&H00FFFF00,OutlineColour=&H80000000,Outline=2,Shadow=2,Alignment=2,MarginV=90",
    "Fontsize=26,PrimaryColour=&HFFD700FF,OutlineColour=&H80000000,Outline=3,Shadow=1,Alignment=2,MarginV=110",
    "Fontsize=23,PrimaryColour=&HFFE0E0FF,OutlineColour=&H80222222,Outline=2,Shadow=1,Alignment=2,MarginV=95",
    "Fontsize=25,PrimaryColour=&HFF90EE90,OutlineColour=&H80000000,Outline=2,Shadow=2,Alignment=2,MarginV=105",
]

# --- YouTube API settings --------------------------------------------------
YOUTUBE_TOKEN_PATH = Path("youtube_token.json")
CLIENT_SECRET_PATH = Path("client_secret.json")

DEFAULT_TAGS_SHORT = [
    "Oración", "Oraciones", "Oración poderosa", "Oración de la mañana",
    "Fe", "Dios", "Jesús", "Espíritu Santo", "Bendición", "Milagro",
    "Oración del día", "Shorts", "Inspiración espiritual", "Cristiano",
]
DEFAULT_TAGS_LONG = [
    "Oración", "Oraciones poderosas", "Oración larga", "Meditación",
    "Fe", "Dios", "Jesús", "Espíritu Santo", "Bendición", "Milagro",
    "Transformación", "Oración profunda", "Reflexión espiritual",
    "Cristiano", "Biblia", "Vida espiritual",
]

CTA_PHRASES = [
    "🔔 Suscríbete y comenta AMÉN si esta oración tocó tu corazón.",
    "🙏 Comenta AMÉN y comparte con alguien que necesite esta oración.",
    "❤️ Dale LIKE si sentiste la presencia de Dios. Suscríbete para más.",
    "✝️ Escribe FE en los comentarios si crees en su poder.",
    "🕊️ Comparte esta oración con alguien que la necesite hoy.",
    "💪 Comenta FUERZA si Dios te dio fuerzas con esta oración.",
    "🌟 Suscríbete y activa la 🔔 para recibir oraciones diarias.",
    "📖 Comenta tu petición de oración y oramos juntos.",
]

DESCRIPTION_TEMPLATE_SHORT = """{title}

{cta}

🙏 Oraciones que transforman — Cada día una oración poderosa
que toca el corazón y renueva tu fe.

#Oración #OraciónPoderosa #Fe #Dios #Jesús #Milagro #Shorts #Bendición"""

DESCRIPTION_TEMPLATE_LONG = """{title}

{cta}

🙏 Oraciones que transforman — Una oración profunda y poderosa
para conectar con Dios y renovar tu espíritu.

Capítulos:
{chapters}

📖 Suscríbete para recibir oraciones que transforman tu vida cada día.

#Oración #OraciónPoderosa #Fe #Dios #Jesús #Milagro #Meditación #Bendición"""

# --- Anti-spam / History ---------------------------------------------------
HISTORY_FILE = Path("publish_history.json")
MAX_HISTORY = 200            # remember last N publications
MIN_TOPIC_DISTANCE = 3       # don't repeat same topic within N publications

# --- Cooldown lock ----------------------------------------------------------
COOLDOWN_MINUTES = 45

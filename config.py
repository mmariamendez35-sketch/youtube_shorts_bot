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
# Para asegurar una duracion MINIMA de 40s y MAXIMA de 58s en Shorts (YouTube limite = 60s):
SHORT_MIN_WORDS = 95
SHORT_MAX_WORDS = 125
SHORT_MIN_DURATION = 40.0     # Minimo 40 segundos
SHORT_MAX_DURATION = 58.0     # Maximo 58 segundos (margen para límite de 60s de Shorts)

LONG_MIN_SEGMENTS = 6         # min chapters in a long video
LONG_MAX_SEGMENTS = 12        # max chapters
LONG_WORDS_PER_SEGMENT = 80   # ~35-40 seconds of speech each
LONG_VIDEO_TARGET_MINUTES = 10  # target duration in minutes

# --- OpenRouter settings ---------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODELS = [
    "openrouter/free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3.5-lightning:free",
]
MODEL_TIMEOUT = 25

# --- TTS settings ----------------------------------------------------------
TTS_LANGUAGE = "es"
TTS_SLOW = False
MAX_TTS_RETRIES = 3

# --- FFmpeg / Video settings -----------------------------------------------
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
MUSIC_FILE = "assets/music.mp3"
PRAYERS_IMG_DIR = Path("assets/prayers")

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

# --- Subtitle styles (High impact, big mobile-friendly fonts, safe-zone positioning) ---
SUBTITLE_STYLES = [
    "Fontname=Arial,Bold=1,Fontsize=56,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,Outline=4,Shadow=2,Alignment=2,MarginV=260",
    "Fontname=Arial,Bold=1,Fontsize=58,PrimaryColour=&H0000FFFF&,OutlineColour=&H00000000&,Outline=4,Shadow=3,Alignment=2,MarginV=260",
    "Fontname=Arial,Bold=1,Fontsize=56,PrimaryColour=&H002EFFFF&,OutlineColour=&H00000000&,Outline=4,Shadow=2,Alignment=2,MarginV=260",
    "Fontname=Arial,Bold=1,Fontsize=54,PrimaryColour=&H00D0FFFF&,OutlineColour=&H00000000&,Outline=4,Shadow=2,Alignment=2,MarginV=260",
    "Fontname=Arial,Bold=1,Fontsize=56,PrimaryColour=&H0098FB98&,OutlineColour=&H00000000&,Outline=4,Shadow=3,Alignment=2,MarginV=260",
]

# --- YouTube API settings --------------------------------------------------
YOUTUBE_TOKEN_PATH = Path("youtube_token.json")
CLIENT_SECRET_PATH = Path("client_secret.json")

DEFAULT_TAGS_SHORT = [
    "Oración", "Oraciones", "Oración poderosa", "Oración de la mañana",
    "Oración de la noche", "Fe", "Dios", "Jesús", "Espíritu Santo", "Bendición",
    "Milagro", "Oración del día", "Shorts", "Inspiración espiritual", "Católico",
    "Cristianos", "Paz interior", "Amén", "Oración de protección", "Dios te dice hoy",
]
DEFAULT_TAGS_LONG = [
    "Oración", "Oraciones poderosas", "Oración larga", "Meditación",
    "Fe", "Dios", "Jesús", "Espíritu Santo", "Bendición", "Milagro",
    "Transformación", "Oración profunda", "Reflexión espiritual",
    "Cristiano", "Biblia", "Vida espiritual", "Paz mental", "Oración para dormir",
]

CTA_PHRASES = [
    "🙏 Si recibes esta bendición hoy, escribe con fe AMÉN en los comentarios y compártela.",
    "✨ Escribe 'DIOS ESTÁ CONMIGO' en los comentarios y declara tu milagro hoy.",
    "🛡️ Comenta AMÉN para sellar la protección de Dios sobre tu hogar y tu familia.",
    "❤️ No te vayas sin dejar tu AMÉN. Dios escucha la oración sincera de tu corazón.",
    "🌟 Escribe FE si crees que Dios abrirá una puerta grande en tu vida esta semana.",
    "🕊️ Comenta 'RECIBO MI PAZ' y deja tus preocupaciones en las manos del Señor.",
    "✝️ Comenta AMÉN y suscríbete para recibir cada día la palabra que transformará tu vida.",
]

DESCRIPTION_TEMPLATE_SHORT = """{title}

{cta}

🙏 Bienvenidos a Oraciones que transforman. Cada día una oración poderosa para renovar tu fe, encontrar paz y recibir las bendiciones de Dios.

👇 Deja tu petición de oración en los comentarios para orar juntos por tu necesidad.

#Oración #OraciónPoderosa #Fe #Dios #Jesús #Milagro #Shorts #Bendición #Amén #Católicos #Cristianos"""

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

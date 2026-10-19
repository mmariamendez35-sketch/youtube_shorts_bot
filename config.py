# config.py
"""Configuration constants for the autonomous YouTube Shorts bot.
Secrets are loaded from environment variables (set in GitHub Secrets).
"""
import os
from pathlib import Path

# --- Channel details -------------------------------------------------------
CHANNEL_NAME = "Historias Bíblicas Diarias"
NICHE = "Historias de la Biblia con enseñanzas hipnóticas y alta retención"
LANGUAGE = "es"

# Publication schedule (UTC-5, Colombia) – 4 shorts + 1 long video
PUBLISH_TIMES = ["08:00", "12:00", "17:00", "21:00"]
LONG_VIDEO_TIME = "10:00"

# --- OpenRouter settings ---------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODELS = [
    "openrouter/free",
    "liquid/lfm-2.5-2.6b:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
]
MODEL_TIMEOUT = 8

# --- TTS settings ----------------------------------------------------------
TTS_LANGUAGE = "es"
TTS_SLOW = False
MAX_TTS_RETRIES = 3

# --- FFmpeg settings -------------------------------------------------------
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
BACKGROUND_VIDEO = "assets/background.mp4"
OVERLAY_IMAGE = "assets/overlay.png"
MUSIC_FILE = "assets/music.mp3"

# --- YouTube API settings --------------------------------------------------
YOUTUBE_TOKEN_PATH = Path(os.getenv("YOUTUBE_TOKEN_JSON", "youtube_token.json"))
CLIENT_SECRET_PATH = Path(os.getenv("CLIENT_SECRET_JSON", "client_secret.json"))

DEFAULT_TAGS = [
    "Biblia", "Historia Bíblica", "Shorts", "Inspiración",
    "Fe", "Dios", "Jesús", "Milagro", "Enseñanza", "Reflexión",
    "Espiritual", "Oración", "Cristiano", "Religión", "Vida"
]
CTA_TEXT = "🔔 Suscríbete y comenta AMÉN si esta historia tocó tu corazón."
DESCRIPTION_TEMPLATE = """{title}

{cta}

📖 Historias bíblicas que transforman vidas.
Cada día un nuevo mensaje de fe, esperanza y amor.

#Biblia #HistoriaBíblica #Shorts #Fe #Dios #Inspiración #Milagro"""

# --- Cooldown lock ----------------------------------------------------------
COOLDOWN_MINUTES = 45

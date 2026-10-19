# main.py
"""Orchestrator for the autonomous YouTube bot – Oraciones que transforman.
Supports TWO modes:
  - "short" → YouTube Shorts (< 60s) — quick, punchy prayers
  - "long"  → Long-form videos (8-15 min) — deep, multi-chapter prayers

Anti-spam features:
  - Topic rotation (no repeats within last N publications)
  - Script fingerprinting (no duplicate content)
  - Visual style rotation (different colors/effects each time)
  - CTA rotation (varied calls-to-action)
"""
import json
import logging
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import (
    CHANNEL_NAME,
    YOUTUBE_TOKEN_PATH,
    DEFAULT_TAGS_SHORT,
    DEFAULT_TAGS_LONG,
    CTA_PHRASES,
    DESCRIPTION_TEMPLATE_SHORT,
    DESCRIPTION_TEMPLATE_LONG,
    COOLDOWN_MINUTES,
)
from scripts.generate_script import generate_short_script, generate_long_script
from scripts.generate_audio import generate_audio_and_srt
from scripts.assemble_video import assemble_short, assemble_long
from scripts.publish_youtube import upload_video
from scripts.lock import recent_upload_exists
from scripts.anti_spam import (
    pick_unique_topic,
    is_script_duplicate,
    record_publication,
    get_next_style_index,
    get_next_cta,
)

logging.basicConfig(level=logging.INFO)

# ── Prayer topics (expanded for anti-spam rotation) ─────────────────────
SHORT_TOPICS = [
    "Oración de la mañana para empezar el día con Dios",
    "Oración de protección para mi familia",
    "Oración para romper cadenas de ansiedad",
    "Oración de sanación física y espiritual",
    "Oración para abrir caminos cerrados",
    "Oración de agradecimiento profundo",
    "Oración de la noche antes de dormir",
    "Oración por los hijos y su futuro",
    "Oración para momentos de crisis",
    "Oración de fortaleza cuando te sientes débil",
    "Oración por la paz interior",
    "Oración para el trabajo y la provisión",
    "Oración de liberación espiritual",
    "Oración por los enfermos",
    "Oración de perdón y reconciliación",
    "Oración para renovar la fe",
    "Oración por un milagro urgente",
    "Oración de bendición para el hogar",
    "Oración contra la soledad y tristeza",
    "Oración de victoria y declaración de fe",
    "Oración por la pareja y el matrimonio",
    "Oración de protección contra el mal",
    "Oración por los que sufren en silencio",
    "Oración para tener paciencia y esperanza",
    "Oración de entrega total a Dios",
]

LONG_TOPICS = [
    "Oración profunda de sanación interior y liberación",
    "Oración completa de protección para toda la familia",
    "Oración de la mañana — 10 minutos con Dios",
    "Oración de la noche — Meditación y descanso espiritual",
    "Oración por los hijos — Protección, guía y bendición",
    "Oración de guerra espiritual y victoria",
    "Oración de gratitud — 10 razones para dar gracias a Dios",
    "Oración profunda para momentos de desesperación",
    "Oración por provisión económica y laboral",
    "Oración de restauración de relaciones rotas",
    "Oración de fortaleza en medio de la enfermedad",
    "Oración por la paz mundial y los que sufren",
    "Oración de entrega total — Rendirse ante Dios",
    "Oración para romper maldiciones generacionales",
    "Oración de consagración y renovación de fe",
]


def _get_channel_id() -> str:
    """Auto-detect channel ID from YouTube API."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    if not YOUTUBE_TOKEN_PATH.is_file():
        raise FileNotFoundError("YouTube token JSON not found.")

    creds = Credentials.from_authorized_user_file(
        str(YOUTUBE_TOKEN_PATH),
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    )
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)
    response = youtube.channels().list(part="id", mine=True).execute()
    items = response.get("items", [])
    if not items:
        raise RuntimeError("No YouTube channel found for the authenticated user.")
    return items[0]["id"]


def run_short(custom_topic: str = ""):
    """Generate and publish a YouTube Short."""
    logging.info(f"=== MODO: SHORT — {CHANNEL_NAME} ===")

    channel_id = _get_channel_id()

    if recent_upload_exists(channel_id):
        logging.warning("Cooldown activo — abortando.")
        return

    # Pick unique topic
    topic = custom_topic.strip() if custom_topic.strip() else pick_unique_topic(SHORT_TOPICS)
    logging.info(f"Topic: {topic}")

    # Generate script (retry if duplicate)
    for attempt in range(3):
        script = generate_short_script(topic)
        if not is_script_duplicate(script):
            break
        logging.warning(f"Script duplicado detectado (intento {attempt+1}), regenerando...")
    logging.info(f"Script ({len(script)} chars): {script[:80]}...")

    # Audio + subtitles
    audio_dir = Path("output/audio")
    audio_path, srt_path = generate_audio_and_srt(script, audio_dir)

    # Video with unique style
    style_idx = get_next_style_index()
    video_dir = Path("output/video")
    video_name = "short_" + "_".join(topic.lower().split()[:5])
    video_path = assemble_short(audio_path, srt_path, video_dir, video_name, style_idx)

    # Title + description (varied CTA)
    cta = get_next_cta(CTA_PHRASES)
    title = f"🙏 {topic[:90]} #Shorts"
    description = DESCRIPTION_TEMPLATE_SHORT.format(title=topic, cta=cta)

    thumbnail = Path("assets/thumbnail.jpg") if Path("assets/thumbnail.jpg").exists() else None

    video_id = upload_video(
        video_path=video_path, title=title, description=description,
        tags=DEFAULT_TAGS_SHORT, thumbnail_path=thumbnail, channel_id=channel_id,
    )

    record_publication(topic, script, "short", video_id, title, style_idx)
    logging.info(f"✅ SHORT publicado: https://youtube.com/shorts/{video_id}")


def run_long(custom_topic: str = ""):
    """Generate and publish a long-form YouTube video."""
    logging.info(f"=== MODO: LONG — {CHANNEL_NAME} ===")

    channel_id = _get_channel_id()

    if recent_upload_exists(channel_id):
        logging.warning("Cooldown activo — abortando.")
        return

    topic = custom_topic.strip() if custom_topic.strip() else pick_unique_topic(LONG_TOPICS)
    logging.info(f"Topic: {topic}")

    # Generate multi-segment script
    segments = generate_long_script(topic)
    logging.info(f"Generados {len(segments)} segmentos.")

    # Generate audio for each segment
    audio_segments = []
    audio_dir = Path("output/audio_long")
    audio_dir.mkdir(parents=True, exist_ok=True)

    full_script = ""
    chapter_timestamps = []
    cumulative_time = 0.0

    for i, seg in enumerate(segments):
        seg_text = seg["text"]
        seg_title = seg.get("title", f"Capítulo {i+1}")
        full_script += seg_text + " "

        audio_path, srt_path = generate_audio_and_srt(seg_text, audio_dir / f"seg_{i:03d}")

        # Estimate duration for chapters
        from scripts.assemble_video import _get_duration
        dur = _get_duration(audio_path)
        minutes = int(cumulative_time // 60)
        seconds = int(cumulative_time % 60)
        chapter_timestamps.append(f"{minutes}:{seconds:02d} — {seg_title}")
        cumulative_time += dur

        audio_segments.append((audio_path, srt_path, seg_title))

    # Assemble long video
    style_idx = get_next_style_index()
    video_dir = Path("output/video")
    video_name = "long_" + "_".join(topic.lower().split()[:5])
    video_path = assemble_long(audio_segments, video_dir, video_name, style_idx)

    # Title + description
    cta = get_next_cta(CTA_PHRASES)
    title = f"🙏 {topic[:95]}"
    chapters_text = "\n".join(chapter_timestamps)
    description = DESCRIPTION_TEMPLATE_LONG.format(title=topic, cta=cta, chapters=chapters_text)

    thumbnail = Path("assets/thumbnail.jpg") if Path("assets/thumbnail.jpg").exists() else None

    video_id = upload_video(
        video_path=video_path, title=title, description=description,
        tags=DEFAULT_TAGS_LONG, thumbnail_path=thumbnail, channel_id=channel_id,
    )

    record_publication(topic, full_script, "long", video_id, title, style_idx)
    logging.info(f"✅ LONG video publicado: https://youtube.com/watch?v={video_id}")


def main():
    """Entry point — decides short vs long based on CLI argument."""
    video_format = "short"
    custom_topic = ""

    if len(sys.argv) > 1:
        arg1 = sys.argv[1].strip().lower()
        if arg1 in ("short", "long"):
            video_format = arg1
            custom_topic = sys.argv[2] if len(sys.argv) > 2 else ""
        else:
            custom_topic = sys.argv[1]

    if video_format == "long":
        run_long(custom_topic)
    else:
        run_short(custom_topic)


if __name__ == "__main__":
    main()

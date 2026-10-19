# main.py
"""Orchestrator for the autonomous YouTube Shorts bot.
It performs the full pipeline:
1. Determine the topic (either from input or randomly chosen).
2. Check the cooldown lock – abort if a video was posted within the configured window.
3. Generate a script via OpenRouter cascade.
4. Produce audio (MP3) and subtitles (SRT).
5. Assemble the final vertical video with background, overlay and optional music.
6. Upload the video to YouTube.
"""
import logging
import os
import random
import sys
from pathlib import Path

from config import (
    CHANNEL_NAME,
    PUBLISH_TIMES,
    OPENROUTER_MODELS,
    COOLDOWN_MINUTES,
    YOUTUBE_TOKEN_PATH,
    CLIENT_SECRET_PATH,
    DEFAULT_TAGS,
    CTA_TEXT,
    DESCRIPTION_TEMPLATE,
)

# Local imports – the scripts reside in the same package directory.
from scripts.generate_script import generate_script
from scripts.generate_audio import generate_audio_and_srt
from scripts.assemble_video import assemble_video
from scripts.publish_youtube import upload_video
from scripts.lock import recent_upload_exists

logging.basicConfig(level=logging.INFO)

def _pick_topic(custom_topic: str = "") -> str:
    if custom_topic:
        return custom_topic
    # Simple fallback list of biblical themes – can be expanded.
    topics = [
        "El valor de David contra Goliat",
        "La perseverancia de Job",
        "El milagro del pan y los peces",
        "La fe de Abraham",
        "El amor del buen pastor",
        "La sabiduría de Salomón",
        "El poder del perdón de José",
    ]
    return random.choice(topics)

def _get_channel_id() -> str:
    # Reads channel ID from the token JSON ("channel_id" field is not standard);
    # alternatively, you can store it in an env var.
    import json
    if not YOUTUBE_TOKEN_PATH.is_file():
        raise FileNotFoundError("YouTube token JSON not found.")
    data = json.loads(YOUTUBE_TOKEN_PATH.read_text())
    return data.get("channel_id") or os.getenv("YOUTUBE_CHANNEL_ID")

def main(custom_topic: str = ""):
    logging.info("Starting YouTube Shorts orchestrator.")
    channel_id = _get_channel_id()
    if not channel_id:
        logging.error("Channel ID not available. Set YOUTUBE_CHANNEL_ID env var or include it in token JSON.")
        sys.exit(1)

    # Cooldown lock – abort if a recent upload exists.
    if recent_upload_exists(channel_id):
        logging.warning("Recent upload detected within cooldown period – aborting this run.")
        return

    topic = _pick_topic(custom_topic)
    logging.info(f"Selected topic: {topic}")
    script = generate_script(topic)
    logging.info(f"Generated script: {script}")

    # Directories for intermediate artefacts
    audio_dir = Path("output/audio")
    video_dir = Path("output/video")
    audio_path, srt_path = generate_audio_and_srt(script, audio_dir)

    video_name = "short_" + "_".join(topic.lower().split())[:30]
    video_path = assemble_video(audio_path, srt_path, video_dir, video_name)

    # Build description and title – title limited to 100 chars for Shorts.
    title = f"{topic[:95]}"  # truncate if necessary
    description = DESCRIPTION_TEMPLATE.format(title=title, cta=CTA_TEXT)

    # Optional thumbnail – you can generate one dynamically; here we use a placeholder if exists.
    thumbnail_path = Path("assets/thumbnail.jpg") if Path("assets/thumbnail.jpg").exists() else None

    video_id = upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=DEFAULT_TAGS,
        thumbnail_path=thumbnail_path,
        channel_id=channel_id,
    )
    logging.info(f"Successfully uploaded Shorts – video ID: {video_id}")

if __name__ == "__main__":
    topic_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    main(topic_arg)

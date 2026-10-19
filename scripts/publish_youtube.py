# publish_youtube.py
"""Upload a prepared video (Short or Long) to YouTube.
Uses the Google API client with an OAuth refresh token (stored in YOUTUBE_TOKEN_JSON secret).
Includes automatic refresh, error resilience and NATIVE MULTILINGUAL LOCALIZATION
so YouTube displays title and description translated into English, Portuguese, French,
German, Italian, Hindi, Arabic, Russian, Japanese, Korean, Indonesian and Tagalog.
"""
import logging
import os
import sys
from pathlib import Path
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import (
    YOUTUBE_TOKEN_PATH,
    CLIENT_SECRET_PATH,
    DEFAULT_TAGS_SHORT,
    DEFAULT_TAGS_LONG,
    CTA_PHRASES,
    DESCRIPTION_TEMPLATE_SHORT,
)
from scripts.multilingual import generate_localizations

logging.basicConfig(level=logging.INFO)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

def _load_credentials() -> Credentials:
    if not YOUTUBE_TOKEN_PATH.is_file():
        raise FileNotFoundError(f"YouTube token file not found at {YOUTUBE_TOKEN_PATH}. Ensure YOUTUBE_TOKEN_JSON secret is set.")
    
    creds = Credentials.from_authorized_user_file(str(YOUTUBE_TOKEN_PATH), scopes=SCOPES)
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        YOUTUBE_TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds

def upload_video(
    video_path: Path,
    title: str,
    description: str,
    tags: List[str] = None,
    thumbnail_path: Path = None,
    channel_id: str = None,
) -> str:
    """Upload video to YouTube with native multilingual localizations."""
    creds = _load_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    # Generate multilingual localizations for worldwide reach
    localizations = generate_localizations(title, description)
    logging.info(f"Generated {len(localizations)} multilingual localizations (EN, PT, FR, DE, IT, HI, AR, RU, JA, KO, ID, TL).")

    body = {
        "snippet": {
            "title": title[:100],  # YouTube title limit
            "description": description[:5000],
            "tags": tags or DEFAULT_TAGS_SHORT,
            "categoryId": "22",  # People & Blogs
            "defaultLanguage": "es",
            "defaultAudioLanguage": "es",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
        "localizations": localizations,
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    logging.info(f"Video uploaded successfully. Video ID: {video_id}")

    if thumbnail_path and Path(thumbnail_path).is_file():
        try:
            thumb_request = youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg"),
            )
            thumb_request.execute()
            logging.info("Thumbnail uploaded successfully.")
        except Exception as e:
            logging.warning(f"Could not upload thumbnail: {e}")

    return video_id

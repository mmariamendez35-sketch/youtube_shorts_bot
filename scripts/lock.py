# lock.py
"""Cooldown lock utility.
Checks YouTube for recent uploads and aborts if a video was posted within the configured cooldown period.
Includes fallbacks to avoid blocking in case of API hiccups.
"""
import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import YOUTUBE_TOKEN_PATH, COOLDOWN_MINUTES

logging.basicConfig(level=logging.INFO)

def _load_credentials() -> Credentials:
    if not YOUTUBE_TOKEN_PATH.is_file():
        raise FileNotFoundError(f"YouTube token file not found at {YOUTUBE_TOKEN_PATH}.")
    creds = Credentials.from_authorized_user_file(str(YOUTUBE_TOKEN_PATH))
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
    return creds

def recent_upload_exists(channel_id: str) -> bool:
    """Return True if a video was uploaded to the channel within COOLDOWN_MINUTES."""
    try:
        creds = _load_credentials()
        youtube = build("youtube", "v3", credentials=creds)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=COOLDOWN_MINUTES)
        
        request = youtube.search().list(
            part="id,snippet",
            channelId=channel_id,
            maxResults=3,
            order="date",
            type="video",
        )
        response = request.execute()
        for item in response.get("items", []):
            pub_str = item["snippet"]["publishedAt"].replace("Z", "+00:00")
            published = datetime.fromisoformat(pub_str)
            if published > cutoff:
                logging.info(f"Found recent upload {item['id']['videoId']} at {published} (within cooldown of {COOLDOWN_MINUTES}m).")
                return True
        return False
    except Exception as e:
        logging.warning(f"Cooldown check warning (proceeding safely): {e}")
        return False

# lock.py
"""Cooldown lock utility.
Checks YouTube for recent uploads and aborts if a video was posted within the configured cooldown period.
"""
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import YOUTUBE_TOKEN_PATH, CLIENT_SECRET_PATH, COOLDOWN_MINUTES

logging.basicConfig(level=logging.INFO)

def _load_credentials() -> Credentials:
    if not YOUTUBE_TOKEN_PATH.is_file():
        raise FileNotFoundError("YouTube token file not found. Ensure YOUTUBE_TOKEN_JSON secret is set.")
    creds = Credentials.from_authorized_user_file(str(YOUTUBE_TOKEN_PATH), scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"])
    return creds

def recent_upload_exists(channel_id: str) -> bool:
    """Return True if a video was uploaded to the channel within COOLDOWN_MINUTES.
    """
    creds = _load_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=COOLDOWN_MINUTES)
    request = youtube.search().list(
        part="id,snippet",
        channelId=channel_id,
        maxResults=5,
        order="date",
        type="video",
    )
    response = request.execute()
    for item in response.get("items", []):
        published = datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
        if published > cutoff:
            logging.info(f"Found recent upload {item['id']['videoId']} at {published} (within cooldown).")
            return True
    return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python lock.py <channel_id>")
        sys.exit(1)
    ch_id = sys.argv[1]
    print(recent_upload_exists(ch_id))

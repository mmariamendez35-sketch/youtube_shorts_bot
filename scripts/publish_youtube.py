# publish_youtube.py
"""Upload a prepared Shorts video to YouTube.
Uses the Google API client with a persisted refresh token (stored in YOUTUBE_TOKEN_JSON secret).
Creates a vertical short, sets title, description, tags, and uploads a thumbnail.
"""
import logging
import os
from pathlib import Path
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import (
    YOUTUBE_TOKEN_PATH,
    CLIENT_SECRET_PATH,
    DEFAULT_TAGS,
    CTA_TEXT,
    DESCRIPTION_TEMPLATE,
)

logging.basicConfig(level=logging.INFO)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]

def _load_credentials() -> Credentials:
    if not YOUTUBE_TOKEN_PATH.is_file():
        raise FileNotFoundError("YouTube token file not found. Ensure YOUTUBE_TOKEN_JSON secret is set.")
    creds = Credentials.from_authorized_user_file(str(YOUTUBE_TOKEN_PATH), scopes=SCOPES)
    # refresh if needed
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        # Save refreshed token back (GitHub Actions will handle persistence via secret)
        YOUTUBE_TOKEN_PATH.write_text(creds.to_json())
    return creds

def upload_video(
    video_path: Path,
    title: str,
    description: str,
    tags: List[str] = None,
    thumbnail_path: Path = None,
    channel_id: str = None,
) -> str:
    """Upload *video_path* to YouTube and return the video ID.
    Args:
        video_path: Path to the MP4 file.
        title: Video title (max 100 chars for Shorts).
        description: Full description text.
        tags: List of tag strings.
        thumbnail_path: Optional path to a vertical thumbnail image.
        channel_id: Optional channel ID (used for logging).
    Returns:
        The YouTube video ID.
    """
    creds = _load_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or DEFAULT_TAGS,
            "categoryId": "22",  # People & Blogs – adjust if needed
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "publishAt": None,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f"Upload progress: {int(status.progress() * 100)}%")
    video_id = response["id"]
    logging.info(f"Uploaded video ID: {video_id}")

    # Set thumbnail if provided
    if thumbnail_path and thumbnail_path.is_file():
        thumb_request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg"),
        )
        thumb_response = thumb_request.execute()
        logging.info("Thumbnail uploaded.")
    else:
        logging.info("No thumbnail provided or file missing.")
    return video_id

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python publish_youtube.py <video_path> <title> <channel_id> [thumbnail_path]")
        sys.exit(1)
    video = Path(sys.argv[1])
    title = sys.argv[2]
    channel = sys.argv[3]
    thumb = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    desc = DESCRIPTION_TEMPLATE.format(title=title, cta=CTA_TEXT)
    upload_video(video, title, desc, tags=DEFAULT_TAGS, thumbnail_path=thumb, channel_id=channel)

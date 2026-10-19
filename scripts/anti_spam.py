# anti_spam.py
"""Anti-spam and history tracker.
Ensures no topic/script is repeated and rotates themes to keep content fresh.
YouTube's algorithm penalizes repetitive content — this module prevents that.
"""
import hashlib
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import HISTORY_FILE, MAX_HISTORY, MIN_TOPIC_DISTANCE

logging.basicConfig(level=logging.INFO)


def _load_history() -> list:
    """Load publish history from JSON file."""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_history(history: list) -> None:
    """Save publish history, keeping only the last MAX_HISTORY entries."""
    trimmed = history[-MAX_HISTORY:]
    HISTORY_FILE.write_text(json.dumps(trimmed, indent=2, ensure_ascii=False), encoding="utf-8")


def _text_fingerprint(text: str) -> str:
    """Create a fingerprint of the text for similarity checking."""
    # Normalize: lowercase, remove punctuation, sort words
    words = sorted(set(text.lower().split()))
    return hashlib.md5(" ".join(words).encode()).hexdigest()


def is_topic_recent(topic: str) -> bool:
    """Check if this topic was used in the last MIN_TOPIC_DISTANCE publications."""
    history = _load_history()
    recent = history[-MIN_TOPIC_DISTANCE:] if history else []
    topic_lower = topic.lower().strip()
    for entry in recent:
        if entry.get("topic", "").lower().strip() == topic_lower:
            logging.info(f"Topic '{topic}' was recently used — skipping.")
            return True
    return False


def is_script_duplicate(script: str) -> bool:
    """Check if a very similar script was already published."""
    history = _load_history()
    new_fp = _text_fingerprint(script)
    for entry in history:
        if entry.get("fingerprint") == new_fp:
            logging.info("Script fingerprint matches a previous publication — duplicate detected.")
            return True
    return False


def pick_unique_topic(topics: List[str]) -> str:
    """Pick a topic that hasn't been used recently, cycling through all options."""
    history = _load_history()
    used_topics = [e.get("topic", "").lower().strip() for e in history[-len(topics):]]

    # Filter out recently used topics
    available = [t for t in topics if t.lower().strip() not in used_topics]
    if not available:
        # All topics have been used recently; reset and pick randomly
        available = topics

    return random.choice(available)


def record_publication(
    topic: str,
    script: str,
    video_format: str,
    video_id: str = "",
    title: str = "",
    style_index: int = 0,
) -> None:
    """Record a publication in the history."""
    history = _load_history()
    history.append({
        "topic": topic,
        "fingerprint": _text_fingerprint(script),
        "format": video_format,
        "video_id": video_id,
        "title": title,
        "style_index": style_index,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })
    _save_history(history)
    logging.info(f"Recorded publication: {topic} ({video_format}) — {video_id}")


def get_next_style_index() -> int:
    """Return a style index that hasn't been used recently to vary visuals."""
    history = _load_history()
    recent_styles = [e.get("style_index", 0) for e in history[-8:]]
    # Pick a style not used in last 8 videos
    for i in range(10):
        if i not in recent_styles:
            return i
    return random.randint(0, 9)


def get_next_cta(cta_list: List[str]) -> str:
    """Pick a CTA phrase not used recently."""
    history = _load_history()
    # We don't store CTAs directly, so just rotate based on count
    idx = len(history) % len(cta_list)
    return cta_list[idx]

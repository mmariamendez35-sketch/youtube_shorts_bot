# generate_audio.py
"""Generate voice audio (MP3) and kinetic subtitles (SRT) from a script.
Uses gTTS as primary engine with exponential backoff retries.
Enhances vocal audio with sanctuary warmth and EQ.
Groups words into natural, high-impact phrase chunks for viral mobile retention.
"""
import os
import subprocess
import time
import logging
from pathlib import Path
from typing import List, Tuple

from gtts import gTTS
from retrying import retry

from config import TTS_LANGUAGE, TTS_SLOW, MAX_TTS_RETRIES

logging.basicConfig(level=logging.INFO)

def _sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in name)

@retry(stop_max_attempt_number=MAX_TTS_RETRIES, wait_exponential_multiplier=1000, wait_exponential_max=8000)
def _tts_gtts(text: str, out_path: Path) -> None:
    tts = gTTS(text=text, lang=TTS_LANGUAGE, slow=TTS_SLOW)
    tts.save(str(out_path))

def _tts_espeak(text: str, out_path: Path) -> None:
    wav_path = out_path.with_suffix('.wav')
    cmd = [
        "espeak-ng",
        "-v", f"{TTS_LANGUAGE}",
        "-s", "150",
        "-w", str(wav_path),
        text,
    ]
    subprocess.run(cmd, check=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", str(out_path)], check=True)
    wav_path.unlink(missing_ok=True)

def _enhance_voice(audio_path: Path) -> None:
    """Enhance raw TTS voice with sacred warmth, EQ, and subtle acoustic presence."""
    temp_enhanced = audio_path.with_name(f"enh_{audio_path.name}")
    af = "equalizer=f=220:width_type=o:width=1.5:g=3.0,equalizer=f=3500:width_type=o:width=2:g=-2.0,aecho=0.8:0.88:35:0.18,volume=1.1"
    try:
        res = subprocess.run([
            "ffmpeg", "-y", "-i", str(audio_path),
            "-af", af,
            "-codec:a", "libmp3lame", "-b:a", "192k",
            str(temp_enhanced)
        ], capture_output=True, text=True)
        if res.returncode == 0 and temp_enhanced.exists():
            temp_enhanced.replace(audio_path)
            logging.info("Vocal track enhanced with sanctuary acoustic presence.")
    except Exception as e:
        logging.warning(f"Voice enhancement skipped: {e}")
        if temp_enhanced.exists():
            temp_enhanced.unlink(missing_ok=True)

def _split_into_phrases(text: str, max_words: int = 4) -> List[str]:
    """Split text into natural, readable phrases of 3 to 5 words for mobile viewers."""
    raw_words = text.replace("\n", " ").split()
    phrases = []
    current = []
    
    for w in raw_words:
        current.append(w)
        # Break phrase if it ends with punctuation or reaches max length
        has_punct = any(w.endswith(p) for p in [".", ",", "!", "?", ";", ":"])
        if len(current) >= max_words or (len(current) >= 2 and has_punct):
            phrases.append(" ".join(current))
            current = []
            
    if current:
        phrases.append(" ".join(current))
        
    return phrases

def _estimate_durations(phrases: List[str], total_seconds: float) -> List[Tuple[float, float, str]]:
    """Distribute total_seconds proportionally based on character length for accurate sync."""
    total_chars = sum(len(p) for p in phrases) or 1
    timestamps = []
    cur = 0.0
    for p in phrases:
        # Weight duration by character length
        weight = len(p) / total_chars
        dur = weight * total_seconds
        start = cur
        end = cur + dur
        timestamps.append((start, end, p))
        cur = end
    return timestamps

def _format_timestamp(secs: float) -> str:
    hrs = int(secs // 3600)
    mins = int((secs % 3600) // 60)
    secs_int = int(secs % 60)
    ms = int((secs - int(secs)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs_int:02d},{ms:03d}"

def _write_srt(timestamps: List[Tuple[float, float, str]], srt_path: Path) -> None:
    with srt_path.open('w', encoding='utf-8') as f:
        for idx, (start, end, phrase) in enumerate(timestamps, start=1):
            f.write(f"{idx}\n")
            f.write(f"{_format_timestamp(start)} --> {_format_timestamp(end)}\n")
            f.write(f"{phrase}\n\n")

def generate_audio_and_srt(script: str, output_dir: Path) -> Tuple[Path, Path]:
    """Generate audio MP3 and SRT file for *script*.
    Returns (audio_path, srt_path).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = _sanitize_filename(script[:30])
    audio_path = output_dir / f"{base_name}.mp3"
    srt_path = output_dir / f"{base_name}.srt"

    # Try gTTS first
    try:
        logging.info("Generating audio with gTTS...")
        _tts_gtts(script, audio_path)
    except Exception as e:
        logging.warning(f"gTTS failed ({e}); falling back to espeak-ng.")
        _tts_espeak(script, audio_path)

    # Enhance vocal warmth & presence
    _enhance_voice(audio_path)

    # Estimate duration using ffprobe
    try:
        probe = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(audio_path)
        ], capture_output=True, text=True, check=True)
        import json
        duration = float(json.loads(probe.stdout)["format"]["duration"])
    except Exception:
        duration = max(5.0, len(script.split()) * 0.45)

    phrases = _split_into_phrases(script, max_words=4)
    timestamps = _estimate_durations(phrases, duration)
    _write_srt(timestamps, srt_path)
    logging.info(f"Audio saved to {audio_path} ({duration:.1f}s), {len(phrases)} subtitle cues to {srt_path}")
    return audio_path, srt_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_audio.py <script>")
        sys.exit(1)
    script_text = sys.argv[1]
    out_dir = Path("output/audio")
    generate_audio_and_srt(script_text, out_dir)

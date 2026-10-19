# generate_audio.py
"""Generate voice audio (MP3) and subtitles (SRT) from a script.
Uses gTTS as primary engine with exponential backoff retries.
Falls back to espeak-ng (requires it to be installed and in PATH).
Produces:
  - audio_path: path to .mp3 file
  - srt_path:   path to .srt subtitle file (word‑by‑word timing approx.)
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
    # espeak-ng must be installed; we use wave output then convert to mp3 via ffmpeg
    wav_path = out_path.with_suffix('.wav')
    cmd = [
        "espeak-ng",
        "-v", f"{TTS_LANGUAGE}",
        "-s", "150",  # speed (words per minute)
        "-w", str(wav_path),
        text,
    ]
    subprocess.run(cmd, check=True)
    # Convert wav to mp3 using ffmpeg (ffmpeg must be in PATH)
    subprocess.run(["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", str(out_path)], check=True)
    wav_path.unlink(missing_ok=True)

def _split_words(text: str) -> List[str]:
    # Very naive split – good enough for short scripts.
    return text.replace("\n", " ").split()

def _estimate_durations(words: List[str], total_seconds: float) -> List[Tuple[float, float, str]]:
    """Distribute total_seconds equally among words and return list of (start, end, word)."""
    per_word = total_seconds / max(len(words), 1)
    timestamps = []
    cur = 0.0
    for w in words:
        start = cur
        end = cur + per_word
        timestamps.append((start, end, w))
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
        for idx, (start, end, word) in enumerate(timestamps, start=1):
            f.write(f"{idx}\n")
            f.write(f"{_format_timestamp(start)} --> {_format_timestamp(end)}\n")
            f.write(f"{word}\n\n")

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

    # Rough estimate of duration using ffprobe (requires ffmpeg installed)
    try:
        import subprocess, json
        probe = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(audio_path)
        ], capture_output=True, text=True, check=True)
        duration = float(json.loads(probe.stdout)["format"]["duration"])
    except Exception:
        duration = max(5.0, len(script.split()) * 0.5)  # fallback estimate

    words = _split_words(script)
    timestamps = _estimate_durations(words, duration)
    _write_srt(timestamps, srt_path)
    logging.info(f"Audio saved to {audio_path}, subtitles to {srt_path}")
    return audio_path, srt_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_audio.py <script>")
        sys.exit(1)
    script_text = sys.argv[1]
    out_dir = Path("output/audio")
    generate_audio_and_srt(script_text, out_dir)

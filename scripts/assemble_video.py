# assemble_video.py
"""Assemble the final Shorts video using ffmpeg.
Inputs:
  - audio_path (mp3)
  - srt_path (subtitles)
Outputs:
  - video_path (mp4) in vertical 1080x1920 format.
The video consists of:
  1. Loopable background video (assets/background.mp4).
  2. Overlay image (assets/overlay.png) centered.
  3. Subtitles rendered at the bottom.
  4. Background music mixed with the voice (optional).
"""
import os
import logging
from pathlib import Path
import ffmpeg
from config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    FPS,
    BACKGROUND_VIDEO,
    OVERLAY_IMAGE,
    MUSIC_FILE,
)

logging.basicConfig(level=logging.INFO)

def _ensure_path(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def assemble_video(audio_path: Path, srt_path: Path, output_dir: Path, video_name: str) -> Path:
    """Create the final video.
    Returns the path to the generated MP4.
    """
    output_dir = _ensure_path(output_dir)
    video_path = output_dir / f"{video_name}.mp4"

    # Input streams
    background = ffmpeg.input(str(BACKGROUND_VIDEO), stream_loop=-1)
    overlay = ffmpeg.input(str(OVERLAY_IMAGE))
    audio = ffmpeg.input(str(audio_path))
    subtitles = ffmpeg.input(str(srt_path))
    # Optional music
    music = None
    if Path(MUSIC_FILE).exists():
        music = ffmpeg.input(str(MUSIC_FILE))

    # Scale background to desired resolution, ensure it loops long enough
    # We'll trim to match audio duration (+1 sec buffer)
    # First, get audio duration via ffprobe
    try:
        import json, subprocess
        probe = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(audio_path)
        ], capture_output=True, text=True, check=True)
        duration = float(json.loads(probe.stdout)["format"]["duration"])
    except Exception:
        duration = 10.0

    bg = (
        background.filter('scale', VIDEO_WIDTH, VIDEO_HEIGHT)
        .filter('trim', duration=duration + 1)
        .filter('setpts', 'PTS-STARTPTS')
    )

    # Overlay image (centered)
    overlay_scaled = (
        overlay.filter('scale', w='if(gte(iw,ih),iw,ih)', h='if(gte(iw,ih),iw,ih)')
        .filter('pad', width=VIDEO_WIDTH, height=VIDEO_HEIGHT, x='(ow-iw)/2', y='(oh-ih)/2')
    )

    video = ffmpeg.concat(bg, overlay_scaled, v=1, a=0).filter('overlay')

    # Add subtitles (burned in)
    video = video.filter('subtitles', str(srt_path), force_style='Fontsize=48,PrimaryColour=&HFFFFFFFF')

    # Mix audio and optional music
    if music:
        # Reduce music volume to 20% and mix
        mixed_audio = ffmpeg.filter_(
            [audio.filter('volume', 1.0), music.filter('volume', 0.2)],
            'amix', dropout_transition=2, duration='shortest'
        )
    else:
        mixed_audio = audio

    # Output
    (
        ffmpeg.output(
            video,
            mixed_audio,
            str(video_path),
            vcodec='libx264',
            acodec='aac',
            video_bitrate='2M',
            audio_bitrate='128k',
            r=FPS,
            preset='medium',
            movflags='+faststart',
            format='mp4',
            loglevel='error',
        )
        .overwrite_output()
        .run()
    )
    logging.info(f"Video assembled at {video_path}")
    return video_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python assemble_video.py <audio_path> <srt_path> <output_name>")
        sys.exit(1)
    audio = Path(sys.argv[1])
    srt = Path(sys.argv[2])
    name = sys.argv[3]
    out_dir = Path("output/video")
    assemble_video(audio, srt, out_dir, name)

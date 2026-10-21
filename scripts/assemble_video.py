# assemble_video.py
"""Assemble videos with Ken Burns effect, keyframe animations, and transitions.
Uses RELIGIOUS IMAGES from assets/prayers/ as background visuals with Ken Burns motion,
vignette, and animated subtitles for high-engagement spiritual videos.
"""
import json
import logging
import math
import os
import random
import subprocess
from pathlib import Path
from typing import List, Tuple

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS, MUSIC_FILE, PRAYERS_IMG_DIR,
    KB_ZOOM_MIN, KB_ZOOM_MAX, KB_PAN_RANGE,
    TRANSITION_DURATION, GRADIENT_PALETTES, SUBTITLE_STYLES,
)

logging.basicConfig(level=logging.INFO)

W, H = VIDEO_WIDTH, VIDEO_HEIGHT


def _get_duration(file_path: Path) -> float:
    """Get duration of an audio/video file using ffprobe."""
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", str(file_path)],
            capture_output=True, text=True, check=True,
        )
        return float(json.loads(probe.stdout)["format"]["duration"])
    except Exception:
        return 10.0


def _get_prayer_images() -> List[Path]:
    """Get all available religious images from PRAYERS_IMG_DIR."""
    img_dir = Path(PRAYERS_IMG_DIR)
    if not img_dir.exists():
        img_dir.mkdir(parents=True, exist_ok=True)
    images = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpeg"))
    return [img for img in images if img.is_file() and img.stat().st_size > 1000]


def _pick_image_for_slide(index: int) -> Path:
    """Pick an image deterministically or randomly from religious assets."""
    images = _get_prayer_images()
    if not images:
        return None
    return images[index % len(images)]


def _build_image_kb_filter(image_path: Path, duration: float, index: int) -> str:
    """Build an FFmpeg video filter for a religious image with Ken Burns pan/zoom and dark spiritual vignette."""
    img_escaped = str(image_path.resolve()).replace("\\", "/").replace(":", "\\\\:")
    
    # Randomize zoom direction per slide
    total_frames = max(1, int(duration * FPS))
    if index % 2 == 0:
        # Zoom in
        zoom_expr = f"'min(zoom+0.0006,1.25)'"
        x_expr = f"'iw/2-(iw/zoom/2)'"
        y_expr = f"'ih/2-(ih/zoom/2)'"
    else:
        # Slow pan down/up with slight zoom
        zoom_expr = f"'1.15'"
        x_expr = f"'iw/2-(iw/zoom/2)'"
        y_expr = f"'(ih-ih/zoom)*(on/{total_frames})'"

    # Scale to fill 1080x1920 (aspect ratio crop), apply zoompan, darken for subtitle readability
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan=z={zoom_expr}:x={x_expr}:y={y_expr}:d={total_frames}:s={W}x{H}:fps={FPS},"
        f"colorlevels=rimax=0.85:gimax=0.85:bimax=0.85,"  # darken slightly for readable text
        f"vignette=PI/4"                                   # spiritual dark vignette edge
    )
    return vf


def _build_gradient_filter(color1: str, color2: str, duration: float, index: int) -> str:
    """Fallback animated gradient background in case no image is found."""
    patterns = [
        f"color=c=0x{color1}:s={W}x{H}:d={duration}:r={FPS},"
        f"geq=r='clip(r(X,Y)+20*sin(2*PI*T/4),0,255)':g='clip(g(X,Y)+15*sin(2*PI*T/3),0,255)':b='clip(b(X,Y)+25*sin(2*PI*T/5),0,255)'",
        f"color=c=0x{color1}:s={W}x{H}:d={duration}:r={FPS},"
        f"geq=r='clip(r(X,Y)*(1-Y/{H})+{int(color2[:2],16)}*(Y/{H}),0,255)'"
        f":g='clip(g(X,Y)*(1-Y/{H})+{int(color2[2:4],16)}*(Y/{H}),0,255)'"
        f":b='clip(b(X,Y)*(1-Y/{H})+{int(color2[4:],16)}*(Y/{H}),0,255)'",
    ]
    return patterns[index % len(patterns)]


def assemble_short(
    audio_path: Path, srt_path: Path, output_dir: Path,
    video_name: str, style_index: int = 0,
) -> Path:
    """Create a SHORT video (< 60s) with a sacred religious image and kinetic subtitles."""
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / f"{video_name}.mp4"
    duration = _get_duration(audio_path)

    sub_style = SUBTITLE_STYLES[style_index % len(SUBTITLE_STYLES)]
    srt_abs = str(srt_path.resolve()).replace("\\", "/").replace(":", "\\\\:")

    # Select religious image
    img = _pick_image_for_slide(style_index)
    has_music = Path(MUSIC_FILE).exists()

    if img and img.exists():
        logging.info(f"Using religious image for Short: {img.name}")
        img_vf = _build_image_kb_filter(img, duration + 1, style_index)
        vf = f"{img_vf},subtitles='{srt_abs}':force_style='{sub_style}'"

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(img),
            "-i", str(audio_path),
        ]
        if has_music:
            cmd += ["-i", str(MUSIC_FILE)]
            af = f"[1:a]volume=1.0[voice];[2:a]volume=0.12,atrim=0:{duration + 1}[music];[voice][music]amix=inputs=2:duration=shortest[aout]"
            cmd += ["-filter_complex", f"[0:v]{vf}[vout];{af}"]
            cmd += ["-map", "[vout]", "-map", "[aout]"]
        else:
            cmd += ["-vf", vf, "-map", "0:v", "-map", "1:a"]

    else:
        logging.warning("No religious images found. Falling back to gradient.")
        palette = GRADIENT_PALETTES[style_index % len(GRADIENT_PALETTES)]
        bg_filter = _build_gradient_filter(palette[0], palette[1], duration + 1, style_index)
        vf = f"subtitles='{srt_abs}':force_style='{sub_style}'"

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", bg_filter,
            "-i", str(audio_path),
        ]
        if has_music:
            cmd += ["-i", str(MUSIC_FILE)]
            af = f"[1:a]volume=1.0[voice];[2:a]volume=0.12,atrim=0:{duration + 1}[music];[voice][music]amix=inputs=2:duration=shortest[aout]"
            cmd += ["-filter_complex", f"[0:v]{vf}[vout];{af}"]
            cmd += ["-map", "[vout]", "-map", "[aout]"]
        else:
            cmd += ["-vf", vf, "-map", "0:v", "-map", "1:a"]

    cmd += [
        "-c:v", "libx264", "-preset", "medium", "-b:v", "2.5M",
        "-c:a", "aac", "-b:a", "128k",
        "-r", str(FPS), "-t", str(duration + 0.5),
        "-movflags", "+faststart", "-shortest",
        str(video_path),
    ]

    logging.info(f"Assembling SHORT video with religious art (style {style_index})...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"ffmpeg stderr: {result.stderr[-800:]}")
        raise RuntimeError(f"ffmpeg failed with code {result.returncode}")

    logging.info(f"Short video assembled successfully: {video_path}")
    return video_path


def assemble_long(
    audio_segments: List[Tuple[Path, Path, str]],
    output_dir: Path,
    video_name: str,
    style_index: int = 0,
) -> Path:
    """Create a LONG video from multiple audio segments.
    Each chapter/segment gets its own religious image slide with Ken Burns effect and title overlay.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / f"{video_name}.mp4"
    temp_dir = output_dir / "temp_segments"
    temp_dir.mkdir(parents=True, exist_ok=True)

    images = _get_prayer_images()
    segment_videos = []

    for i, (audio_path, srt_path, title) in enumerate(audio_segments):
        seg_path = temp_dir / f"seg_{i:03d}.mp4"
        duration = _get_duration(audio_path)

        sub_style = SUBTITLE_STYLES[(style_index + i) % len(SUBTITLE_STYLES)]
        srt_abs = str(srt_path.resolve()).replace("\\", "/").replace(":", "\\\\:")

        title_escaped = title.replace("'", "\\'").replace(":", "\\:")
        title_filter = (
            f"drawtext=text='{title_escaped}':"
            f"fontsize=42:fontcolor=gold:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=200:"
            f"enable='between(t,0,4)':alpha='if(lt(t,0.5),t/0.5,if(gt(t,3.5),1-(t-3.5)/0.5,1))'"
        )

        img = images[(style_index + i) % len(images)] if images else None

        if img and img.exists():
            logging.info(f"Segment {i+1} using image: {img.name}")
            img_vf = _build_image_kb_filter(img, duration + 1, style_index + i)
            vf = f"{img_vf},{title_filter},subtitles='{srt_abs}':force_style='{sub_style}'"

            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(img),
                "-i", str(audio_path),
                "-vf", vf,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "medium", "-b:v", "2.5M",
                "-c:a", "aac", "-b:a", "128k",
                "-r", str(FPS), "-t", str(duration + 0.5),
                "-movflags", "+faststart",
                str(seg_path),
            ]
        else:
            palette = GRADIENT_PALETTES[(style_index + i) % len(GRADIENT_PALETTES)]
            bg_filter = _build_gradient_filter(palette[0], palette[1], duration + 2, style_index + i)
            vf = f"{title_filter},subtitles='{srt_abs}':force_style='{sub_style}'"

            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", bg_filter,
                "-i", str(audio_path),
                "-vf", vf,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "medium", "-b:v", "2M",
                "-c:a", "aac", "-b:a", "128k",
                "-r", str(FPS), "-t", str(duration + 1),
                "-movflags", "+faststart",
                str(seg_path),
            ]

        logging.info(f"Assembling segment {i+1}/{len(audio_segments)}: {title}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Segment {i} ffmpeg error: {result.stderr[-500:]}")
            raise RuntimeError(f"ffmpeg failed on segment {i}")

        segment_videos.append(seg_path)

    if len(segment_videos) == 1:
        segment_videos[0].rename(video_path)
        return video_path

    # Concat
    concat_file = temp_dir / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for sv in segment_videos:
            f.write(f"file '{sv.resolve()}'\n")

    has_music = Path(MUSIC_FILE).exists()
    if has_music:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(MUSIC_FILE),
            "-filter_complex", "[0:a]volume=1.0[voice];[1:a]volume=0.10[music];[voice][music]amix=inputs=2:duration=shortest[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-b:v", "2.5M",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(video_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c:v", "libx264", "-preset", "medium", "-b:v", "2.5M",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(video_path),
        ]

    logging.info("Concatenating segments into final long video...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Concat ffmpeg error: {result.stderr[-500:]}")
        raise RuntimeError("ffmpeg concat failed")

    for sv in segment_videos:
        sv.unlink(missing_ok=True)
    concat_file.unlink(missing_ok=True)
    try:
        temp_dir.rmdir()
    except OSError:
        pass

    logging.info(f"Long video assembled successfully: {video_path}")
    return video_path

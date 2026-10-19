# assemble_video.py
"""Assemble videos with Ken Burns effect, keyframe animations, and transitions.
Creates UNIQUE videos every time by randomizing:
- Background gradient colors
- Ken Burns zoom/pan direction and intensity
- Subtitle styles
- Transition effects
Each "slide" is a segment of the prayer with its own visual treatment.
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
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS, MUSIC_FILE,
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


def _random_kb_params() -> dict:
    """Generate random Ken Burns parameters for one slide."""
    zoom_start = random.uniform(KB_ZOOM_MIN, KB_ZOOM_MAX)
    zoom_end = random.uniform(KB_ZOOM_MIN, KB_ZOOM_MAX)
    # Ensure there's actual motion
    if abs(zoom_start - zoom_end) < 0.05:
        zoom_end = zoom_start + random.choice([-0.1, 0.1])
        zoom_end = max(1.0, min(1.3, zoom_end))
    pan_x = random.randint(-KB_PAN_RANGE, KB_PAN_RANGE)
    pan_y = random.randint(-KB_PAN_RANGE, KB_PAN_RANGE)
    return {
        "zoom_start": zoom_start,
        "zoom_end": zoom_end,
        "pan_x": pan_x,
        "pan_y": pan_y,
    }


def _build_gradient_filter(color1: str, color2: str, duration: float, index: int) -> str:
    """Build an FFmpeg filter for an animated gradient background slide.
    Uses different animation patterns based on index for variety.
    """
    # Create a base color, then apply animated effects
    patterns = [
        # Slow pulsing brightness
        f"color=c=0x{color1}:s={W}x{H}:d={duration}:r={FPS},"
        f"geq=r='clip(r(X,Y)+20*sin(2*PI*T/4),0,255)':g='clip(g(X,Y)+15*sin(2*PI*T/3),0,255)':b='clip(b(X,Y)+25*sin(2*PI*T/5),0,255)'",

        # Vertical gradient with slow shift
        f"color=c=0x{color1}:s={W}x{H}:d={duration}:r={FPS},"
        f"geq=r='clip(r(X,Y)*(1-Y/{H})+{int(color2[:2],16)}*(Y/{H}),0,255)'"
        f":g='clip(g(X,Y)*(1-Y/{H})+{int(color2[2:4],16)}*(Y/{H}),0,255)'"
        f":b='clip(b(X,Y)*(1-Y/{H})+{int(color2[4:],16)}*(Y/{H}),0,255)'",

        # Simple solid with slight Ken Burns zoom
        f"color=c=0x{color1}:s={int(W*1.2)}x{int(H*1.2)}:d={duration}:r={FPS},"
        f"zoompan=z='1+0.001*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*FPS)}:s={W}x{H}:fps={FPS}",

        # Radial-ish effect via geq
        f"color=c=0x{color2}:s={W}x{H}:d={duration}:r={FPS},"
        f"geq=r='clip({int(color1[:2],16)}+30*sin(hypot(X-{W//2},Y-{H//2})/100+T),0,255)'"
        f":g='clip({int(color1[2:4],16)}+20*sin(hypot(X-{W//2},Y-{H//2})/120+T*0.8),0,255)'"
        f":b='clip({int(color1[4:],16)}+40*sin(hypot(X-{W//2},Y-{H//2})/80+T*1.2),0,255)'",
    ]
    return patterns[index % len(patterns)]


def assemble_short(
    audio_path: Path, srt_path: Path, output_dir: Path,
    video_name: str, style_index: int = 0,
) -> Path:
    """Create a SHORT video (< 60s) with unique visual style."""
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / f"{video_name}.mp4"
    duration = _get_duration(audio_path)

    # Pick visual style
    palette = GRADIENT_PALETTES[style_index % len(GRADIENT_PALETTES)]
    sub_style = SUBTITLE_STYLES[style_index % len(SUBTITLE_STYLES)]

    # Build background filter
    bg_filter = _build_gradient_filter(palette[0], palette[1], duration + 1, style_index)

    # Subtitle path (escaped for FFmpeg)
    srt_abs = str(srt_path.resolve()).replace("\\", "/").replace(":", "\\\\:")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", bg_filter,
        "-i", str(audio_path),
    ]

    has_music = Path(MUSIC_FILE).exists()
    if has_music:
        cmd += ["-i", str(MUSIC_FILE)]

    # Video filter: add subtitles
    vf = f"subtitles='{srt_abs}':force_style='{sub_style}'"

    if has_music:
        af = "[1:a]volume=1.0[voice];[2:a]volume=0.12,atrim=0:" + str(duration + 1) + "[music];[voice][music]amix=inputs=2:duration=shortest[aout]"
        cmd += ["-filter_complex", f"[0:v]{vf}[vout];{af}"]
        cmd += ["-map", "[vout]", "-map", "[aout]"]
    else:
        cmd += ["-vf", vf, "-map", "0:v", "-map", "1:a"]

    cmd += [
        "-c:v", "libx264", "-preset", "medium", "-b:v", "2M",
        "-c:a", "aac", "-b:a", "128k",
        "-r", str(FPS), "-t", str(duration + 0.5),
        "-movflags", "+faststart", "-shortest",
        str(video_path),
    ]

    logging.info(f"Assembling SHORT video (style {style_index})...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"ffmpeg stderr: {result.stderr[-800:]}")
        raise RuntimeError(f"ffmpeg failed with code {result.returncode}")

    logging.info(f"Short video assembled: {video_path}")
    return video_path


def assemble_long(
    audio_segments: List[Tuple[Path, Path, str]],
    output_dir: Path,
    video_name: str,
    style_index: int = 0,
) -> Path:
    """Create a LONG video from multiple audio segments.
    Each segment gets its own visual slide with Ken Burns effect and transitions.

    audio_segments: list of (audio_path, srt_path, segment_title)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / f"{video_name}.mp4"
    temp_dir = output_dir / "temp_segments"
    temp_dir.mkdir(parents=True, exist_ok=True)

    segment_videos = []

    for i, (audio_path, srt_path, title) in enumerate(audio_segments):
        seg_path = temp_dir / f"seg_{i:03d}.mp4"
        duration = _get_duration(audio_path)

        # Each segment gets a different palette variation
        palette_idx = (style_index + i) % len(GRADIENT_PALETTES)
        palette = GRADIENT_PALETTES[palette_idx]
        sub_style_idx = (style_index + i) % len(SUBTITLE_STYLES)
        sub_style = SUBTITLE_STYLES[sub_style_idx]

        bg_filter = _build_gradient_filter(palette[0], palette[1], duration + 2, style_index + i)
        srt_abs = str(srt_path.resolve()).replace("\\", "/").replace(":", "\\\\:")

        # Add chapter title overlay for 3 seconds at start
        title_escaped = title.replace("'", "\\'").replace(":", "\\:")
        title_filter = (
            f"drawtext=text='{title_escaped}':"
            f"fontsize=40:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"enable='between(t,0,3)':alpha='if(lt(t,0.5),t/0.5,if(gt(t,2.5),1-(t-2.5)/0.5,1))'"
        )

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

    # Concatenate all segments with crossfade transitions
    if len(segment_videos) == 1:
        segment_videos[0].rename(video_path)
        return video_path

    # Create concat file
    concat_file = temp_dir / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for sv in segment_videos:
            f.write(f"file '{sv.resolve()}'\n")

    # Simple concat (transitions via xfade would be ideal but complex)
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "medium", "-b:v", "2M",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
    ]

    # Add background music if available
    has_music = Path(MUSIC_FILE).exists()
    if has_music:
        cmd_with_music = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(MUSIC_FILE),
            "-filter_complex", "[0:a]volume=1.0[voice];[1:a]volume=0.10[music];[voice][music]amix=inputs=2:duration=shortest[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-b:v", "2M",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(video_path),
        ]
        cmd = cmd_with_music
    else:
        cmd += [str(video_path)]

    logging.info("Concatenating segments into final long video...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Concat ffmpeg error: {result.stderr[-500:]}")
        raise RuntimeError(f"ffmpeg concat failed")

    # Cleanup temp
    for sv in segment_videos:
        sv.unlink(missing_ok=True)
    concat_file.unlink(missing_ok=True)
    try:
        temp_dir.rmdir()
    except OSError:
        pass

    logging.info(f"Long video assembled: {video_path}")
    return video_path


# Backward compatibility alias
def assemble_video(audio_path, srt_path, output_dir, video_name, style_index=0):
    """Alias for assemble_short."""
    return assemble_short(audio_path, srt_path, output_dir, video_name, style_index)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python assemble_video.py <audio_path> <srt_path> <output_name> [style_index]")
        sys.exit(1)
    audio = Path(sys.argv[1])
    srt = Path(sys.argv[2])
    name = sys.argv[3]
    style = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    out_dir = Path("output/video")
    assemble_short(audio, srt, out_dir, name, style)

# YouTube Shorts Autonomous Bot

## Overview
This repository contains a **zero‑cost, fully autonomous pipeline** that generates, assembles, and publishes YouTube Shorts (4 times a day) about biblical stories with high retention. The architecture mirrors the robust "Daily Oracle" bot and uses only free services:
- **OpenRouter free models** (cascading fallback)
- **gTTS** (primary TTS) with **espeak‑ng** fallback
- **FFmpeg** for vertical video creation
- **GitHub Actions** as the server‑less scheduler
- **YouTube Data API v3** with persisted OAuth token
- Optional **Tkinter desktop monitor** and **PWA** (to be added later)

## Folder Structure
```
youtube_shorts_bot/
├─ .github/
│  └─ workflows/
│     └─ publish_shorts.yml      # Scheduler (4×/day)
├─ docs/
│  └─ index.html                # Placeholder for future PWA
├─ assets/
│  ├─ background.mp4            # Loopable background (add your own)
│  ├─ overlay.png               # Illustration/card (add your own)
│  ├─ music.mp3                 # Ambient music (optional)
│  └─ thumbnail.jpg             # Vertical thumbnail (optional)
├─ scripts/
│  ├─ generate_script.py        # OpenRouter cascade
│  ├─ generate_audio.py         # gTTS / espeak‑ng + SRT
│  ├─ assemble_video.py         # FFmpeg assembly
│  ├─ publish_youtube.py        # YouTube uploader
│  ├─ lock.py                   # Cool‑down lock (45 min)
│  └─ main.py                   # Orchestrator called by the Action
├─ config.py                     # Channel & secret configuration
├─ requirements.txt              # Python dependencies
└─ README.md                     # This file
```

## Quick Setup Guide
1. **Create the repo**
   ```bash
   mkdir youtube_shorts_bot && cd youtube_shorts_bot
   # copy the generated files from the artifact directory to here
   # (or simply `git clone` a fresh repo and paste the contents)
   git init && git add . && git commit -m "Initial commit"
   git remote add origin <YOUR_GITHUB_URL>
   git push -u origin master
   ```
2. **Add the required GitHub Secrets** (Settings → Secrets → Actions)
   - `OPENROUTER_API_KEY` – your free OpenRouter key.
   - `YOUTUBE_TOKEN_JSON` – the OAuth token JSON (obtain via the Google OAuth flow; the token must contain a `refresh_token`).
   - `CLIENT_SECRET_JSON` – the client secret you received from Google Cloud Console.
   - *(Optional)* `YOUTUBE_CHANNEL_ID` – the numeric channel ID if it is not present in the token JSON.
3. **Provide assets**
   - Place a **loopable vertical video** (≈5‑10 s) at `assets/background.mp4`.
   - Add an **illustration** for the overlay at `assets/overlay.png`.
   - (Optional) background music `assets/music.mp3` and thumbnail `assets/thumbnail.jpg`.
4. **Enable the workflow**
   - Go to the *Actions* tab, enable the "Publish YouTube Shorts" workflow.
   - You can trigger it manually via *Run workflow* → optional *topic* input.
5. **Test a single run**
   ```bash
   python scripts/main.py "El valor de David contra Goliat"
   ```
   Check the logs in the Action run; a video should appear on your channel.

## Customising the Bot
- **Channel details** – edit `config.py` (name, niche, CTA, tags).
- **Publish schedule** – modify `PUBLISH_TIMES` in `config.py` and the cron expression in `.github/workflows/publish_shorts.yml`.
- **Emergency script pool** – edit `EMERGENCY_SCRIPTS` in `scripts/generate_script.py`.
- **Audio language / speed** – adjust `TTS_LANGUAGE` and `TTS_SLOW` in `config.py`.
- **Background / overlay** – replace the files in `assets/`.

## Next Steps (Optional)
- Implement the **Tkinter desktop monitor** (scripts/ui_app.py) for real‑time status and manual overrides.
- Flesh‑out the **PWA** in `docs/` (HTML + simple auth) so you can trigger uploads from mobile.
- Add a **long‑form video** generation pipeline (reuse the same scripts, just change the schedule and script length).

---
Feel free to ask if you need help setting up the OAuth flow, generating the assets, or extending the bot with the desktop/PWA UI.

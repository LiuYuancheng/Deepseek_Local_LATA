#!/usr/bin/env python3
"""
Video Subtitle Generator using Whisper + Local Ollama LLM
---------------------------------------------------------
Usage:
    python subtitle_generator.py <video_file> [options]

Requirements:
    pip install openai-whisper ffmpeg-python requests tqdm
    Also requires: ffmpeg installed on your system
    Also requires: Ollama running locally (https://ollama.com)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

import requests
from tqdm import tqdm

# ── Configuration ─────────────────────────────────────────────────────────────

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3"       # Change to any model you have pulled
DEFAULT_WHISPER_MODEL = "base"        # tiny | base | small | medium | large
DEFAULT_LANGUAGE = None               # None = auto-detect, or e.g. "en", "zh"
OLLAMA_TIMEOUT = 120                  # seconds per LLM request

# ── Helpers ───────────────────────────────────────────────────────────────────

def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp HH:MM:SS,mmm"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((td.total_seconds() - total_seconds) * 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def check_ffmpeg():
    """Ensure ffmpeg is available."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌  ffmpeg not found. Install it first: https://ffmpeg.org/download.html")
        sys.exit(1)


def check_ollama(model: str):
    """Ensure Ollama is running and the model is available."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"].split(":")[0] for m in resp.json().get("models", [])]
        if model not in models and model.split(":")[0] not in models:
            print(f"⚠️  Model '{model}' not found in Ollama.")
            print(f"   Available models: {', '.join(models) if models else 'none'}")
            print(f"   Run: ollama pull {model}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"❌  Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print("   Make sure Ollama is running: ollama serve")
        sys.exit(1)

# ── Step 1: Extract audio ──────────────────────────────────────────────────────

def extract_audio(video_path: str, audio_path: str):
    """Extract mono 16kHz WAV audio from video for Whisper."""
    print(f"\n🎬  Extracting audio from '{Path(video_path).name}' ...")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn",                   # no video
        "-acodec", "pcm_s16le",  # PCM WAV
        "-ar", "16000",          # 16 kHz sample rate
        "-ac", "1",              # mono
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌  ffmpeg error:\n", result.stderr)
        sys.exit(1)
    print("✅  Audio extracted.")

# ── Step 2: Transcribe with Whisper ───────────────────────────────────────────

def transcribe_audio(audio_path: str, whisper_model: str, language: str | None) -> list[dict]:
    """
    Run Whisper transcription and return a list of segments:
    [{"start": float, "end": float, "text": str}, ...]
    """
    print(f"\n🔊  Transcribing with Whisper model='{whisper_model}' ...")
    try:
        import whisper
    except ImportError:
        print("❌  openai-whisper not installed. Run: pip install openai-whisper")
        sys.exit(1)

    model = whisper.load_model(whisper_model)
    options = {"verbose": False}
    if language:
        options["language"] = language

    result = model.transcribe(audio_path, **options)
    segments = [
        {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
        for s in result["segments"]
    ]
    print(f"✅  Transcription complete: {len(segments)} segments.")
    return segments

# ── Step 3: Refine with Ollama LLM ────────────────────────────────────────────

def refine_segment_with_ollama(text: str, model: str, context: str = "") -> str:
    """
    Send a subtitle segment to Ollama for grammar/punctuation refinement.
    Returns the cleaned text.
    """
    prompt = (
        "You are a professional subtitle editor. "
        "Fix grammar, punctuation, and capitalization of the following subtitle text. "
        "Keep the meaning identical. Do NOT translate. Do NOT add explanations. "
        "Return ONLY the corrected subtitle text, nothing else.\n\n"
        f"Subtitle: {text}"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 200}
    }

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )
        resp.raise_for_status()
        refined = resp.json().get("response", text).strip()
        # Guard: if LLM returns something much longer, fallback to original
        if len(refined) > len(text) * 3:
            return text
        return refined
    except Exception as e:
        # On any error, return the original whisper text unchanged
        return text


def refine_all_segments(segments: list[dict], model: str, skip_llm: bool) -> list[dict]:
    """Optionally refine every segment through the Ollama LLM."""
    if skip_llm:
        print("\n⏩  Skipping LLM refinement (--skip-llm flag).")
        return segments

    print(f"\n🤖  Refining subtitles with Ollama model='{model}' ...")
    refined = []
    for seg in tqdm(segments, desc="LLM refine", unit="seg"):
        new_text = refine_segment_with_ollama(seg["text"], model)
        refined.append({**seg, "text": new_text})
    print("✅  LLM refinement complete.")
    return refined

# ── Step 4: Write SRT ─────────────────────────────────────────────────────────

def write_srt(segments: list[dict], output_path: str):
    """Write segments to an SRT subtitle file."""
    lines = []
    for i, seg in enumerate(segments, start=1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"]
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n💾  Subtitle saved to: {output_path}")

# ── Optional Step 5: Burn subtitles into video ────────────────────────────────

def burn_subtitles(video_path: str, srt_path: str, output_video: str):
    """Use ffmpeg to hard-code (burn) subtitles into a new video file."""
    print(f"\n🔥  Burning subtitles into video ...")
    # Escape Windows-style paths for ffmpeg filter
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"subtitles='{srt_escaped}'",
        "-c:a", "copy",
        output_video
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠️  Could not burn subtitles:\n", result.stderr[-500:])
    else:
        print(f"✅  Video with subtitles saved to: {output_video}")

# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate subtitles for a video using Whisper + Ollama LLM"
    )
    parser.add_argument("video", help="Path to the input video file")
    parser.add_argument(
        "--ollama-model", default=DEFAULT_OLLAMA_MODEL,
        help=f"Ollama model name (default: {DEFAULT_OLLAMA_MODEL})"
    )
    parser.add_argument(
        "--whisper-model", default=DEFAULT_WHISPER_MODEL,
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help=f"Whisper model size (default: {DEFAULT_WHISPER_MODEL})"
    )
    parser.add_argument(
        "--language", default=DEFAULT_LANGUAGE,
        help="Force language code e.g. 'en', 'zh', 'ja'. Default: auto-detect"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output .srt file path. Default: same as video with .srt extension"
    )
    parser.add_argument(
        "--burn", action="store_true",
        help="Also burn subtitles into a new video file"
    )
    parser.add_argument(
        "--skip-llm", action="store_true",
        help="Skip LLM refinement step (faster, raw Whisper output)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    video_path = Path(args.video).resolve()
    if not video_path.exists():
        print(f"❌  Video file not found: {video_path}")
        sys.exit(1)

    output_srt = Path(args.output) if args.output else video_path.with_suffix(".srt")

    # Pre-flight checks
    check_ffmpeg()
    if not args.skip_llm:
        check_ollama(args.ollama_model)

    print(f"""
╔══════════════════════════════════════════╗
║      Video Subtitle Generator            ║
╠══════════════════════════════════════════╣
║  Video        : {video_path.name:<25}║
║  Whisper model: {args.whisper_model:<25}║
║  Ollama model : {args.ollama_model:<25}║
║  Language     : {str(args.language or 'auto-detect'):<25}║
║  Output SRT   : {output_srt.name:<25}║
╚══════════════════════════════════════════╝
""")

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        # 1. Extract audio
        extract_audio(str(video_path), audio_path)

        # 2. Transcribe
        segments = transcribe_audio(audio_path, args.whisper_model, args.language)

        if not segments:
            print("⚠️  No speech detected in the video.")
            sys.exit(0)

        # 3. Refine with LLM
        segments = refine_all_segments(segments, args.ollama_model, args.skip_llm)

        # 4. Write SRT
        write_srt(segments, str(output_srt))

        # 5. Optionally burn subtitles
        if args.burn:
            burned_output = video_path.with_name(video_path.stem + "_subtitled" + video_path.suffix)
            burn_subtitles(str(video_path), str(output_srt), str(burned_output))

    print("\n🎉  Done!\n")


if __name__ == "__main__":
    main()

# Video Subtitle Generator — Setup Guide

## Requirements

### System Dependencies
- **Python 3.10+**
- **ffmpeg** — for audio extraction and subtitle burning
  - macOS:   `brew install ffmpeg`
  - Ubuntu:  `sudo apt install ffmpeg`
  - Windows: https://ffmpeg.org/download.html (add to PATH)
- **Ollama** — local LLM runner
  - Install from https://ollama.com
  - Start the server: `ollama serve`
  - Pull a model: `ollama pull llama3`

### Python Packages
```bash
pip install openai-whisper ffmpeg-python requests tqdm
```
> Whisper also requires PyTorch. If not already installed:
> ```bash
> pip install torch torchvision torchaudio
> ```

---

## Usage

### Basic (auto-detect language, use default models)
```bash
python subtitle_generator.py my_video.mp4
```
Produces `my_video.srt` in the same folder.

### Specify Ollama model and Whisper model
```bash
python subtitle_generator.py my_video.mp4 \
  --ollama-model mistral \
  --whisper-model small
```

### Force a language (faster transcription)
```bash
python subtitle_generator.py my_video.mp4 --language en
python subtitle_generator.py my_video.mp4 --language zh
```

### Custom output path
```bash
python subtitle_generator.py my_video.mp4 --output subtitles/my_subs.srt
```

### Also burn subtitles into a new video
```bash
python subtitle_generator.py my_video.mp4 --burn
```
Creates `my_video_subtitled.mp4` with embedded subtitles.

### Skip LLM step (raw Whisper output, much faster)
```bash
python subtitle_generator.py my_video.mp4 --skip-llm
```

---

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `video` | *(required)* | Path to input video file |
| `--ollama-model` | `llama3` | Ollama model to use for refinement |
| `--whisper-model` | `base` | Whisper model size: tiny/base/small/medium/large |
| `--language` | auto | Language code e.g. `en`, `zh`, `ja`, `fr` |
| `--output` | `<video>.srt` | Custom output .srt file path |
| `--burn` | off | Burn subtitles into a new video file |
| `--skip-llm` | off | Skip Ollama LLM refinement step |

---

## Whisper Model Size Guide

| Model | VRAM | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | ~1 GB | Fastest | Basic |
| `base` | ~1 GB | Fast | Good |
| `small` | ~2 GB | Moderate | Better |
| `medium` | ~5 GB | Slow | Great |
| `large` | ~10 GB | Slowest | Best |

## Recommended Ollama Models

```bash
ollama pull llama3        # General purpose, good quality
ollama pull mistral       # Fast and lightweight
ollama pull gemma3        # Google's model, multilingual
ollama pull qwen2.5       # Excellent for Chinese/English
```

---

## Pipeline Overview

```
Video file
   │
   ▼ ffmpeg
Audio (.wav, 16kHz mono)
   │
   ▼ Whisper (openai-whisper)
Raw transcript segments [{start, end, text}, ...]
   │
   ▼ Ollama LLM (local)
Refined segments (grammar/punctuation fixed)
   │
   ▼
Output: subtitles.srt
   │ (optional --burn)
   ▼ ffmpeg
Video with burned-in subtitles
```

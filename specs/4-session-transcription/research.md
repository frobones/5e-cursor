# Research: Session Transcription

## OpenAI Whisper (Local)

### Installation

```bash
pip install openai-whisper
```

**Note**: This is the open-source local version, NOT the API. No API key required.

### System Dependencies

Whisper requires `ffmpeg` for audio processing:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (with chocolatey)
choco install ffmpeg
```

### Model Download

Models are downloaded on first use to `~/.cache/whisper/`:

| Model | Size | Download Time (50 Mbps) |
|-------|------|------------------------|
| tiny | 39 MB | ~6 seconds |
| base | 74 MB | ~12 seconds |
| small | 244 MB | ~40 seconds |
| medium | 769 MB | ~2 minutes |
| large | 1.5 GB | ~4 minutes |

### Basic Usage

```python
import whisper

# Load model
model = whisper.load_model("base")

# Transcribe audio
result = model.transcribe("audio.mp3")

# Access transcript
print(result["text"])
```

### Result Structure

```python
result = {
    "text": "Full transcript as a single string...",
    "segments": [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 4.0,
            "text": " First segment...",
            "tokens": [50364, 1374, ...],
            "temperature": 0.0,
            "avg_logprob": -0.25,
            "compression_ratio": 1.5,
            "no_speech_prob": 0.01
        },
        # ... more segments
    ],
    "language": "en"
}
```

### Device Selection

```python
import whisper
import torch

# Automatic device selection
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

# Load model on specific device
model = whisper.load_model("base", device=device)
```

### Performance Benchmarks

Approximate transcription times for 1-hour audio:

| Model | GPU (CUDA/MPS) | CPU |
|-------|----------------|-----|
| tiny | ~2 min | ~15 min |
| base | ~3 min | ~25 min |
| small | ~5 min | ~45 min |
| medium | ~10 min | ~90 min |
| large | ~15 min | ~180 min |

**Note**: Apple Silicon (MPS) is typically 2-3x slower than CUDA but much faster than CPU.

### Audio Format Support

Whisper uses ffmpeg for audio decoding. Supported formats include:
- MP3
- WAV
- M4A
- FLAC
- OGG
- WEBM
- Any format ffmpeg can decode

### Long Audio Handling

Whisper processes audio in 30-second chunks internally. Long files are handled automatically, but:
- Memory usage increases with file length
- No built-in progress indication
- Interrupted transcription loses all progress

### Language Detection

Whisper auto-detects language by default. Can be forced:

```python
result = model.transcribe("audio.mp3", language="en")
```

Supported languages: 99+ including English, Spanish, French, German, Chinese, Japanese, etc.

## PyTorch Hardware Detection

### CUDA (NVIDIA GPU)

```python
import torch

# Check if CUDA is available
torch.cuda.is_available()  # True/False

# Get device count
torch.cuda.device_count()

# Get device name
torch.cuda.get_device_name(0)  # e.g., "NVIDIA GeForce RTX 3080"
```

### MPS (Apple Silicon)

```python
import torch

# Check if MPS is available
torch.backends.mps.is_available()  # True/False

# Check if MPS is built into PyTorch
torch.backends.mps.is_built()  # True/False
```

**Note**: MPS requires macOS 12.3+ and PyTorch 1.12+.

## Error Handling

### Common Errors

1. **ffmpeg not found**
   ```
   RuntimeError: ffmpeg was not found but is required to load audio files
   ```
   Solution: Install ffmpeg

2. **CUDA out of memory**
   ```
   RuntimeError: CUDA out of memory
   ```
   Solution: Use smaller model or CPU

3. **Invalid audio file**
   ```
   RuntimeError: Error opening 'file.mp3': No such file or directory
   ```
   Solution: Check file path and format

4. **MPS not available**
   ```
   RuntimeError: MPS backend is not available
   ```
   Solution: Update macOS and PyTorch, or fall back to CPU

## Integration with Session Manager

### Existing Patterns

From `session_manager.py`:

```python
def get_next_session_number(sessions_dir: Path) -> int:
    """Find the next available session number."""
    # ... existing implementation

def update_session_index(campaign_dir: Path, session_number: int, title: str, filename: str) -> None:
    """Update the session index with a new session."""
    # ... existing implementation
```

### Reusable Utilities

From `markdown_writer.py`:

```python
from lib.markdown_writer import (
    bold,
    heading,
    horizontal_rule,
    iso_date,
    session_filename,
)
```

## Design Decisions

### Local vs API

**Decision**: Local Whisper only (no API option)

**Rationale**:
- No ongoing costs for users
- No API key management
- Works offline
- Privacy - audio never leaves user's machine
- Consistent with project's "AI-first but local data" philosophy

### Default Model Selection

**Decision**: Large for GPU, Small for CPU

**Rationale**:
- Large provides best accuracy for understanding D&D sessions (character names, spell names, etc.)
- GPU makes large model practical (~15 min for 1-hour session)
- Small is reasonable trade-off for CPU users (~45 min for 1-hour)
- Users can always override with `--model`

### Transcript Storage

**Decision**: Store raw transcript separately from session file

**Rationale**:
- Session files can be edited without losing original transcript
- Raw transcripts are smaller/simpler for programmatic access
- Allows future features like transcript search, comparison

## Open Items

None - all design decisions resolved.

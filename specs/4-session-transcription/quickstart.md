# Quickstart: Session Transcription

This guide walks you through transcribing a D&D session audio recording and generating session notes.

## Prerequisites

### 1. Install ffmpeg

Whisper requires ffmpeg for audio processing.

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows (with Chocolatey):**
```bash
choco install ffmpeg
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs `openai-whisper` and its dependencies (including PyTorch).

### 3. Initialize Campaign (if not already done)

```bash
python scripts/campaign/init_campaign.py "Your Campaign Name"
```

## Basic Usage

### Transcribe an Audio Recording

```bash
python scripts/campaign/transcribe_session.py "path/to/recording.mp3" --title "Into the Dragon's Lair"
```

This will:
1. Detect your hardware (GPU or CPU)
2. Load the appropriate Whisper model
3. Transcribe the audio
4. Save the transcript to `campaign/sessions/transcripts/session-NNN.txt`
5. Create a session file at `campaign/sessions/session-NNN.md`
6. Update the session index

### Example Output

```
Apple Silicon detected. Using 'large' model for best accuracy.
Loading Whisper model 'large'...
Transcribing: recording.mp3
Progress: Transcription complete (duration: 3:24:15)

Created session 5: Into the Dragon's Lair
  Session file: campaign/sessions/session-005.md
  Transcript: campaign/sessions/transcripts/session-005.txt
```

## Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--title` | Session title | `--title "The Goblin Caves"` |
| `--model` | Override model selection | `--model medium` |
| `--number` | Specify session number | `--number 5` |

### Override Model Selection

```bash
# Use medium model instead of auto-detected default
python scripts/campaign/transcribe_session.py recording.mp3 --model medium

# Use small model for faster (but less accurate) transcription
python scripts/campaign/transcribe_session.py recording.mp3 --model small
```

### Specify Session Number

```bash
# Create as session 10 instead of auto-incrementing
python scripts/campaign/transcribe_session.py recording.mp3 --title "Boss Fight" --number 10
```

## Analyzing the Transcript

After transcription, open the session file in Cursor and run the analyze command:

```
/analyze-session
```

The command will automatically:
1. Read the transcript section
2. Check your campaign's existing NPCs and locations
3. Fill in all structured sections (Summary, Key Events, NPCs, Locations, Loot, Notes)
4. Link to existing entities or mark new ones with (NEW)

### Manual Prompts (Alternative)

You can also ask the AI specific questions:

- "Summarize this session in 2-3 paragraphs"
- "What NPCs did the party interact with?"
- "What locations did they visit?"
- "What loot or rewards did they receive?"
- "What plot hooks or cliffhangers should I remember for next session?"

## Troubleshooting

### "ffmpeg not found"

Install ffmpeg using the commands in Prerequisites.

### "Campaign directory not found"

Run `python scripts/campaign/init_campaign.py "Campaign Name"` first.

### Slow transcription

- On CPU, transcription takes ~45 minutes per hour of audio with `small` model
- Use `--model tiny` for faster (but less accurate) results
- If you have a GPU, ensure CUDA or MPS is properly configured

### Model download taking a long time

Whisper models are downloaded on first use:
- `small`: ~244 MB
- `large`: ~1.5 GB

This only happens once per model.

### Out of memory errors

Use a smaller model:
```bash
python scripts/campaign/transcribe_session.py recording.mp3 --model small
```

## Workflow Summary

1. **Record your session** (phone, OBS, Discord, etc.)
2. **Transfer audio file** to your computer
3. **Run transcription**: `python scripts/campaign/transcribe_session.py recording.mp3 --title "Session Title"`
4. **Open session file** in Cursor
5. **Run `/analyze-session`** to auto-fill all sections
6. **Review and edit** the generated notes
7. **Create new entities** for any marked (NEW)
8. **Commit changes** to preserve session history

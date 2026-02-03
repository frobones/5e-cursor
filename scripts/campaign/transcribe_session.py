#!/usr/bin/env python3
"""
Session Transcription - Transcribe audio recordings to session notes.

Transcribes D&D session audio recordings using local Whisper, creating
session files with embedded transcripts that Cursor AI can analyze.

Usage:
    python scripts/campaign/transcribe_session.py "recording.mp3" --title "The Dragon's Lair"
    python scripts/campaign/transcribe_session.py recording.mp3 --model medium
    python scripts/campaign/transcribe_session.py recording.mp3 --title "Session 5" --number 5

Requirements:
    - ffmpeg: Install with `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)
    - openai-whisper: Installed via requirements.txt

Models (downloaded on first use):
    - tiny (39 MB): Quick test, basic quality
    - base (74 MB): Fast, good quality
    - small (244 MB): Default for CPU, better quality
    - medium (769 MB): Slow, great quality
    - large (1.5 GB): Default for GPU, highest quality
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.markdown_writer import bold, heading, horizontal_rule, iso_date, session_filename

# Valid Whisper model names
VALID_MODELS = ["tiny", "base", "small", "medium", "large"]


def detect_device() -> str:
    """Detect best available device for Whisper.

    Returns:
        Device string: "cuda", "mps", or "cpu"
    """
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    except ImportError:
        return "cpu"


def get_default_model(device: str) -> str:
    """Determine best default model based on hardware.

    Args:
        device: Device type from detect_device()

    Returns:
        Model name: "large" for GPU, "small" for CPU
    """
    if device == "cuda":
        return "large"
    elif device == "mps":
        return "large"
    else:
        return "small"


def print_device_status(device: str, model: str) -> None:
    """Print hardware detection status for user feedback.

    Args:
        device: Detected device type
        model: Selected model name
    """
    if device == "cuda":
        print(f"NVIDIA GPU detected. Using '{model}' model for best accuracy.")
    elif device == "mps":
        print(f"Apple Silicon detected. Using '{model}' model for best accuracy.")
    else:
        print(f"No GPU detected. Using '{model}' model for reasonable speed.")
        if model == "small":
            print("Tip: Use --model medium for better quality (slower).")


def validate_audio_path(audio_path: Path) -> None:
    """Validate that the audio file exists and is readable.

    Args:
        audio_path: Path to audio file

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file isn't readable
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if not audio_path.is_file():
        raise ValueError(f"Path is not a file: {audio_path}")

    # Check if readable
    try:
        with open(audio_path, "rb") as f:
            f.read(1)
    except PermissionError:
        raise PermissionError(f"Cannot read audio file: {audio_path}")


def transcribe_audio(audio_path: Path, model_name: str, device: str) -> str:
    """Transcribe audio file using Whisper.

    Args:
        audio_path: Path to audio file
        model_name: Whisper model name (tiny, base, small, medium, large)
        device: Device to use (cuda, mps, cpu)

    Returns:
        Transcript text

    Raises:
        RuntimeError: If ffmpeg is not installed or transcription fails
    """
    try:
        import whisper
    except ImportError:
        raise ImportError(
            "Whisper not installed. Run: pip install openai-whisper"
        )

    print(f"Loading Whisper model '{model_name}'...")

    try:
        model = whisper.load_model(model_name, device=device)
    except Exception as e:
        if "ffmpeg" in str(e).lower():
            raise RuntimeError(
                "ffmpeg not found. Install with:\n"
                "  macOS: brew install ffmpeg\n"
                "  Linux: sudo apt install ffmpeg\n"
                "  Windows: choco install ffmpeg"
            )
        raise

    print(f"Transcribing: {audio_path.name}")
    print("This may take a while for long recordings...")

    try:
        result = model.transcribe(str(audio_path))
    except Exception as e:
        if "ffmpeg" in str(e).lower() or "No such file" in str(e):
            raise RuntimeError(
                f"Could not process audio file. Ensure ffmpeg is installed.\n"
                f"Error: {e}"
            )
        raise

    transcript = result.get("text", "")
    language = result.get("language", "unknown")

    print(f"Transcription complete. Detected language: {language}")

    return transcript.strip()


def get_next_session_number(sessions_dir: Path) -> int:
    """Find the next available session number.

    Args:
        sessions_dir: Path to sessions directory

    Returns:
        Next session number
    """
    if not sessions_dir.exists():
        return 1

    max_num = 0
    for session_file in sessions_dir.glob("session-*.md"):
        match = re.search(r"session-(\d+)\.md", session_file.name)
        if match:
            num = int(match.group(1))
            max_num = max(max_num, num)

    return max_num + 1


def save_transcript(transcript: str, session_number: int, sessions_dir: Path) -> Path:
    """Save raw transcript to file.

    Args:
        transcript: Transcript text
        session_number: Session number
        sessions_dir: Path to sessions directory

    Returns:
        Path to saved transcript file
    """
    transcripts_dir = sessions_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    filename = f"session-{session_number:03d}.txt"
    transcript_path = transcripts_dir / filename

    transcript_path.write_text(transcript, encoding="utf-8")

    return transcript_path


def create_session_with_transcript(
    sessions_dir: Path,
    title: str,
    session_number: int,
    transcript: str,
    audio_source: str,
    model: str,
) -> Path:
    """Create a session file with embedded transcript.

    Args:
        sessions_dir: Path to sessions directory
        title: Session title
        session_number: Session number
        transcript: Transcript text
        audio_source: Original audio filename
        model: Whisper model used

    Returns:
        Path to created session file
    """
    sessions_dir.mkdir(parents=True, exist_ok=True)

    filename = session_filename(session_number)
    session_path = sessions_dir / filename

    today = iso_date()

    content = f"""{heading(f"Session {session_number}: {title}")}

{bold("Date")}: {today}  
{bold("Session Number")}: {session_number}  
{bold("Audio Source")}: {audio_source}  
{bold("Transcription Model")}: {model}

{horizontal_rule()}

## Summary

*Ask Cursor AI to summarize the transcript below*

## Key Events

*Ask Cursor AI to extract key events from the transcript*

## NPCs Encountered

*Ask Cursor AI to identify NPCs mentioned*

## Locations Visited

*Ask Cursor AI to identify locations visited*

## Loot & Rewards

*Ask Cursor AI to identify any loot or rewards*

## Notes for Next Session

*Ask Cursor AI to identify hooks and cliffhangers*

{horizontal_rule()}

## Transcript

> Full transcript below. Ask AI: "Analyze this session transcript and fill in the sections above"

{transcript}

{horizontal_rule()}

*Session created from audio transcription on {today}*  
*Transcript: campaign/sessions/transcripts/session-{session_number:03d}.txt*
"""

    session_path.write_text(content, encoding="utf-8")
    return session_path


def update_session_index(
    campaign_dir: Path, session_number: int, title: str, filename: str
) -> None:
    """Update the session index with a new session.

    Args:
        campaign_dir: Campaign directory
        session_number: Session number
        title: Session title
        filename: Session filename
    """
    index_path = campaign_dir / "sessions" / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    today = iso_date()

    lines = content.split("\n")
    new_lines = []

    for line in lines:
        new_lines.append(line)
        if line.startswith("| ----"):
            new_row = f"| {session_number} | {today} | [{title}]({filename}) |"
            new_lines.append(new_row)

    # Remove placeholder if present
    final_lines = [l for l in new_lines if "*No sessions recorded yet" not in l]

    index_path.write_text("\n".join(final_lines), encoding="utf-8")


def find_repo_root() -> Path:
    """Find the repository root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "books").exists() or (current / "scripts").exists():
            return current
        current = current.parent
    return Path.cwd()


def main():
    """Main entry point for session transcription."""
    parser = argparse.ArgumentParser(
        description="Transcribe audio recordings to session notes using Whisper.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage (auto-detects hardware and model)
    python scripts/campaign/transcribe_session.py "recording.mp3" --title "The Dragon's Lair"

    # Use specific model
    python scripts/campaign/transcribe_session.py recording.mp3 --model medium

    # Specify session number
    python scripts/campaign/transcribe_session.py recording.mp3 --title "Boss Fight" --number 5

Models:
    tiny   - 39 MB, fastest, basic quality
    base   - 74 MB, fast, good quality
    small  - 244 MB, medium speed, better quality (CPU default)
    medium - 769 MB, slow, great quality
    large  - 1.5 GB, slowest, highest quality (GPU default)
        """,
    )

    parser.add_argument(
        "audio_path",
        type=Path,
        help="Path to audio file (mp3, wav, m4a, etc.)",
    )
    parser.add_argument(
        "--title", "-t",
        default="Untitled Session",
        help="Session title (default: 'Untitled Session')",
    )
    parser.add_argument(
        "--model", "-m",
        choices=VALID_MODELS,
        default=None,
        help="Whisper model to use (default: auto-detected based on hardware)",
    )
    parser.add_argument(
        "--number", "-n",
        type=int,
        default=None,
        help="Session number (default: auto-increment)",
    )

    args = parser.parse_args()

    # Find repo root and campaign directory
    repo_root = find_repo_root()
    campaign_dir = repo_root / "campaign"
    sessions_dir = campaign_dir / "sessions"

    if not campaign_dir.exists():
        print("Error: Campaign directory not found.")
        print("Run: python scripts/campaign/init_campaign.py \"Campaign Name\"")
        sys.exit(1)

    # Resolve audio path
    audio_path = args.audio_path
    if not audio_path.is_absolute():
        audio_path = Path.cwd() / audio_path

    # Validate audio file
    try:
        validate_audio_path(audio_path)
    except (FileNotFoundError, ValueError, PermissionError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Detect hardware and select model
    device = detect_device()
    model = args.model if args.model else get_default_model(device)

    print_device_status(device, model)
    print()

    # Transcribe
    try:
        transcript = transcribe_audio(audio_path, model, device)
    except (ImportError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not transcript:
        print("Warning: Transcription produced empty result.")
        sys.exit(1)

    print()

    # Get session number
    session_number = args.number if args.number else get_next_session_number(sessions_dir)

    # Save transcript
    transcript_path = save_transcript(transcript, session_number, sessions_dir)
    print(f"Saved transcript: {transcript_path}")

    # Create session file
    session_path = create_session_with_transcript(
        sessions_dir=sessions_dir,
        title=args.title,
        session_number=session_number,
        transcript=transcript,
        audio_source=audio_path.name,
        model=model,
    )
    print(f"Created session: {session_path}")

    # Update index
    update_session_index(campaign_dir, session_number, args.title, session_path.name)

    print()
    print(f"Session {session_number}: {args.title}")
    print(f"  Session file: {session_path}")
    print(f"  Transcript: {transcript_path}")
    print()
    print("Next steps:")
    print(f"  1. Open {session_path.name} in Cursor")
    print("  2. Run /analyze-session to auto-fill session sections")


if __name__ == "__main__":
    main()

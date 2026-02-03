"""
File Watcher Service - Monitor campaign directory for changes.

Uses watchdog to detect file system events and notify connected clients.
"""

import asyncio
import logging
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


@dataclass
class FileChangeEvent:
    """Represents a file change event."""

    event_type: str  # "created", "modified", "deleted"
    entity_type: str  # "npcs", "locations", "sessions", etc.
    slug: str  # File slug (filename without .md)
    path: str  # Full path to the file


def path_to_entity_type(path: Path) -> Optional[str]:
    """Map a file path to its entity type.

    Args:
        path: Path to the file

    Returns:
        Entity type string or None if not a recognized entity
    """
    parts = path.parts

    # Look for campaign directory structure
    if "campaign" not in parts:
        return None

    try:
        campaign_idx = parts.index("campaign")
        if campaign_idx + 1 < len(parts):
            subdir = parts[campaign_idx + 1]

            # Map subdirectories to entity types
            entity_map = {
                "npcs": "npcs",
                "locations": "locations",
                "sessions": "sessions",
                "encounters": "encounters",
                "party": "party",
            }

            if subdir in entity_map:
                return entity_map[subdir]

            # Special case for characters subdirectory
            if subdir == "party" and len(parts) > campaign_idx + 2:
                if parts[campaign_idx + 2] == "characters":
                    return "characters"

    except (ValueError, IndexError):
        pass

    # Check for root campaign files
    if path.name in ("campaign.md", "timeline.md", "relationships.md", "events.md"):
        return "campaign"

    return None


def path_to_slug(path: Path) -> str:
    """Extract slug from file path.

    Args:
        path: Path to the file

    Returns:
        Slug (filename without extension)
    """
    return path.stem


class CampaignEventHandler(FileSystemEventHandler):
    """Handle file system events for campaign directory."""

    def __init__(
        self,
        callback: Callable[[FileChangeEvent], None],
        debounce_ms: int = 100,
    ) -> None:
        """Initialize the event handler.

        Args:
            callback: Function to call with file change events
            debounce_ms: Debounce time in milliseconds
        """
        super().__init__()
        self.callback = callback
        self.debounce_ms = debounce_ms
        self._last_events: dict[str, float] = {}
        self._lock = threading.Lock()

    def _should_process(self, path: str) -> bool:
        """Check if event should be processed (debounce).

        Args:
            path: File path

        Returns:
            True if event should be processed
        """
        now = time.time()
        with self._lock:
            last_time = self._last_events.get(path, 0)
            if now - last_time < self.debounce_ms / 1000:
                return False
            self._last_events[path] = now
            return True

    def _handle_event(self, event: FileSystemEvent, event_type: str) -> None:
        """Handle a file system event.

        Args:
            event: The file system event
            event_type: Type of event (created, modified, deleted)
        """
        # Only handle markdown files
        path = Path(event.src_path)
        if path.suffix != ".md":
            return

        # Skip index files
        if path.name == "index.md":
            return

        # Debounce rapid events
        if not self._should_process(event.src_path):
            return

        # Determine entity type
        entity_type = path_to_entity_type(path)
        if entity_type is None:
            return

        # Create and dispatch event
        change_event = FileChangeEvent(
            event_type=event_type,
            entity_type=entity_type,
            slug=path_to_slug(path),
            path=str(path),
        )

        logger.debug(f"File change: {change_event}")
        self.callback(change_event)

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation."""
        if not event.is_directory:
            self._handle_event(event, "created")

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification."""
        if not event.is_directory:
            self._handle_event(event, "modified")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion."""
        if not event.is_directory:
            self._handle_event(event, "deleted")


class FileWatcherService:
    """Service for watching campaign directory changes."""

    def __init__(self, campaign_dir: Path) -> None:
        """Initialize the file watcher.

        Args:
            campaign_dir: Path to the campaign directory
        """
        self.campaign_dir = campaign_dir
        self._observer: Optional[Observer] = None
        self._callbacks: list[Callable[[FileChangeEvent], None]] = []
        self._running = False

    def add_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Add a callback for file change events.

        Args:
            callback: Function to call with file change events
        """
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[FileChangeEvent], None]) -> None:
        """Remove a callback.

        Args:
            callback: The callback to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _dispatch_event(self, event: FileChangeEvent) -> None:
        """Dispatch event to all callbacks.

        Args:
            event: The file change event
        """
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in file watcher callback: {e}")

    def start(self) -> None:
        """Start watching the campaign directory."""
        if self._running:
            return

        if not self.campaign_dir.exists():
            logger.warning(f"Campaign directory does not exist: {self.campaign_dir}")
            return

        self._observer = Observer()
        handler = CampaignEventHandler(self._dispatch_event)
        self._observer.schedule(handler, str(self.campaign_dir), recursive=True)
        self._observer.start()
        self._running = True
        logger.info(f"Started watching: {self.campaign_dir}")

    def stop(self) -> None:
        """Stop watching the campaign directory."""
        if self._observer and self._running:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._running = False
            logger.info("Stopped file watcher")

    @property
    def is_running(self) -> bool:
        """Check if the watcher is running."""
        return self._running

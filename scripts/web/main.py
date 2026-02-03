"""
Campaign Web UI - FastAPI Application.

A read-only web API for browsing D&D campaign data.

Usage:
    # Development
    uvicorn scripts.web.main:app --reload --port 8000

    # Or from scripts/web directory
    cd scripts/web && uvicorn main:app --reload --port 8000
"""

import logging
import logging.handlers
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scripts_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.api import campaign, combat, creatures, docs, entities, reference, search, visualizations, websocket
from web.api.websocket import broadcast_file_change
from web.services.file_watcher import FileWatcherService


def configure_logging(log_to_file: bool = True) -> None:
    """Configure logging for the web UI.

    Args:
        log_to_file: If True, log to file; if False, log to console.
    """
    log_format = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    log_level = logging.INFO

    if log_to_file:
        # Ensure logs directory exists
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "web-ui.log"

        # Rotating file handler: 5MB max, keep 3 backups
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
        )
        handler.setFormatter(logging.Formatter(log_format))

        # Configure root logger
        logging.basicConfig(level=log_level, handlers=[handler])
    else:
        logging.basicConfig(level=log_level, format=log_format)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchdog").setLevel(logging.WARNING)


# Configure logging (log to file by default)
configure_logging(log_to_file=True)
logger = logging.getLogger(__name__)

# Find repository root
REPO_ROOT = Path(__file__).parent.parent.parent
CAMPAIGN_DIR = REPO_ROOT / "campaign"

# Global file watcher instance
file_watcher: FileWatcherService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle - start/stop file watcher."""
    global file_watcher

    # Startup: Start file watcher
    if CAMPAIGN_DIR.exists():
        file_watcher = FileWatcherService(CAMPAIGN_DIR)
        file_watcher.add_callback(broadcast_file_change)
        file_watcher.start()
        logger.info("File watcher started")
    else:
        logger.warning(f"Campaign directory not found: {CAMPAIGN_DIR}")

    yield

    # Shutdown: Stop file watcher
    if file_watcher:
        file_watcher.stop()
        logger.info("File watcher stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Campaign Web UI",
        description="A read-only web API for browsing D&D campaign data",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(campaign.router, prefix="/api", tags=["campaign"])
    app.include_router(combat.router, prefix="/api", tags=["combat"])
    app.include_router(creatures.router, prefix="/api", tags=["creatures"])
    app.include_router(docs.router, prefix="/api", tags=["docs"])
    app.include_router(entities.router, prefix="/api", tags=["entities"])
    app.include_router(reference.router, prefix="/api", tags=["reference"])
    app.include_router(search.router, prefix="/api", tags=["search"])
    app.include_router(visualizations.router, prefix="/api", tags=["visualizations"])
    app.include_router(websocket.router, tags=["websocket"])

    @app.get("/api/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {
            "status": "ok",
            "file_watcher": file_watcher.is_running if file_watcher else False,
            "websocket_connections": websocket.manager.connection_count,
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

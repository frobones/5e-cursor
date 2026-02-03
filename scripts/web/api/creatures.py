"""
Creatures API endpoints.

Provides structured creature stats from 5etools JSON data for combat tracking.
"""

from fastapi import APIRouter, HTTPException

from web.services.creature_stats import CreatureStatsService, CreatureStats

router = APIRouter()


@router.get("/creatures/{slug}/stats", response_model=CreatureStats)
async def get_creature_stats(slug: str) -> CreatureStats:
    """Get full creature stats by slug.

    Args:
        slug: URL-safe creature name (e.g., "goblin", "ancient-red-dragon")

    Returns:
        Full creature stat block including AC, HP, abilities, actions, etc.
    """
    service = CreatureStatsService()
    stats = service.get_creature_stats(slug)

    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Creature not found: {slug}"
        )

    return stats


@router.get("/creatures/list")
async def list_creatures(limit: int = 100) -> list[dict]:
    """List available creatures.

    Args:
        limit: Maximum number of creatures to return

    Returns:
        List of creatures with name, slug, and CR
    """
    service = CreatureStatsService()
    return service.list_creatures(limit=limit)

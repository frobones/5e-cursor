"""
Entity service for NPCs, locations, sessions, party, and encounters.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from web.models.entities import (
    NPCListItem,
    NPCDetail,
    LocationListItem,
    LocationDetail,
    SessionListItem,
    SessionDetail,
    CharacterListItem,
    CharacterDetail,
    EncounterListItem,
    EncounterDetail,
    EncounterCreature,
    EncounterCreate,
    EncounterUpdate,
    PartyOverview,
    Connection,
)
from web.services.campaign import get_campaign_dir


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


class EntityService:
    """Service for entity CRUD operations."""

    def __init__(self) -> None:
        """Initialize the entity service."""
        self.campaign_dir = get_campaign_dir()

    # --- NPC Methods ---

    def list_npcs(self, role: Optional[str] = None) -> list[NPCListItem]:
        """List all NPCs, optionally filtered by role."""
        npcs_dir = self.campaign_dir / "npcs"
        if not npcs_dir.exists():
            return []

        npcs = []
        for npc_file in npcs_dir.glob("*.md"):
            if npc_file.name == "index.md":
                continue

            content = npc_file.read_text(encoding="utf-8")
            npc = self._parse_npc_list_item(npc_file.stem, content)

            if role is None or npc.role.lower() == role.lower():
                npcs.append(npc)

        return sorted(npcs, key=lambda x: x.name.lower())

    def get_npc(self, slug: str) -> Optional[NPCDetail]:
        """Get NPC details by slug."""
        npc_file = self.campaign_dir / "npcs" / f"{slug}.md"
        if not npc_file.exists():
            return None

        content = npc_file.read_text(encoding="utf-8")
        return self._parse_npc_detail(slug, content)

    def _parse_npc_list_item(self, slug: str, content: str) -> NPCListItem:
        """Parse NPC content into list item."""
        return NPCListItem(
            name=self._extract_title(content),
            slug=slug,
            role=(self._extract_metadata(content, "Role") or "unknown").lower(),
            occupation=self._extract_metadata(content, "Occupation", strip_links=True),
            location=self._extract_metadata(content, "Location", strip_links=True),
            first_seen=self._extract_metadata(content, "First Appearance"),
        )

    def _parse_npc_detail(self, slug: str, content: str) -> NPCDetail:
        """Parse NPC content into detail model."""
        connections = self._parse_connections(content)

        return NPCDetail(
            name=self._extract_title(content),
            slug=slug,
            role=(self._extract_metadata(content, "Role") or "unknown").lower(),
            content=content,
            occupation=self._extract_metadata(content, "Occupation", strip_links=True),
            location=self._extract_metadata(content, "Location", strip_links=True),
            first_seen=self._extract_metadata(content, "First Appearance"),
            connections=connections,
        )

    def _parse_connections(self, content: str) -> list[Connection]:
        """Parse connections section from NPC content."""
        connections = []

        # Find Connections section
        match = re.search(r"## Connections\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if not match:
            return connections

        section = match.group(1)
        for line in section.split("\n"):
            line = line.strip()
            if not line.startswith("- "):
                continue

            # Parse: - [Name](file.md) | type | description
            # or: - Name | type | description
            parts = line[2:].split("|")
            if len(parts) < 2:
                continue

            name_part = parts[0].strip()
            rel_type = parts[1].strip() if len(parts) > 1 else "unknown"
            description = parts[2].strip() if len(parts) > 2 else None

            # Extract name and slug from link
            link_match = re.match(r"\[(.+?)\]\((.+?)\.md\)", name_part)
            if link_match:
                target_name = link_match.group(1)
                target_slug = link_match.group(2)
            else:
                target_name = name_part
                target_slug = None

            connections.append(
                Connection(
                    target_name=target_name,
                    target_slug=target_slug,
                    type=rel_type,
                    description=description,
                )
            )

        return connections

    # --- Location Methods ---

    def list_locations(self, location_type: Optional[str] = None) -> list[LocationListItem]:
        """List all locations, optionally filtered by type."""
        locations_dir = self.campaign_dir / "locations"
        if not locations_dir.exists():
            return []

        locations = []
        for loc_file in locations_dir.glob("*.md"):
            if loc_file.name == "index.md":
                continue

            content = loc_file.read_text(encoding="utf-8")
            loc = self._parse_location_list_item(loc_file.stem, content)

            if location_type is None or loc.type.lower() == location_type.lower():
                locations.append(loc)

        return sorted(locations, key=lambda x: x.name.lower())

    def get_location(self, slug: str) -> Optional[LocationDetail]:
        """Get location details by slug."""
        loc_file = self.campaign_dir / "locations" / f"{slug}.md"
        if not loc_file.exists():
            return None

        content = loc_file.read_text(encoding="utf-8")
        return self._parse_location_detail(slug, content)

    def _parse_location_list_item(self, slug: str, content: str) -> LocationListItem:
        """Parse location content into list item."""
        return LocationListItem(
            name=self._extract_title(content),
            slug=slug,
            type=self._extract_metadata(content, "Type") or "other",
            region=self._extract_metadata(content, "Region", strip_links=True),
            discovered=self._extract_metadata(content, "Discovered"),
        )

    def _parse_location_detail(self, slug: str, content: str) -> LocationDetail:
        """Parse location content into detail model."""
        return LocationDetail(
            name=self._extract_title(content),
            slug=slug,
            type=self._extract_metadata(content, "Type") or "other",
            content=content,
            region=self._extract_metadata(content, "Region", strip_links=True),
            discovered=self._extract_metadata(content, "Discovered"),
            key_npcs=self._extract_list_items(content, "Key NPCs"),
        )

    # --- Session Methods ---

    def list_sessions(self) -> list[SessionListItem]:
        """List all sessions."""
        sessions_dir = self.campaign_dir / "sessions"
        if not sessions_dir.exists():
            return []

        sessions = []
        for session_file in sessions_dir.glob("session-*.md"):
            content = session_file.read_text(encoding="utf-8")

            # Extract session number from filename
            match = re.search(r"session-(\d+)\.md", session_file.name)
            if not match:
                continue

            number = int(match.group(1))
            sessions.append(self._parse_session_list_item(number, content))

        return sorted(sessions, key=lambda x: x.number, reverse=True)

    def get_session(self, number: int) -> Optional[SessionDetail]:
        """Get session details by number."""
        session_file = self.campaign_dir / "sessions" / f"session-{number:03d}.md"
        if not session_file.exists():
            return None

        content = session_file.read_text(encoding="utf-8")
        return self._parse_session_detail(number, content)

    def _parse_session_list_item(self, number: int, content: str) -> SessionListItem:
        """Parse session content into list item."""
        title = self._extract_title(content)
        # Remove "Session N: " prefix if present
        title = re.sub(r"^Session \d+:\s*", "", title)

        return SessionListItem(
            number=number,
            title=title,
            date=self._extract_metadata(content, "Date") or "",
            in_game_date=self._extract_metadata(content, "In-Game Date"),
        )

    def _parse_session_detail(self, number: int, content: str) -> SessionDetail:
        """Parse session content into detail model."""
        title = self._extract_title(content)
        title = re.sub(r"^Session \d+:\s*", "", title)

        return SessionDetail(
            number=number,
            title=title,
            date=self._extract_metadata(content, "Date") or "",
            content=content,
            in_game_date=self._extract_metadata(content, "In-Game Date"),
            summary=self._extract_section(content, "Summary"),
            npcs_encountered=self._extract_list_items(content, "NPCs Encountered"),
            locations_visited=self._extract_list_items(content, "Locations Visited"),
        )

    # --- Party Methods ---

    def get_party(self) -> PartyOverview:
        """Get party overview."""
        characters = self.list_characters()

        levels = [c.level for c in characters if c.level is not None]
        avg_level = sum(levels) / len(levels) if levels else None

        return PartyOverview(
            size=len(characters),
            average_level=avg_level,
            characters=characters,
        )

    def list_characters(self) -> list[CharacterListItem]:
        """List all party characters."""
        characters_dir = self.campaign_dir / "party" / "characters"
        if not characters_dir.exists():
            return []

        characters = []
        for char_file in characters_dir.glob("*.md"):
            content = char_file.read_text(encoding="utf-8")
            characters.append(self._parse_character_list_item(char_file.stem, content))

        return sorted(characters, key=lambda x: x.name.lower())

    def get_character(self, slug: str) -> Optional[CharacterDetail]:
        """Get character details by slug."""
        char_file = self.campaign_dir / "party" / "characters" / f"{slug}.md"
        if not char_file.exists():
            return None

        content = char_file.read_text(encoding="utf-8")
        return self._parse_character_detail(slug, content)

    def _parse_character_list_item(self, slug: str, content: str) -> CharacterListItem:
        """Parse character content into list item."""
        # Try explicit Level field first
        level_str = self._extract_metadata(content, "Level")
        level = int(level_str) if level_str and level_str.isdigit() else None

        class_info = self._extract_metadata(content, "Class", strip_links=True)

        # If no explicit level, extract from class info (e.g., "Rogue 1" or "Fighter 5/Wizard 3")
        if level is None and class_info:
            level = self._extract_level_from_class(class_info)

        return CharacterListItem(
            name=self._extract_title(content),
            slug=slug,
            player=self._extract_metadata(content, "Player"),
            species=self._extract_metadata(content, "Species", strip_links=True),
            class_info=class_info,
            level=level,
        )

    def _parse_character_detail(self, slug: str, content: str) -> CharacterDetail:
        """Parse character content into detail model."""
        # Try explicit Level field first
        level_str = self._extract_metadata(content, "Level")
        level = int(level_str) if level_str and level_str.isdigit() else None

        class_info = self._extract_metadata(content, "Class", strip_links=True)

        # If no explicit level, extract from class info (e.g., "Rogue 1" or "Fighter 5/Wizard 3")
        if level is None and class_info:
            level = self._extract_level_from_class(class_info)

        return CharacterDetail(
            name=self._extract_title(content),
            slug=slug,
            content=content,
            player=self._extract_metadata(content, "Player"),
            species=self._extract_metadata(content, "Species", strip_links=True),
            class_info=class_info,
            level=level,
        )

    def _extract_level_from_class(self, class_info: str) -> Optional[int]:
        """Extract total character level from class info string.

        Handles formats like:
        - "Rogue 1"
        - "Fighter 5"
        - "Fighter 5/Wizard 3" (multiclass, returns 8)
        - "Rogue" (no level, returns None)
        """
        import re
        # Find all class/level pairs like "Rogue 1" or "Wizard 3"
        pattern = r'(\w+)\s+(\d+)'
        matches = re.findall(pattern, class_info)
        if not matches:
            return None
        # Sum all levels for multiclass characters
        total_level = sum(int(level) for _, level in matches)
        return total_level if total_level > 0 else None

    # --- Encounter Methods ---

    def list_encounters(self) -> list[EncounterListItem]:
        """List all saved encounters."""
        encounters_dir = self.campaign_dir / "encounters"
        if not encounters_dir.exists():
            return []

        encounters = []
        for enc_file in encounters_dir.glob("*.md"):
            if enc_file.name == "index.md":
                continue

            content = enc_file.read_text(encoding="utf-8")
            encounters.append(self._parse_encounter_list_item(enc_file.stem, content))

        return sorted(encounters, key=lambda x: x.name.lower())

    def get_encounter(self, slug: str) -> Optional[EncounterDetail]:
        """Get encounter details by slug."""
        enc_file = self.campaign_dir / "encounters" / f"{slug}.md"
        if not enc_file.exists():
            return None

        content = enc_file.read_text(encoding="utf-8")
        return self._parse_encounter_detail(slug, content)

    def _parse_encounter_list_item(self, slug: str, content: str) -> EncounterListItem:
        """Parse encounter content into list item."""
        party_level_str = self._extract_metadata(content, "Party Level")
        party_level = int(party_level_str) if party_level_str and party_level_str.isdigit() else 1

        party_size_str = self._extract_metadata(content, "Party Size")
        party_size = int(party_size_str) if party_size_str and party_size_str.isdigit() else 4

        # Extract base XP (stored as "Base XP: 1,234")
        base_xp_str = self._extract_metadata(content, "Base XP")
        base_xp = 0
        if base_xp_str:
            # Remove commas from number format
            base_xp = int(base_xp_str.replace(",", "")) if base_xp_str.replace(",", "").isdigit() else 0

        total_creatures = self._count_encounter_creatures(content)
        created = self._extract_metadata(content, "Created")

        return EncounterListItem(
            name=self._extract_title(content),
            slug=slug,
            difficulty=self._extract_metadata(content, "Difficulty") or "Medium",
            total_creatures=total_creatures,
            party_level=party_level,
            party_size=party_size,
            base_xp=base_xp,
            created=created,
        )

    def _parse_encounter_detail(self, slug: str, content: str) -> EncounterDetail:
        """Parse encounter content into detail model."""
        party_level_str = self._extract_metadata(content, "Party Level")
        party_level = int(party_level_str) if party_level_str and party_level_str.isdigit() else 1

        party_size_str = self._extract_metadata(content, "Party Size")
        party_size = int(party_size_str) if party_size_str and party_size_str.isdigit() else 4

        creatures = self._parse_encounter_creatures(content)
        total_xp = sum(c.xp * c.count for c in creatures)

        return EncounterDetail(
            name=self._extract_title(content),
            slug=slug,
            content=content,
            difficulty=self._extract_metadata(content, "Difficulty") or "Medium",
            party_level=party_level,
            party_size=party_size,
            creatures=creatures,
            total_xp=total_xp,
        )

    def _count_encounter_creatures(self, content: str) -> int:
        """Count total creatures in encounter."""
        creatures = self._parse_encounter_creatures(content)
        return sum(c.count for c in creatures)

    def _parse_encounter_creatures(self, content: str) -> list[EncounterCreature]:
        """Parse creatures table from encounter content."""
        creatures = []

        # Look for creatures table
        # | Creature | CR | XP | Count | Total XP |
        table_match = re.search(r"\| Creature \|.*?\n\|[-\s|]+\n(.*?)(?=\n\n|\Z)", content, re.DOTALL)
        if not table_match:
            return creatures

        for line in table_match.group(1).split("\n"):
            if not line.strip() or not line.startswith("|"):
                continue

            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 4:
                # Extract name from link if present
                name_match = re.match(r"\[(.+?)\]", cells[0])
                name = name_match.group(1) if name_match else cells[0]

                try:
                    creatures.append(
                        EncounterCreature(
                            name=name,
                            cr=cells[1],
                            xp=int(cells[2].replace(",", "")),
                            count=int(cells[3]),
                        )
                    )
                except (ValueError, IndexError):
                    continue

        return creatures

    def create_encounter(self, encounter: EncounterCreate) -> EncounterDetail:
        """Create a new encounter and save to file.

        Raises:
            ValueError: If an encounter with the same name already exists.
        """
        encounters_dir = self.campaign_dir / "encounters"
        encounters_dir.mkdir(parents=True, exist_ok=True)

        slug = slugify(encounter.name)
        enc_file = encounters_dir / f"{slug}.md"

        # Check for duplicate encounter name
        if enc_file.exists():
            raise ValueError(f"An encounter named '{encounter.name}' already exists")

        # Calculate difficulty and XP
        base_xp = sum(c.xp * c.count for c in encounter.creatures)
        total_creatures = sum(c.count for c in encounter.creatures)
        multiplier = self._get_encounter_multiplier(total_creatures)
        adjusted_xp = int(base_xp * multiplier)
        difficulty = self._calculate_difficulty(
            adjusted_xp, encounter.party_level, encounter.party_size
        )

        # Generate loot based on highest CR creature and total count
        loot_markdown = self._generate_encounter_loot(encounter.creatures, total_creatures)

        # Generate markdown content
        content = self._generate_encounter_markdown(
            name=encounter.name,
            party_level=encounter.party_level,
            party_size=encounter.party_size,
            creatures=encounter.creatures,
            difficulty=difficulty,
            base_xp=base_xp,
            adjusted_xp=adjusted_xp,
            loot_markdown=loot_markdown,
        )

        enc_file.write_text(content, encoding="utf-8")

        # Update the encounters index
        creature_list = ", ".join(f"{c.count}x {c.name}" for c in encounter.creatures)
        self._update_encounter_index(
            name=encounter.name,
            slug=slug,
            difficulty=difficulty,
            party_level=encounter.party_level,
            creature_list=creature_list,
        )

        return EncounterDetail(
            name=encounter.name,
            slug=slug,
            content=content,
            difficulty=difficulty,
            party_level=encounter.party_level,
            party_size=encounter.party_size,
            creatures=[
                EncounterCreature(name=c.name, cr=c.cr, xp=c.xp, count=c.count)
                for c in encounter.creatures
            ],
            total_xp=base_xp,
            has_active_combat=False,
        )

    def update_encounter(self, slug: str, update: EncounterUpdate) -> Optional[EncounterDetail]:
        """Update an existing encounter."""
        existing = self.get_encounter(slug)
        if not existing:
            return None

        # Merge updates with existing values
        name = update.name if update.name is not None else existing.name
        party_level = update.party_level if update.party_level is not None else existing.party_level
        party_size = update.party_size if update.party_size is not None else existing.party_size
        creatures = update.creatures if update.creatures is not None else [
            EncounterCreate.__annotations__["creatures"].__args__[0](
                name=c.name, slug=slugify(c.name), cr=c.cr, xp=c.xp, count=c.count
            )
            for c in existing.creatures
        ]

        # Recalculate if creatures changed
        base_xp = sum(c.xp * c.count for c in creatures)
        total_creatures = sum(c.count for c in creatures)
        multiplier = self._get_encounter_multiplier(total_creatures)
        adjusted_xp = int(base_xp * multiplier)
        difficulty = self._calculate_difficulty(adjusted_xp, party_level, party_size)

        # Generate loot based on creatures
        loot_markdown = self._generate_encounter_loot(creatures, total_creatures)

        # Generate new content
        content = self._generate_encounter_markdown(
            name=name,
            party_level=party_level,
            party_size=party_size,
            creatures=creatures,
            difficulty=difficulty,
            base_xp=base_xp,
            adjusted_xp=adjusted_xp,
            loot_markdown=loot_markdown,
        )

        # Write to file (use existing slug)
        enc_file = self.campaign_dir / "encounters" / f"{slug}.md"
        enc_file.write_text(content, encoding="utf-8")

        # Update the encounters index
        creature_list = ", ".join(f"{c.count}x {c.name}" for c in creatures)
        self._update_encounter_index(
            name=name,
            slug=slug,
            difficulty=difficulty,
            party_level=party_level,
            creature_list=creature_list,
        )

        return EncounterDetail(
            name=name,
            slug=slug,
            content=content,
            difficulty=difficulty,
            party_level=party_level,
            party_size=party_size,
            creatures=[
                EncounterCreature(name=c.name, cr=c.cr, xp=c.xp, count=c.count)
                for c in creatures
            ],
            total_xp=base_xp,
            has_active_combat=self._has_active_combat(slug),
        )

    def _has_active_combat(self, encounter_slug: str) -> bool:
        """Check if an encounter has an active combat state file."""
        combat_file = self.campaign_dir / "encounters" / f"combat-{encounter_slug}.json"
        return combat_file.exists()

    def _update_encounter_index(
        self,
        name: str,
        slug: str,
        difficulty: str,
        party_level: int,
        creature_list: str,
    ) -> None:
        """Update the encounters index with a new or modified encounter.

        If the encounter already exists in the index, update its row.
        Otherwise, add a new row after the table header.
        """
        index_path = self.campaign_dir / "encounters" / "index.md"
        if not index_path.exists():
            return

        content = index_path.read_text(encoding="utf-8")
        filename = f"{slug}.md"
        new_row = f"| [{name}]({filename}) | {difficulty} | {party_level} | {creature_list} |"

        lines = content.split("\n")
        new_lines = []
        updated = False

        for line in lines:
            # Check if this line is an existing entry for this encounter
            if f"]({filename})" in line:
                # Replace with updated row
                new_lines.append(new_row)
                updated = True
            else:
                new_lines.append(line)
                # If this is the header separator and we haven't updated, add new row
                if line.startswith("| ----") and not updated and filename not in content:
                    new_lines.append(new_row)
                    updated = True

        # Remove placeholder if present
        final_lines = [l for l in new_lines if "*No encounters saved yet" not in l]

        index_path.write_text("\n".join(final_lines), encoding="utf-8")

    def _get_encounter_multiplier(self, num_creatures: int) -> float:
        """Get encounter multiplier based on creature count (DMG rules)."""
        multipliers = [
            (1, 1, 1.0),
            (2, 2, 1.5),
            (3, 6, 2.0),
            (7, 10, 2.5),
            (11, 14, 3.0),
            (15, float("inf"), 4.0),
        ]
        for min_c, max_c, mult in multipliers:
            if min_c <= num_creatures <= max_c:
                return mult
        return 4.0

    def _calculate_difficulty(self, adjusted_xp: int, party_level: int, party_size: int) -> str:
        """Calculate encounter difficulty based on XP thresholds."""
        xp_thresholds = {
            1: (25, 50, 75, 100),
            2: (50, 100, 150, 200),
            3: (75, 150, 225, 400),
            4: (125, 250, 375, 500),
            5: (250, 500, 750, 1100),
            6: (300, 600, 900, 1400),
            7: (350, 750, 1100, 1700),
            8: (450, 900, 1400, 2100),
            9: (550, 1100, 1600, 2400),
            10: (600, 1200, 1900, 2800),
            11: (800, 1600, 2400, 3600),
            12: (1000, 2000, 3000, 4500),
            13: (1100, 2200, 3400, 5100),
            14: (1250, 2500, 3800, 5700),
            15: (1400, 2800, 4300, 6400),
            16: (1600, 3200, 4800, 7200),
            17: (2000, 3900, 5900, 8800),
            18: (2100, 4200, 6300, 9500),
            19: (2400, 4900, 7300, 10900),
            20: (2800, 5700, 8500, 12700),
        }

        level = max(1, min(20, party_level))
        thresholds = xp_thresholds[level]
        easy = thresholds[0] * party_size
        medium = thresholds[1] * party_size
        hard = thresholds[2] * party_size
        deadly = thresholds[3] * party_size

        if adjusted_xp < easy:
            return "Trivial"
        elif adjusted_xp < medium:
            return "Easy"
        elif adjusted_xp < hard:
            return "Medium"
        elif adjusted_xp < deadly:
            return "Hard"
        else:
            return "Deadly"

    def _generate_encounter_loot(self, creatures: list, total_creatures: int) -> str:
        """Generate loot for an encounter based on creatures.

        Args:
            creatures: List of creatures in the encounter
            total_creatures: Total number of creatures

        Returns:
            Markdown-formatted loot section
        """
        try:
            # Import loot generator
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from campaign.loot_generator import LootGenerator, TreasureFormatter, parse_cr

            # Find the highest CR among creatures
            max_cr = 0.0
            for c in creatures:
                try:
                    cr = parse_cr(str(c.cr))
                    if cr > max_cr:
                        max_cr = cr
                except ValueError:
                    continue

            if max_cr == 0 and creatures:
                max_cr = 0.25  # Default to CR 1/4 if all CRs invalid

            # Generate individual loot for each creature
            reference_index = Path("books/reference/reference-index.json")
            generator = LootGenerator(
                reference_index_path=reference_index if reference_index.exists() else None
            )
            treasure = generator.generate_individual(max_cr, total_creatures)

            # Format as markdown
            formatter = TreasureFormatter(generator.linker)
            loot_text = formatter.format_console(treasure, f"Treasure (Individual, {total_creatures} creatures)")

            return loot_text
        except Exception as e:
            # If loot generation fails, return empty section
            return f"## Treasure\n\n*Loot generation failed: {e}*\n"

    def _generate_encounter_markdown(
        self,
        name: str,
        party_level: int,
        party_size: int,
        creatures: list,
        difficulty: str,
        base_xp: int,
        adjusted_xp: int,
        loot_markdown: str = "",
    ) -> str:
        """Generate markdown content for an encounter."""
        lines = [
            f"# {name}",
            "",
            f"**Difficulty**: {difficulty}  ",
            f"**Party Level**: {party_level}  ",
            f"**Party Size**: {party_size}  ",
            f"**Total Creatures**: {sum(c.count for c in creatures)}  ",
            f"**Base XP**: {base_xp:,}  ",
            f"**Adjusted XP**: {adjusted_xp:,}  ",
            f"**Created**: {datetime.now().isoformat(timespec='seconds')}",
            "",
            "## Creatures",
            "",
            "| Creature | CR | XP | Count | Total XP |",
            "|----------|----|----|-------|----------|",
        ]

        for c in creatures:
            total = c.xp * c.count
            lines.append(f"| {c.name} | {c.cr} | {c.xp:,} | {c.count} | {total:,} |")

        lines.append("")

        # Add loot section if provided
        if loot_markdown:
            lines.append(loot_markdown)
            lines.append("")

        return "\n".join(lines)

    # --- Helper Methods ---

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown heading."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1).strip() if match else "Untitled"

    def _extract_metadata(
        self, content: str, key: str, strip_links: bool = False
    ) -> Optional[str]:
        """Extract metadata value from bold key pattern.

        Args:
            content: The markdown content to search
            key: The metadata key (e.g., "Role", "Location")
            strip_links: If True, extract text from markdown links [text](url)
        """
        pattern = rf"\*\*{key}\*\*:\s*(.+?)(?:\s\s|\n|$)"
        match = re.search(pattern, content)
        if not match:
            return None

        value = match.group(1).strip()
        if strip_links:
            value = self._strip_markdown_links(value)
        return value

    def _strip_markdown_links(self, text: str) -> str:
        """Convert markdown links [text](url) to just text."""
        return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    def _extract_section(self, content: str, heading: str) -> Optional[str]:
        """Extract content from a markdown section."""
        pattern = rf"## {heading}\s*\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Skip placeholder text
            if text.startswith("*") and text.endswith("*"):
                return None
            return text
        return None

    def _extract_list_items(self, content: str, heading: str) -> list[str]:
        """Extract list items from a section."""
        section = self._extract_section(content, heading)
        if not section:
            return []

        items = []
        for line in section.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                # Extract text, removing link syntax
                text = line[2:]
                link_match = re.match(r"\[(.+?)\]\(.+?\)", text)
                if link_match:
                    text = link_match.group(1)
                items.append(text)

        return items

"""Magic item extractor for 5etools data."""

import json
import sys
from pathlib import Path
from typing import Optional

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_book import TagConverter, EntryConverter
from extractors.base import make_safe_filename


class ItemExtractor:
    """Extracts items to individual markdown files."""

    RARITY_ORDER = ['common', 'uncommon', 'rare', 'very rare', 'legendary', 'artifact', 'unknown']

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        """
        Initialize the item extractor.

        Args:
            output_dir: Directory to output item files
            sources: List of source codes to filter by (e.g., ['XDMG', 'XPHB', 'AAG'])
        """
        self.output_dir = Path(output_dir)
        self.sources = [s.upper() for s in sources] if sources else None
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract items from a source file. Returns count extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        items = data.get('item', [])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for item in items:
            if not isinstance(item, dict):
                continue

            # Filter by source if specified
            item_source = item.get('source', '').upper()
            if self.sources and item_source not in self.sources:
                continue

            self._extract_item(item)
            count += 1

        return count

    def _extract_item(self, item: dict) -> None:
        """Extract a single item to a markdown file."""
        name = item.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        content = self._item_to_markdown(item)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to index with enriched data
        rarity = item.get('rarity', 'unknown')
        if isinstance(rarity, dict):
            rarity = rarity.get('rarity', 'unknown')
        rarity = rarity.title() if rarity else 'Unknown'

        item_type = self._get_item_type(item)
        source = item.get('source', '')
        attunement = item.get('reqAttune', False)

        # Damage types (for weapons)
        damage_types = []
        dmg_type = item.get('dmgType', '')
        if dmg_type:
            dmg_map = {'B': 'bludgeoning', 'P': 'piercing', 'S': 'slashing',
                       'A': 'acid', 'C': 'cold', 'F': 'fire', 'L': 'lightning',
                       'N': 'necrotic', 'O': 'force', 'R': 'radiant', 'T': 'thunder',
                       'Y': 'psychic', 'I': 'poison'}
            damage_types.append(dmg_map.get(dmg_type, dmg_type))

        # Properties
        properties = []
        for prop in item.get('property', []):
            if isinstance(prop, str):
                properties.append(prop)
            elif isinstance(prop, dict):
                properties.append(prop.get('property', ''))

        self.index_entries.append({
            'name': name,
            'rarity': rarity,
            'item_type': item_type,
            'source': source,
            'attunement': bool(attunement),
            'path': filename,
            'damage_types': damage_types,
            'properties': properties,
        })

    def _item_to_markdown(self, item: dict) -> str:
        """Convert an item to markdown."""
        parts = []

        name = item.get('name', 'Unknown')
        source = item.get('source', '')
        page = item.get('page', '')

        parts.append(f"# {name}")
        parts.append("")

        # Type and rarity line
        item_type = self._get_item_type(item)
        rarity = item.get('rarity', 'unknown')
        if isinstance(rarity, dict):
            rarity = rarity.get('rarity', 'unknown')

        type_line = f"*{item_type}"
        if rarity and rarity != 'none':
            type_line += f", {rarity}"
        type_line += "*"
        parts.append(type_line)
        parts.append("")

        # Source
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Attunement
        attune = item.get('reqAttune', False)
        if attune:
            if isinstance(attune, str):
                parts.append(f"**Requires Attunement:** {attune}")
            else:
                parts.append("**Requires Attunement**")
            parts.append("")

        # Weight
        weight = item.get('weight', None)
        if weight:
            parts.append(f"**Weight:** {weight} lb.")

        # Value
        value = item.get('value', None)
        if value:
            parts.append(f"**Value:** {self._format_value(value)}")

        # Weapon/armor specific properties
        if item.get('weaponCategory'):
            parts.append(f"**Weapon Category:** {item.get('weaponCategory')}")
            dmg1 = item.get('dmg1')
            dmg_type = item.get('dmgType')
            if dmg1:
                parts.append(f"**Damage:** {dmg1} {self._get_damage_type(dmg_type)}")

        if item.get('ac'):
            parts.append(f"**Armor Class:** {item.get('ac')}")

        parts.append("")
        parts.append("---")
        parts.append("")

        # Description/entries
        entries = item.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        return "\n".join(parts)

    def _get_item_type(self, item: dict) -> str:
        """Determine the item type string."""
        type_code = item.get('type', '')
        wondrous = item.get('wondrous', False)
        weapon = item.get('weaponCategory', '')
        armor = item.get('armor', False)

        if wondrous:
            return "Wondrous item"
        elif weapon:
            return f"Weapon ({weapon})"
        elif armor:
            return "Armor"
        elif type_code:
            type_map = {
                'A': 'Ammunition',
                'AF': 'Ammunition (firearm)',
                'AT': "Artisan's tools",
                'EM': 'Eldritch machine',
                'EXP': 'Explosive',
                'G': 'Adventuring gear',
                'GS': 'Gaming set',
                'HA': 'Heavy armor',
                'INS': 'Instrument',
                'LA': 'Light armor',
                'M': 'Melee weapon',
                'MA': 'Medium armor',
                'MNT': 'Mount',
                'P': 'Potion',
                'R': 'Ranged weapon',
                'RD': 'Rod',
                'RG': 'Ring',
                'S': 'Shield',
                'SC': 'Scroll',
                'SCF': 'Spellcasting focus',
                'T': 'Tools',
                'TAH': 'Tack and harness',
                'TG': 'Trade good',
                'VEH': 'Vehicle',
                'WD': 'Wand',
                '$': 'Treasure',
            }
            return type_map.get(type_code, type_code)
        return "Item"

    def _get_damage_type(self, dmg_type: str) -> str:
        """Convert damage type code to full name."""
        type_map = {
            'B': 'bludgeoning',
            'P': 'piercing',
            'S': 'slashing',
            'A': 'acid',
            'C': 'cold',
            'F': 'fire',
            'O': 'force',
            'L': 'lightning',
            'N': 'necrotic',
            'I': 'poison',
            'Y': 'psychic',
            'R': 'radiant',
            'T': 'thunder',
        }
        return type_map.get(dmg_type, dmg_type or '')

    def _format_value(self, value: int) -> str:
        """Format value in copper to readable format."""
        if value >= 100:
            gp = value // 100
            remainder = value % 100
            if remainder:
                return f"{gp} gp, {remainder} cp"
            return f"{gp} gp"
        elif value >= 10:
            sp = value // 10
            remainder = value % 10
            if remainder:
                return f"{sp} sp, {remainder} cp"
            return f"{sp} sp"
        return f"{value} cp"

    def create_index(self) -> None:
        """Create the item index file."""
        parts = ["# Magic Item Index", ""]

        # Summary
        parts.append(f"**Total Items:** {len(self.index_entries)}")
        parts.append("")

        # Group by rarity
        by_rarity = {}
        for item in self.index_entries:
            rarity = item['rarity']
            if rarity not in by_rarity:
                by_rarity[rarity] = []
            by_rarity[rarity].append(item)

        parts.append("## By Rarity")
        parts.append("")

        for rarity in self.RARITY_ORDER:
            if rarity not in by_rarity:
                continue

            parts.append(f"### {rarity.title()}")
            parts.append("")
            parts.append("| Item | Type | Attunement | Source |")
            parts.append("| ---- | ---- | ---------- | ------ |")

            for item in sorted(by_rarity[rarity], key=lambda x: x['name']):
                name = item['name']
                itype = item['type']
                attune = "Yes" if item['attunement'] else "No"
                source = item['source']
                path = item['path']
                parts.append(f"| [{name}]({path}) | {itype} | {attune} | {source} |")

            parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

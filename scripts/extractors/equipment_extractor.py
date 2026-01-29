"""Equipment extractor for mundane gear from 5etools data."""

import json
import sys
from pathlib import Path
from typing import Optional

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_book import TagConverter, EntryConverter
from extractors.base import make_safe_filename


# Sources to include
ALLOWED_SOURCES = {'XPHB', 'XDMG', 'XMM', 'AAG', 'BAM'}

# Item type codes for mundane equipment
MUNDANE_TYPES = {
    'G': 'Adventuring Gear',
    'A': 'Ammunition',
    'AT': 'Artisan Tools',
    'GS': 'Gaming Set',
    'INS': 'Musical Instrument',
    'T': 'Tools',
    'TG': 'Trade Goods',
    'TAH': 'Tack and Harness',
    'MNT': 'Mount',
    'VEH': 'Vehicle',
    'SHP': 'Ship',
    'AIR': 'Airship',
    'FD': 'Food and Drink',
    'SCF': 'Spellcasting Focus',
    # Weapons
    'M': 'Melee Weapon',
    'R': 'Ranged Weapon',
    # Armor
    'LA': 'Light Armor',
    'MA': 'Medium Armor',
    'HA': 'Heavy Armor',
    'S': 'Shield',
}

# Categories for organization
EQUIPMENT_CATEGORIES = {
    'weapons': {'M', 'R'},
    'armor': {'LA', 'MA', 'HA', 'S'},
    'gear': {'G', 'A', 'AT', 'GS', 'INS', 'T', 'TG', 'TAH', 'FD', 'SCF'},
    'mounts': {'MNT', 'VEH', 'SHP', 'AIR'},
}


class EquipmentExtractor:
    """Extracts mundane equipment to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        """
        Initialize the equipment extractor.

        Args:
            output_dir: Directory to output equipment files
            sources: List of source codes to filter by (defaults to ALLOWED_SOURCES)
        """
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract equipment from a source file. Returns count extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        items = data.get('item', [])
        count = 0

        for item in items:
            if not isinstance(item, dict):
                continue

            # Filter by source
            item_source = item.get('source', '').upper()
            if item_source not in self.sources:
                continue

            # Skip magic items (have rarity or wondrous)
            if item.get('rarity') and item.get('rarity') != 'none':
                continue
            if item.get('wondrous'):
                continue

            # Get item type
            item_type = item.get('type', '')
            # Handle compound types like "G|XPHB"
            if '|' in item_type:
                item_type = item_type.split('|')[0]

            # Skip if not a mundane type
            if item_type not in MUNDANE_TYPES:
                continue

            self._extract_item(item, item_type)
            count += 1

        return count

    def extract_base_items(self, source_path: str) -> int:
        """Extract base items (weapons, armor) from items-base.json. Returns count extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        items = data.get('baseitem', [])
        count = 0

        for item in items:
            if not isinstance(item, dict):
                continue

            # Filter by source
            item_source = item.get('source', '').upper()
            if item_source not in self.sources:
                continue

            # Get item type
            item_type = item.get('type', '')
            # Handle compound types like "M|XPHB"
            if '|' in item_type:
                item_type = item_type.split('|')[0]

            # Skip if not a mundane type
            if item_type not in MUNDANE_TYPES:
                continue

            self._extract_item(item, item_type)
            count += 1

        return count

    def _get_category(self, item_type: str) -> str:
        """Get the category folder for an item type."""
        for category, types in EQUIPMENT_CATEGORIES.items():
            if item_type in types:
                return category
        return 'gear'

    def _extract_item(self, item: dict, item_type: str) -> None:
        """Extract a single equipment item to a markdown file."""
        name = item.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        category = self._get_category(item_type)

        # Create category directory
        cat_dir = self.output_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{safe_name}.md"
        filepath = cat_dir / filename

        content = self._item_to_markdown(item, item_type)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to index with enriched data
        source = item.get('source', '')
        type_name = MUNDANE_TYPES.get(item_type, item_type)
        weight = item.get('weight', '')
        value = item.get('value', 0)

        # Format cost
        cost = self._format_value(value) if value else '-'

        # Get damage for weapons
        damage = ''
        if item_type in {'M', 'R'}:
            dmg1 = item.get('dmg1', '')
            dmg_type = item.get('dmgType', '')
            dmg_map = {'B': 'bludgeoning', 'P': 'piercing', 'S': 'slashing'}
            if dmg1:
                damage = f"{dmg1} {dmg_map.get(dmg_type, dmg_type)}"

        # Get AC for armor
        ac = ''
        if item_type in {'LA', 'MA', 'HA', 'S'}:
            ac = item.get('ac', '')

        self.index_entries.append({
            'name': name,
            'type': type_name,
            'category': category,
            'source': source,
            'weight': weight,
            'value': value,
            'cost': cost,
            'damage': damage,
            'ac': ac,
            'path': f"{category}/{filename}",
        })

    def _item_to_markdown(self, item: dict, item_type: str) -> str:
        """Convert an equipment item to markdown."""
        parts = []

        name = item.get('name', 'Unknown')
        source = item.get('source', '')
        page = item.get('page', '')
        type_name = MUNDANE_TYPES.get(item_type, item_type)

        parts.append(f"# {name}")
        parts.append("")
        parts.append(f"*{type_name}*")
        parts.append("")

        # Source
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append("---")
        parts.append("")

        # Weight
        weight = item.get('weight')
        if weight:
            parts.append(f"**Weight:** {weight} lb.")

        # Value/Cost
        value = item.get('value')
        if value:
            parts.append(f"**Cost:** {self._format_value(value)}")

        # Weapon properties
        if item_type in {'M', 'R'}:
            # Damage
            dmg1 = item.get('dmg1')
            dmg_type = item.get('dmgType')
            if dmg1:
                dmg_str = f"{dmg1} {self._get_damage_type(dmg_type)}"
                parts.append(f"**Damage:** {dmg_str}")

            # Properties
            properties = item.get('property', [])
            if properties:
                prop_str = ', '.join(self._format_property(p) for p in properties)
                parts.append(f"**Properties:** {prop_str}")

            # Range
            item_range = item.get('range')
            if item_range:
                parts.append(f"**Range:** {item_range} ft.")

        # Armor properties
        if item_type in {'LA', 'MA', 'HA', 'S'}:
            ac = item.get('ac')
            if ac:
                parts.append(f"**Armor Class:** {ac}")

            strength = item.get('strength')
            if strength:
                parts.append(f"**Strength Required:** {strength}")

            stealth = item.get('stealth')
            if stealth:
                parts.append("**Stealth:** Disadvantage")

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

    def _get_damage_type(self, dmg_type: str) -> str:
        """Convert damage type code to full name."""
        type_map = {
            'B': 'bludgeoning',
            'P': 'piercing',
            'S': 'slashing',
        }
        return type_map.get(dmg_type, dmg_type or '')

    def _format_property(self, prop) -> str:
        """Format weapon property code."""
        prop_map = {
            'L': 'Light',
            'F': 'Finesse',
            'H': 'Heavy',
            '2H': 'Two-Handed',
            'V': 'Versatile',
            'T': 'Thrown',
            'A': 'Ammunition',
            'LD': 'Loading',
            'R': 'Reach',
            'S': 'Special',
            'AF': 'Ammunition (Firearm)',
            'RLD': 'Reload',
            'BF': 'Burst Fire',
        }
        # Handle dict properties (e.g., versatile with damage)
        if isinstance(prop, dict):
            prop_code = prop.get('property', '')
            if '|' in prop_code:
                prop_code = prop_code.split('|')[0]
            return prop_map.get(prop_code, prop_code)
        # Handle string with pipe (e.g., "V|XPHB")
        if isinstance(prop, str) and '|' in prop:
            prop = prop.split('|')[0]
        return prop_map.get(prop, prop)

    def create_index(self) -> None:
        """Create the equipment index file."""
        parts = ["# Equipment Index", ""]
        parts.append(f"**Total Equipment:** {len(self.index_entries)}")
        parts.append("")

        # Group by category
        by_category = {}
        for item in self.index_entries:
            cat = item['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)

        category_order = ['weapons', 'armor', 'gear', 'mounts']
        category_names = {
            'weapons': 'Weapons',
            'armor': 'Armor and Shields',
            'gear': 'Adventuring Gear',
            'mounts': 'Mounts and Vehicles',
        }

        for category in category_order:
            if category not in by_category:
                continue

            parts.append(f"## {category_names.get(category, category.title())}")
            parts.append("")
            parts.append("| Item | Type | Cost | Weight | Source |")
            parts.append("| ---- | ---- | ---- | ------ | ------ |")

            for item in sorted(by_category[category], key=lambda x: x['name']):
                name = item['name']
                itype = item['type']
                value = self._format_value(item['value']) if item['value'] else '-'
                weight = f"{item['weight']} lb." if item['weight'] else '-'
                source = item['source']
                path = item['path']
                parts.append(f"| [{name}]({path}) | {itype} | {value} | {weight} | {source} |")

            parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

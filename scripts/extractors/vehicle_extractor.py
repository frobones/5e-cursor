"""Vehicle/Ship extractor for 5etools data."""

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


class VehicleExtractor:
    """Extracts vehicles/ships to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract vehicles from a source file."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        vehicles = data.get('vehicle', [])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for vehicle in vehicles:
            if not isinstance(vehicle, dict):
                continue

            source = vehicle.get('source', '').upper()
            if source not in self.sources:
                continue

            self._extract_vehicle(vehicle)
            count += 1

        return count

    def _extract_vehicle(self, vehicle: dict) -> None:
        """Extract a single vehicle."""
        name = vehicle.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        content = self._vehicle_to_markdown(vehicle)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        source = vehicle.get('source', '')
        vtype = vehicle.get('vehicleType', 'vehicle')
        
        self.index_entries.append({
            'name': name,
            'type': vtype,
            'source': source,
            'path': filename,
        })

    def _vehicle_to_markdown(self, vehicle: dict) -> str:
        """Convert a vehicle to markdown."""
        parts = []

        name = vehicle.get('name', 'Unknown')
        source = vehicle.get('source', '')
        page = vehicle.get('page', '')
        vtype = vehicle.get('vehicleType', 'vehicle')

        parts.append(f"# {name}")
        parts.append("")
        
        type_names = {'SHIP': 'Spelljammer Ship', 'INFWAR': 'Infernal War Machine', 'CREATURE': 'Creature Vehicle'}
        parts.append(f"*{type_names.get(vtype, 'Vehicle')}*")
        parts.append("")

        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append("---")
        parts.append("")

        # Size
        size = vehicle.get('size', '')
        if size:
            size_map = {'G': 'Gargantuan', 'H': 'Huge', 'L': 'Large', 'M': 'Medium'}
            parts.append(f"**Size:** {size_map.get(size, size)}")

        # Dimensions
        dimensions = vehicle.get('dimensions', [])
        if dimensions:
            parts.append(f"**Dimensions:** {' x '.join(dimensions)}")

        # Pace/Speed
        pace = vehicle.get('pace', '')
        if pace:
            if isinstance(pace, dict):
                pace_parts = [f"{k} {v}" for k, v in pace.items()]
                pace = ', '.join(pace_parts)
            parts.append(f"**Pace:** {pace}")

        speed = vehicle.get('speed', '')
        if speed:
            if isinstance(speed, dict):
                speed_parts = [f"{k} {v} ft." for k, v in speed.items()]
                speed = ', '.join(speed_parts)
            parts.append(f"**Speed:** {speed}")

        # Crew
        crew = vehicle.get('crew', {})
        if crew:
            if isinstance(crew, dict):
                min_crew = crew.get('min', 0)
                max_crew = crew.get('max', min_crew)
                parts.append(f"**Crew:** {min_crew}-{max_crew}")
            else:
                parts.append(f"**Crew:** {crew}")

        # Passengers
        passengers = vehicle.get('passengers', '')
        if passengers:
            parts.append(f"**Passengers:** {passengers}")

        # Cargo
        cargo = vehicle.get('cargo', '')
        if cargo:
            parts.append(f"**Cargo:** {cargo} tons")

        # AC and HP
        ac = vehicle.get('ac', '')
        if ac:
            parts.append(f"**Armor Class:** {ac}")

        hp = vehicle.get('hp', {})
        if hp:
            if isinstance(hp, dict):
                parts.append(f"**Hit Points:** {hp.get('hp', hp)}")
            else:
                parts.append(f"**Hit Points:** {hp}")

        # Damage Threshold
        thresh = vehicle.get('damThresh', '')
        if thresh:
            parts.append(f"**Damage Threshold:** {thresh}")

        parts.append("")
        parts.append("---")
        parts.append("")

        # Entries/description
        entries = vehicle.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)
                parts.append("")

        # Weapons
        weapons = vehicle.get('weapon', [])
        if weapons:
            parts.append("## Weapons")
            parts.append("")
            for weapon in weapons:
                if isinstance(weapon, dict):
                    w_name = weapon.get('name', 'Weapon')
                    parts.append(f"### {w_name}")
                    parts.append("")
                    w_entries = weapon.get('entries', [])
                    if w_entries:
                        content = self.converter.convert(w_entries, 0)
                        if content:
                            parts.append(content)
                            parts.append("")

        # Actions
        actions = vehicle.get('action', [])
        if actions:
            parts.append("## Actions")
            parts.append("")
            for action in actions:
                if isinstance(action, dict):
                    a_name = action.get('name', 'Action')
                    parts.append(f"### {a_name}")
                    parts.append("")
                    a_entries = action.get('entries', [])
                    if a_entries:
                        content = self.converter.convert(a_entries, 0)
                        if content:
                            parts.append(content)
                            parts.append("")

        return "\n".join(parts)

    def create_index(self) -> None:
        """Create the vehicle index file."""
        parts = ["# Vehicle Index", ""]
        parts.append(f"**Total Vehicles:** {len(self.index_entries)}")
        parts.append("")

        parts.append("| Vehicle | Type | Source |")
        parts.append("| ------- | ---- | ------ |")

        for vehicle in sorted(self.index_entries, key=lambda x: x['name']):
            name = vehicle['name']
            vtype = vehicle['type']
            source = vehicle['source']
            path = vehicle['path']
            parts.append(f"| [{name}]({path}) | {vtype} | {source} |")

        parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

"""Index collector for generating AI-optimized reference indexes."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


class IndexCollector:
    """Collects and aggregates index data from all extractors to generate optimized indexes."""

    def __init__(self):
        self.entries = defaultdict(list)
        self.keywords = defaultdict(lambda: defaultdict(list))

    def add_entries(self, category: str, entries: list) -> None:
        """Add entries from an extractor to the collector."""
        for entry in entries:
            entry['category'] = category
            self.entries[category].append(entry)
            self._extract_keywords(category, entry)

    def _extract_keywords(self, category: str, entry: dict) -> None:
        """Extract searchable keywords from an entry."""
        name = entry.get('name', '')
        path = entry.get('path', '')

        # Damage types
        for dmg_type in entry.get('damage_types', []):
            self.keywords[dmg_type.lower()][category].append({'name': name, 'path': path})

        # Conditions
        for condition in entry.get('conditions', []):
            self.keywords[condition.lower()][category].append({'name': name, 'path': path})

        # Creature types
        if category == 'creatures':
            ctype = entry.get('type', '')
            if isinstance(ctype, dict):
                ctype = ctype.get('type', '')
            if ctype:
                self.keywords[ctype.lower()][category].append({'name': name, 'path': path})

            # Movement types
            for move_type in entry.get('speed_types', []):
                self.keywords[move_type.lower()][category].append({'name': name, 'path': path})

            # Immunities/resistances
            for immunity in entry.get('immunities', []):
                kw = f"{immunity.lower()}-immune"
                self.keywords[kw][category].append({'name': name, 'path': path})

        # Spell schools
        if category == 'spells':
            school = entry.get('school', '').lower()
            if school:
                self.keywords[school][category].append({'name': name, 'path': path})

        # Item rarity
        if category == 'items':
            rarity = entry.get('rarity', '').lower()
            if rarity:
                self.keywords[rarity][category].append({'name': name, 'path': path})

    def generate_master_json(self, output_path: Path) -> None:
        """Generate the master JSON index file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Flatten all entries
        all_entries = []
        by_type = defaultdict(list)

        for category, entries in self.entries.items():
            for entry in entries:
                # Create a clean entry for the index
                clean_entry = {
                    'name': entry.get('name', ''),
                    'type': category,
                    'path': f"reference/{category}/{entry.get('path', '')}",
                }

                # Add category-specific fields
                if category == 'spells':
                    clean_entry['level'] = entry.get('level', 0)
                    clean_entry['school'] = entry.get('school', '')
                    clean_entry['casting_time'] = entry.get('casting_time', '')
                    clean_entry['range'] = entry.get('range', '')
                elif category == 'creatures':
                    clean_entry['cr'] = entry.get('cr', '0')
                    clean_entry['creature_type'] = entry.get('type', '')
                    clean_entry['size'] = entry.get('size', '')
                    clean_entry['hp'] = entry.get('hp', '')
                    clean_entry['ac'] = entry.get('ac', '')
                elif category == 'items':
                    clean_entry['rarity'] = entry.get('rarity', '')
                    clean_entry['item_type'] = entry.get('item_type', '')
                    clean_entry['attunement'] = entry.get('attunement', False)
                elif category == 'equipment':
                    clean_entry['equipment_type'] = entry.get('type', '')
                    clean_entry['cost'] = entry.get('cost', '')
                    clean_entry['damage'] = entry.get('damage', '')

                all_entries.append(clean_entry)
                by_type[category].append(entry.get('name', ''))

        index_data = {
            'total_entries': len(all_entries),
            'entries': sorted(all_entries, key=lambda x: x['name'].lower()),
            'by_type': {k: sorted(v) for k, v in by_type.items()},
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)

        print(f"  Master index: {len(all_entries)} entries")

    def generate_quick_references(self, reference_dir: Path) -> None:
        """Generate quick-reference.md files for each category."""
        generators = {
            'spells': self._generate_spell_quick_ref,
            'creatures': self._generate_creature_quick_ref,
            'items': self._generate_item_quick_ref,
            'equipment': self._generate_equipment_quick_ref,
        }

        for category, generator in generators.items():
            if category in self.entries:
                output_path = reference_dir / category / 'quick-reference.md'
                generator(output_path)

    def _generate_spell_quick_ref(self, output_path: Path) -> None:
        """Generate spell quick reference."""
        entries = self.entries.get('spells', [])
        if not entries:
            return

        parts = ["# Spell Quick Reference", ""]
        parts.append(f"**Total:** {len(entries)} spells")
        parts.append("")
        parts.append("| Spell | Lvl | School | Time | Range |")
        parts.append("| ----- | --- | ------ | ---- | ----- |")

        for entry in sorted(entries, key=lambda x: (x.get('level', 0), x['name'])):
            name = entry['name']
            level = entry.get('level', 0)
            school = entry.get('school', '')[:3]
            time = entry.get('casting_time', '')[:10]
            spell_range = entry.get('range', '')[:15]
            path = entry.get('path', '')
            parts.append(f"| [{name}]({path}) | {level} | {school} | {time} | {spell_range} |")

        parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        print(f"  Spell quick-ref: {len(entries)} entries")

    def _generate_creature_quick_ref(self, output_path: Path) -> None:
        """Generate creature quick reference."""
        entries = self.entries.get('creatures', [])
        if not entries:
            return

        parts = ["# Creature Quick Reference", ""]
        parts.append(f"**Total:** {len(entries)} creatures")
        parts.append("")
        parts.append("| Creature | CR | Type | Size | HP | AC |")
        parts.append("| -------- | -- | ---- | ---- | -- | -- |")

        def cr_sort_key(cr):
            if isinstance(cr, str):
                if '/' in cr:
                    num, den = cr.split('/')
                    return float(num) / float(den)
                try:
                    return float(cr)
                except ValueError:
                    return 0
            return float(cr)

        for entry in sorted(entries, key=lambda x: (cr_sort_key(x.get('cr', '0')), x['name'])):
            name = entry['name']
            cr = entry.get('cr', '0')
            ctype = entry.get('type', '')
            if isinstance(ctype, dict):
                ctype = ctype.get('type', '')
            ctype = str(ctype)[:10] if ctype else '-'
            size = str(entry.get('size', ''))[:1] if entry.get('size') else '-'
            hp = entry.get('hp', '-')
            ac = entry.get('ac', '-')
            path = entry.get('path', '')
            parts.append(f"| [{name}]({path}) | {cr} | {ctype} | {size} | {hp} | {ac} |")

        parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        print(f"  Creature quick-ref: {len(entries)} entries")

    def _generate_item_quick_ref(self, output_path: Path) -> None:
        """Generate item quick reference."""
        entries = self.entries.get('items', [])
        if not entries:
            return

        parts = ["# Magic Item Quick Reference", ""]
        parts.append(f"**Total:** {len(entries)} items")
        parts.append("")
        parts.append("| Item | Rarity | Type | Attune |")
        parts.append("| ---- | ------ | ---- | ------ |")

        rarity_order = {'common': 0, 'uncommon': 1, 'rare': 2, 'very rare': 3, 'legendary': 4, 'artifact': 5}

        for entry in sorted(entries, key=lambda x: (rarity_order.get(x.get('rarity', '').lower(), 6), x['name'])):
            name = entry['name']
            rarity = entry.get('rarity', '-')
            itype = entry.get('item_type', '-')[:15]
            attune = 'Yes' if entry.get('attunement') else '-'
            path = entry.get('path', '')
            parts.append(f"| [{name}]({path}) | {rarity} | {itype} | {attune} |")

        parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        print(f"  Item quick-ref: {len(entries)} entries")

    def _generate_equipment_quick_ref(self, output_path: Path) -> None:
        """Generate equipment quick reference."""
        entries = self.entries.get('equipment', [])
        if not entries:
            return

        parts = ["# Equipment Quick Reference", ""]
        parts.append(f"**Total:** {len(entries)} items")
        parts.append("")
        parts.append("| Item | Type | Cost | Damage/AC |")
        parts.append("| ---- | ---- | ---- | --------- |")

        for entry in sorted(entries, key=lambda x: x['name']):
            name = entry['name']
            etype = entry.get('type', '-')[:15]
            cost = entry.get('cost', '-')
            damage = entry.get('damage', entry.get('ac', '-'))
            path = entry.get('path', '')
            parts.append(f"| [{name}]({path}) | {etype} | {cost} | {damage} |")

        parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        print(f"  Equipment quick-ref: {len(entries)} entries")

    def generate_cross_references(self, output_dir: Path) -> None:
        """Generate cross-reference tables."""
        output_dir.mkdir(parents=True, exist_ok=True)

        self._generate_creatures_by_cr(output_dir / 'creatures-by-cr.md')
        self._generate_creatures_by_type(output_dir / 'creatures-by-type.md')
        self._generate_spells_by_level(output_dir / 'spells-by-level.md')
        self._generate_spells_by_school(output_dir / 'spells-by-school.md')
        self._generate_items_by_rarity(output_dir / 'items-by-rarity.md')
        self._generate_items_by_type(output_dir / 'items-by-type.md')

    def _generate_creatures_by_cr(self, output_path: Path) -> None:
        """Generate creatures grouped by CR."""
        entries = self.entries.get('creatures', [])
        if not entries:
            return

        cr_groups = defaultdict(list)
        for entry in entries:
            cr = entry.get('cr', '0')
            cr_groups[cr].append(entry)

        parts = ["# Creatures by Challenge Rating", ""]

        def cr_sort_key(cr):
            if '/' in str(cr):
                num, den = str(cr).split('/')
                return float(num) / float(den)
            try:
                return float(cr)
            except ValueError:
                return 0

        for cr in sorted(cr_groups.keys(), key=cr_sort_key):
            creatures = cr_groups[cr]
            parts.append(f"## CR {cr} ({len(creatures)} creatures)")
            parts.append("")
            for c in sorted(creatures, key=lambda x: x['name']):
                path = c.get('path', '')
                parts.append(f"- [{c['name']}](reference/creatures/{path})")
            parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

    def _generate_creatures_by_type(self, output_path: Path) -> None:
        """Generate creatures grouped by type."""
        entries = self.entries.get('creatures', [])
        if not entries:
            return

        type_groups = defaultdict(list)
        for entry in entries:
            ctype = entry.get('type', 'Unknown')
            if isinstance(ctype, dict):
                ctype = ctype.get('type', 'Unknown')
            type_groups[str(ctype)].append(entry)

        parts = ["# Creatures by Type", ""]

        for ctype in sorted(type_groups.keys()):
            creatures = type_groups[ctype]
            parts.append(f"## {str(ctype).title()} ({len(creatures)} creatures)")
            parts.append("")
            for c in sorted(creatures, key=lambda x: x['name']):
                path = c.get('path', '')
                cr = c.get('cr', '?')
                parts.append(f"- [{c['name']}](reference/creatures/{path}) (CR {cr})")
            parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

    def _generate_spells_by_level(self, output_path: Path) -> None:
        """Generate spells grouped by level."""
        entries = self.entries.get('spells', [])
        if not entries:
            return

        level_groups = defaultdict(list)
        for entry in entries:
            level = entry.get('level', 0)
            level_groups[level].append(entry)

        parts = ["# Spells by Level", ""]

        level_names = {0: 'Cantrips', 1: '1st Level', 2: '2nd Level', 3: '3rd Level',
                       4: '4th Level', 5: '5th Level', 6: '6th Level',
                       7: '7th Level', 8: '8th Level', 9: '9th Level'}

        for level in sorted(level_groups.keys()):
            spells = level_groups[level]
            level_name = level_names.get(level, f'{level}th Level')
            parts.append(f"## {level_name} ({len(spells)} spells)")
            parts.append("")
            for s in sorted(spells, key=lambda x: x['name']):
                path = s.get('path', '')
                school = s.get('school', '')[:3]
                parts.append(f"- [{s['name']}](reference/spells/{path}) [{school}]")
            parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

    def _generate_spells_by_school(self, output_path: Path) -> None:
        """Generate spells grouped by school."""
        entries = self.entries.get('spells', [])
        if not entries:
            return

        school_groups = defaultdict(list)
        for entry in entries:
            school = entry.get('school', 'Unknown')
            school_groups[school].append(entry)

        parts = ["# Spells by School", ""]

        for school in sorted(school_groups.keys()):
            spells = school_groups[school]
            parts.append(f"## {school} ({len(spells)} spells)")
            parts.append("")
            for s in sorted(spells, key=lambda x: (x.get('level', 0), x['name'])):
                path = s.get('path', '')
                level = s.get('level', 0)
                level_str = 'C' if level == 0 else str(level)
                parts.append(f"- [{s['name']}](reference/spells/{path}) (Lvl {level_str})")
            parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

    def _generate_items_by_rarity(self, output_path: Path) -> None:
        """Generate items grouped by rarity."""
        entries = self.entries.get('items', [])
        if not entries:
            return

        rarity_groups = defaultdict(list)
        for entry in entries:
            rarity = entry.get('rarity', 'Unknown')
            rarity_groups[rarity].append(entry)

        parts = ["# Magic Items by Rarity", ""]

        rarity_order = ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary', 'Artifact']

        for rarity in rarity_order:
            if rarity not in rarity_groups:
                continue
            items = rarity_groups[rarity]
            parts.append(f"## {rarity} ({len(items)} items)")
            parts.append("")
            for i in sorted(items, key=lambda x: x['name']):
                path = i.get('path', '')
                parts.append(f"- [{i['name']}](reference/items/{path})")
            parts.append("")

        # Handle any remaining rarities
        for rarity in sorted(rarity_groups.keys()):
            if rarity in rarity_order:
                continue
            items = rarity_groups[rarity]
            parts.append(f"## {rarity} ({len(items)} items)")
            parts.append("")
            for i in sorted(items, key=lambda x: x['name']):
                path = i.get('path', '')
                parts.append(f"- [{i['name']}](reference/items/{path})")
            parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

    def _generate_items_by_type(self, output_path: Path) -> None:
        """Generate items grouped by type."""
        entries = self.entries.get('items', [])
        if not entries:
            return

        type_groups = defaultdict(list)
        for entry in entries:
            itype = entry.get('item_type', 'Other')
            type_groups[itype].append(entry)

        parts = ["# Magic Items by Type", ""]

        for itype in sorted(type_groups.keys()):
            items = type_groups[itype]
            parts.append(f"## {itype} ({len(items)} items)")
            parts.append("")
            for i in sorted(items, key=lambda x: x['name']):
                path = i.get('path', '')
                rarity = i.get('rarity', '')
                parts.append(f"- [{i['name']}](reference/items/{path}) ({rarity})")
            parts.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

    def generate_keyword_index(self, output_path: Path) -> None:
        """Generate the keyword index JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert defaultdict to regular dict for JSON serialization
        keyword_data = {}
        for keyword, categories in sorted(self.keywords.items()):
            if not any(categories.values()):
                continue
            keyword_data[keyword] = {}
            for category, entries in categories.items():
                if entries:
                    # Deduplicate and sort
                    unique_entries = {e['name']: e for e in entries}
                    keyword_data[keyword][category] = sorted(
                        [{'name': e['name'], 'path': f"reference/{category}/{e['path']}"} for e in unique_entries.values()],
                        key=lambda x: x['name']
                    )

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(keyword_data, f, indent=2)

        print(f"  Keyword index: {len(keyword_data)} keywords")

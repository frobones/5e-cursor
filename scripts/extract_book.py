#!/usr/bin/env python3
"""
5etools JSON to Markdown Extractor

Extracts D&D content from 5etools JSON format and converts to readable markdown.
Supports books, adventures, and bestiaries.
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


class TagConverter:
    """Converts 5etools tags to markdown format."""

    # Pattern to match 5etools tags like {@spell fireball}, {@creature dragon|MM}
    TAG_PATTERN = re.compile(r'\{@(\w+)\s+([^}]+)\}')

    @classmethod
    def convert_tags(cls, text: str) -> str:
        """Convert all 5etools tags in text to markdown."""
        if not isinstance(text, str):
            return str(text)

        def replace_tag(match):
            tag_type = match.group(1)
            content = match.group(2)
            return cls._convert_single_tag(tag_type, content)

        # Keep converting until no more tags (handles nested tags)
        result = text
        max_iterations = 10
        for _ in range(max_iterations):
            new_result = cls.TAG_PATTERN.sub(replace_tag, result)
            if new_result == result:
                break
            result = new_result

        return result

    @classmethod
    def _convert_single_tag(cls, tag_type: str, content: str) -> str:
        """Convert a single tag to markdown."""
        # Split content by | to get the display text vs reference
        parts = content.split('|')
        display_text = parts[0]

        # Handle different tag types
        tag_handlers = {
            'b': lambda p: f"**{p[0]}**",
            'bold': lambda p: f"**{p[0]}**",
            'i': lambda p: f"*{p[0]}*",
            'italic': lambda p: f"*{p[0]}*",
            'spell': lambda p: f"*{p[0]}*",
            'creature': lambda p: f"**{p[0]}**",
            'item': lambda p: f"*{p[0]}*",
            'condition': lambda p: f"**{p[0]}**",
            'skill': lambda p: f"**{p[0]}**",
            'action': lambda p: f"**{p[0]}**",
            'dice': lambda p: f"`{p[0]}`",
            'damage': lambda p: f"`{p[0]}`",
            'hit': lambda p: f"+{p[0]}",
            'dc': lambda p: f"DC {p[0]}",
            'atk': lambda p: cls._format_attack(p[0]),
            'h': lambda p: "Hit:",
            'recharge': lambda p: cls._format_recharge(p),
            'book': lambda p: cls._format_book_ref(p),
            'adventure': lambda p: cls._format_adventure_ref(p),
            'feat': lambda p: f"**{p[0]}**",
            'background': lambda p: f"**{p[0]}**",
            'race': lambda p: f"**{p[0]}**",
            'class': lambda p: f"**{p[0]}**",
            'vehicle': lambda p: f"*{p[0]}*",
            'object': lambda p: f"*{p[0]}*",
            'hazard': lambda p: f"*{p[0]}*",
            'variantrule': lambda p: f"**{p[0]}**",
            'sense': lambda p: f"**{p[0]}**",
            'link': lambda p: cls._format_link(p),
            'tip': lambda p: p[0] if p else "",
            'note': lambda p: f"*{p[0]}*" if p else "",
            'filter': lambda p: p[0] if p else "",
            'table': lambda p: p[0] if p else "",
            'classFeature': lambda p: f"**{p[0]}**",
            'subclassFeature': lambda p: f"**{p[0]}**",
            'optfeature': lambda p: f"**{p[0]}**",
            'area': lambda p: f"**Area {p[0]}**" if p else "",
            'scaledice': lambda p: cls._format_scaledice(p),
            'scaledamage': lambda p: cls._format_scaledice(p),
            'chance': lambda p: f"{p[0]}%",
            'quickref': lambda p: p[0] if p else "",
            'card': lambda p: p[0] if p else "",
            'deity': lambda p: f"**{p[0]}**",
            'language': lambda p: f"*{p[0]}*",
            'reward': lambda p: f"**{p[0]}**",
            'psionic': lambda p: f"*{p[0]}*",
            'boon': lambda p: f"**{p[0]}**",
            'charoption': lambda p: f"**{p[0]}**",
            'cult': lambda p: f"**{p[0]}**",
            'trap': lambda p: f"*{p[0]}*",
            'disease': lambda p: f"*{p[0]}*",
            'status': lambda p: f"**{p[0]}**",
            'legroup': lambda p: p[0] if p else "",
            'homebrew': lambda p: p[0] if p else "",
        }

        handler = tag_handlers.get(tag_type.lower())
        if handler:
            return handler(parts)
        else:
            # Unknown tag, just return the display text
            return display_text

    @staticmethod
    def _format_attack(attack_type: str) -> str:
        """Format attack type abbreviations."""
        attack_types = {
            'mw': 'Melee Weapon Attack:',
            'rw': 'Ranged Weapon Attack:',
            'ms': 'Melee Spell Attack:',
            'rs': 'Ranged Spell Attack:',
            'mw,rw': 'Melee or Ranged Weapon Attack:',
        }
        return attack_types.get(attack_type.lower(), f'{attack_type} Attack:')

    @staticmethod
    def _format_recharge(parts: list) -> str:
        """Format recharge abilities."""
        if not parts or not parts[0]:
            return "(Recharge 6)"
        val = parts[0]
        if val == '6':
            return "(Recharge 6)"
        return f"(Recharge {val}-6)"

    @staticmethod
    def _format_book_ref(parts: list) -> str:
        """Format book references."""
        if len(parts) >= 1:
            return f"*{parts[0]}*"
        return ""

    @staticmethod
    def _format_adventure_ref(parts: list) -> str:
        """Format adventure references."""
        if len(parts) >= 1:
            return f"*{parts[0]}*"
        return ""

    @staticmethod
    def _format_link(parts: list) -> str:
        """Format links."""
        if len(parts) >= 2:
            return f"[{parts[0]}]({parts[1]})"
        elif len(parts) == 1:
            return parts[0]
        return ""

    @staticmethod
    def _format_scaledice(parts: list) -> str:
        """Format scaled dice notation."""
        if parts:
            # Extract just the dice notation
            return f"`{parts[0]}`"
        return ""


class EntryConverter:
    """Converts 5etools entry objects to markdown."""

    def __init__(self, heading_level: int = 1):
        self.heading_level = heading_level
        self.tag_converter = TagConverter()

    def convert(self, entry: Any, depth: int = 0) -> str:
        """Convert an entry to markdown."""
        if entry is None:
            return ""

        if isinstance(entry, str):
            return self.tag_converter.convert_tags(entry)

        if isinstance(entry, list):
            parts = []
            for item in entry:
                converted = self.convert(item, depth)
                if converted:
                    parts.append(converted)
            return "\n\n".join(parts)

        if isinstance(entry, dict):
            return self._convert_dict_entry(entry, depth)

        return str(entry)

    def _convert_dict_entry(self, entry: dict, depth: int) -> str:
        """Convert a dictionary entry to markdown."""
        entry_type = entry.get('type', '')

        converters = {
            'section': self._convert_section,
            'entries': self._convert_entries,
            'entry': self._convert_entry,
            'list': self._convert_list,
            'item': self._convert_item,
            'table': self._convert_table,
            'inset': self._convert_inset,
            'insetReadaloud': self._convert_inset_readaloud,
            'quote': self._convert_quote,
            'image': self._convert_image,
            'abilityDc': self._convert_ability_dc,
            'abilityAttackMod': self._convert_ability_attack,
            'options': self._convert_options,
            'optfeature': self._convert_optfeature,
            'refClassFeature': self._convert_ref_class_feature,
            'refSubclassFeature': self._convert_ref_subclass_feature,
            'refOptionalfeature': self._convert_ref_optional_feature,
            'statblock': self._convert_statblock,
            'statblockInline': self._convert_statblock,
            'hr': lambda e, d: "---",
            'cell': self._convert_cell,
            'flowchart': self._convert_flowchart,
            'gallery': self._convert_gallery,
            'inline': self._convert_inline,
            'inlineBlock': self._convert_inline,
            'bonus': self._convert_bonus,
            'bonusSpeed': self._convert_bonus,
            'dice': self._convert_dice,
            'abilityGeneric': self._convert_ability_generic,
        }

        converter = converters.get(entry_type)
        if converter:
            return converter(entry, depth)

        # If we have entries, process them
        if 'entries' in entry:
            name = entry.get('name', '')
            content = self.convert(entry['entries'], depth)
            if name:
                heading = '#' * min(self.heading_level + depth, 6)
                return f"{heading} {self.tag_converter.convert_tags(name)}\n\n{content}"
            return content

        # Fallback: just convert to string representation
        return ""

    def _convert_section(self, entry: dict, depth: int) -> str:
        """Convert a section entry."""
        name = entry.get('name', '')
        entries = entry.get('entries', [])

        parts = []
        if name:
            heading = '#' * min(self.heading_level + depth, 6)
            parts.append(f"{heading} {self.tag_converter.convert_tags(name)}")

        content = self.convert(entries, depth + 1)
        if content:
            parts.append(content)

        return "\n\n".join(parts)

    def _convert_entries(self, entry: dict, depth: int) -> str:
        """Convert an entries block."""
        name = entry.get('name', '')
        entries = entry.get('entries', [])

        parts = []
        if name:
            heading = '#' * min(self.heading_level + depth + 1, 6)
            parts.append(f"{heading} {self.tag_converter.convert_tags(name)}")

        content = self.convert(entries, depth + 1)
        if content:
            parts.append(content)

        return "\n\n".join(parts)

    def _convert_entry(self, entry: dict, depth: int) -> str:
        """Convert a single entry."""
        return self._convert_entries(entry, depth)

    def _convert_list(self, entry: dict, depth: int) -> str:
        """Convert a list entry."""
        items = entry.get('items', [])
        style = entry.get('style', '')

        parts = []
        for item in items:
            if isinstance(item, str):
                parts.append(f"- {self.tag_converter.convert_tags(item)}")
            elif isinstance(item, dict):
                item_type = item.get('type', '')
                if item_type == 'item':
                    name = item.get('name', '')
                    item_entry = item.get('entry', '') or item.get('entries', '')
                    if isinstance(item_entry, list):
                        item_entry = self.convert(item_entry, depth)
                    else:
                        item_entry = self.tag_converter.convert_tags(item_entry)

                    if name:
                        parts.append(f"- **{self.tag_converter.convert_tags(name)}**: {item_entry}")
                    else:
                        parts.append(f"- {item_entry}")
                else:
                    converted = self.convert(item, depth)
                    if converted:
                        parts.append(f"- {converted}")

        return "\n".join(parts)

    def _convert_item(self, entry: dict, depth: int) -> str:
        """Convert an item entry."""
        name = entry.get('name', '')
        item_entry = entry.get('entry', '') or entry.get('entries', '')

        if isinstance(item_entry, list):
            item_entry = self.convert(item_entry, depth)
        else:
            item_entry = self.tag_converter.convert_tags(item_entry)

        if name:
            return f"**{self.tag_converter.convert_tags(name)}**: {item_entry}"
        return item_entry

    def _convert_table(self, entry: dict, depth: int) -> str:
        """Convert a table entry."""
        caption = entry.get('caption', '')
        col_labels = entry.get('colLabels', [])
        rows = entry.get('rows', [])

        parts = []

        if caption:
            parts.append(f"**{self.tag_converter.convert_tags(caption)}**\n")

        if col_labels:
            # Header row
            headers = [self.tag_converter.convert_tags(str(label)) for label in col_labels]
            parts.append("| " + " | ".join(headers) + " |")
            # Separator
            parts.append("|" + "|".join(["---"] * len(col_labels)) + "|")

        # Data rows
        for row in rows:
            if isinstance(row, list):
                cells = []
                for cell in row:
                    if isinstance(cell, dict):
                        cell_text = self._convert_cell(cell, depth)
                    else:
                        cell_text = self.tag_converter.convert_tags(str(cell))
                    # Escape pipe characters in cells
                    cell_text = cell_text.replace("|", "\\|")
                    cells.append(cell_text)
                parts.append("| " + " | ".join(cells) + " |")
            elif isinstance(row, dict):
                # Row might be a special row type
                row_type = row.get('type', '')
                if row_type == 'row':
                    row_data = row.get('row', [])
                    cells = [self.tag_converter.convert_tags(str(cell)) for cell in row_data]
                    parts.append("| " + " | ".join(cells) + " |")

        return "\n".join(parts)

    def _convert_cell(self, entry: dict, depth: int) -> str:
        """Convert a table cell."""
        if 'roll' in entry:
            roll = entry['roll']
            if isinstance(roll, dict):
                if 'exact' in roll:
                    return str(roll['exact'])
                elif 'min' in roll and 'max' in roll:
                    return f"{roll['min']}-{roll['max']}"
        if 'entry' in entry:
            return self.convert(entry['entry'], depth)
        if 'entries' in entry:
            return self.convert(entry['entries'], depth)
        return ""

    def _convert_inset(self, entry: dict, depth: int) -> str:
        """Convert an inset (sidebar) entry."""
        name = entry.get('name', '')
        entries = entry.get('entries', [])

        parts = []
        if name:
            parts.append(f"> ### {self.tag_converter.convert_tags(name)}")
        parts.append(">")

        content = self.convert(entries, depth)
        # Add blockquote prefix to each line
        for line in content.split('\n'):
            parts.append(f"> {line}")

        return "\n".join(parts)

    def _convert_inset_readaloud(self, entry: dict, depth: int) -> str:
        """Convert a read-aloud text box."""
        entries = entry.get('entries', [])

        parts = ["> *Read-aloud:*", ">"]
        content = self.convert(entries, depth)
        for line in content.split('\n'):
            parts.append(f"> *{line}*")

        return "\n".join(parts)

    def _convert_quote(self, entry: dict, depth: int) -> str:
        """Convert a quote entry."""
        entries = entry.get('entries', [])
        by = entry.get('by', '')

        parts = []
        content = self.convert(entries, depth)
        for line in content.split('\n'):
            parts.append(f"> {line}")

        if by:
            parts.append(f">\n> — *{self.tag_converter.convert_tags(by)}*")

        return "\n".join(parts)

    def _convert_image(self, entry: dict, depth: int) -> str:
        """Convert an image reference."""
        title = entry.get('title', '')
        credit = entry.get('credit', '')
        href = entry.get('href', {})

        path = href.get('path', '') if isinstance(href, dict) else ''

        parts = []
        if title:
            parts.append(f"*[Image: {self.tag_converter.convert_tags(title)}]*")
        else:
            parts.append("*[Image]*")

        if credit:
            parts.append(f"*Art by {credit}*")

        return "\n".join(parts)

    def _convert_ability_dc(self, entry: dict, depth: int) -> str:
        """Convert ability DC calculation."""
        name = entry.get('name', 'Ability')
        attributes = entry.get('attributes', [])
        attr_str = '/'.join(attributes) if attributes else 'ability'
        return f"**{name}** = 8 + your proficiency bonus + your {attr_str} modifier"

    def _convert_ability_attack(self, entry: dict, depth: int) -> str:
        """Convert ability attack modifier calculation."""
        name = entry.get('name', 'Attack')
        attributes = entry.get('attributes', [])
        attr_str = '/'.join(attributes) if attributes else 'ability'
        return f"**{name}** = your proficiency bonus + your {attr_str} modifier"

    def _convert_options(self, entry: dict, depth: int) -> str:
        """Convert options block."""
        entries = entry.get('entries', [])
        return self.convert(entries, depth)

    def _convert_optfeature(self, entry: dict, depth: int) -> str:
        """Convert optional feature."""
        name = entry.get('name', '')
        entries = entry.get('entries', [])

        parts = []
        if name:
            parts.append(f"**{self.tag_converter.convert_tags(name)}**")

        content = self.convert(entries, depth)
        if content:
            parts.append(content)

        return "\n\n".join(parts)

    def _convert_ref_class_feature(self, entry: dict, depth: int) -> str:
        """Convert class feature reference."""
        class_feature = entry.get('classFeature', '')
        return f"*See: {class_feature}*"

    def _convert_ref_subclass_feature(self, entry: dict, depth: int) -> str:
        """Convert subclass feature reference."""
        subclass_feature = entry.get('subclassFeature', '')
        return f"*See: {subclass_feature}*"

    def _convert_ref_optional_feature(self, entry: dict, depth: int) -> str:
        """Convert optional feature reference."""
        opt_feature = entry.get('optionalfeature', '')
        return f"*See: {opt_feature}*"

    def _convert_statblock(self, entry: dict, depth: int) -> str:
        """Convert a statblock reference."""
        tag = entry.get('tag', '')
        name = entry.get('name', '')
        source = entry.get('source', '')
        return f"*[Statblock: {name}]*"

    def _convert_flowchart(self, entry: dict, depth: int) -> str:
        """Convert flowchart."""
        blocks = entry.get('blocks', [])
        parts = []
        for block in blocks:
            name = block.get('name', '')
            entries = block.get('entries', [])
            if name:
                parts.append(f"**{self.tag_converter.convert_tags(name)}**")
            content = self.convert(entries, depth)
            if content:
                parts.append(content)
        return "\n\n".join(parts)

    def _convert_gallery(self, entry: dict, depth: int) -> str:
        """Convert gallery."""
        images = entry.get('images', [])
        parts = []
        for img in images:
            parts.append(self._convert_image(img, depth))
        return "\n\n".join(parts)

    def _convert_inline(self, entry: dict, depth: int) -> str:
        """Convert inline entries."""
        entries = entry.get('entries', [])
        return " ".join([self.convert(e, depth) for e in entries])

    def _convert_bonus(self, entry: dict, depth: int) -> str:
        """Convert bonus value."""
        value = entry.get('value', 0)
        return f"+{value}" if value >= 0 else str(value)

    def _convert_dice(self, entry: dict, depth: int) -> str:
        """Convert dice entry."""
        to_roll = entry.get('toRoll', [])
        if to_roll:
            dice_parts = []
            for dice in to_roll:
                if isinstance(dice, dict):
                    num = dice.get('number', 1)
                    faces = dice.get('faces', 6)
                    dice_parts.append(f"{num}d{faces}")
            return "`" + " + ".join(dice_parts) + "`"
        return ""

    def _convert_ability_generic(self, entry: dict, depth: int) -> str:
        """Convert generic ability description."""
        text = entry.get('text', '')
        return self.tag_converter.convert_tags(text)


class BookExtractor:
    """Extracts content from 5etools book JSON files."""

    def __init__(self, source_path: str, output_dir: str):
        self.source_path = Path(source_path)
        self.output_dir = Path(output_dir)
        self.converter = EntryConverter(heading_level=1)

    def extract(self) -> None:
        """Extract the book content to markdown files."""
        with open(self.source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different data structures
        if 'data' in data:
            sections = data['data']
            self._extract_book_sections(sections)
        elif 'monster' in data:
            monsters = data['monster']
            self._extract_bestiary(monsters)
        else:
            print(f"Unknown data structure in {self.source_path}")

    def _extract_book_sections(self, sections: list) -> None:
        """Extract book sections to individual markdown files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for idx, section in enumerate(sections):
            if not isinstance(section, dict):
                continue

            name = section.get('name', f'Section {idx}')
            # Create safe filename
            safe_name = self._make_safe_filename(name)
            filename = f"{idx:02d}-{safe_name}.md"

            content = self._section_to_markdown(section)

            output_path = self.output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  Created: {filename}")

    def _extract_bestiary(self, monsters: list) -> None:
        """Extract bestiary to markdown files."""
        creatures_dir = self.output_dir / 'creatures'
        creatures_dir.mkdir(parents=True, exist_ok=True)

        # Also create an index file
        index_entries = []

        for monster in monsters:
            if not isinstance(monster, dict):
                continue

            name = monster.get('name', 'Unknown')
            safe_name = self._make_safe_filename(name)
            filename = f"{safe_name}.md"

            content = self._monster_to_markdown(monster)

            output_path = creatures_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            cr = monster.get('cr', '?')
            if isinstance(cr, dict):
                cr = cr.get('cr', '?')
            index_entries.append((name, cr, filename))

        # Create index
        index_content = self._create_bestiary_index(index_entries)
        with open(self.output_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write(index_content)

        print(f"  Created: {len(monsters)} creature files + index.md")

    def _section_to_markdown(self, section: dict) -> str:
        """Convert a section to markdown."""
        name = section.get('name', '')
        page = section.get('page', '')

        parts = []

        # Title
        if name:
            parts.append(f"# {TagConverter.convert_tags(name)}")
            if page:
                parts.append(f"*Page {page}*")
            parts.append("")

        # Convert entries
        entries = section.get('entries', [])
        content = self.converter.convert(entries, 0)
        if content:
            parts.append(content)

        return "\n".join(parts)

    def _monster_to_markdown(self, monster: dict) -> str:
        """Convert a monster stat block to markdown."""
        parts = []

        name = monster.get('name', 'Unknown')
        parts.append(f"# {name}")
        parts.append("")

        # Basic info
        size_map = {'T': 'Tiny', 'S': 'Small', 'M': 'Medium', 'L': 'Large', 'H': 'Huge', 'G': 'Gargantuan'}
        sizes = monster.get('size', ['M'])
        size = ', '.join([size_map.get(s, s) for s in sizes])

        monster_type = monster.get('type', '')
        if isinstance(monster_type, dict):
            monster_type = monster_type.get('type', '')

        alignment = monster.get('alignment', [])
        if isinstance(alignment, list):
            align_map = {
                'L': 'Lawful', 'N': 'Neutral', 'C': 'Chaotic',
                'G': 'Good', 'E': 'Evil', 'U': 'Unaligned', 'A': 'Any'
            }
            alignment = ' '.join([align_map.get(a, a) for a in alignment])

        parts.append(f"*{size} {monster_type}, {alignment}*")
        parts.append("")

        # Combat stats
        parts.append("---")
        parts.append("")

        # AC
        ac = monster.get('ac', [])
        if ac:
            if isinstance(ac[0], dict):
                ac_val = ac[0].get('ac', 10)
                ac_from = ac[0].get('from', [])
                ac_str = f"**Armor Class** {ac_val}"
                if ac_from:
                    ac_str += f" ({', '.join(ac_from)})"
            else:
                ac_str = f"**Armor Class** {ac[0]}"
            parts.append(ac_str)

        # HP
        hp = monster.get('hp', {})
        if isinstance(hp, dict):
            avg = hp.get('average', 0)
            formula = hp.get('formula', '')
            parts.append(f"**Hit Points** {avg} ({formula})")

        # Speed
        speed = monster.get('speed', {})
        if speed:
            speed_parts = []
            for stype, sval in speed.items():
                if isinstance(sval, dict):
                    sval = sval.get('number', sval)
                if stype == 'walk':
                    speed_parts.append(f"{sval} ft.")
                elif sval:
                    speed_parts.append(f"{stype} {sval} ft.")
            parts.append(f"**Speed** {', '.join(speed_parts)}")

        parts.append("")
        parts.append("---")
        parts.append("")

        # Ability scores
        abilities = ['str', 'dex', 'con', 'int', 'wis', 'cha']
        scores = []
        for ability in abilities:
            score = monster.get(ability, 10)
            mod = (score - 10) // 2
            mod_str = f"+{mod}" if mod >= 0 else str(mod)
            scores.append(f"**{ability.upper()}** {score} ({mod_str})")
        parts.append(" | ".join(scores))
        parts.append("")
        parts.append("---")
        parts.append("")

        # Senses, Languages, CR
        senses = monster.get('senses', [])
        passive = monster.get('passive', 10)
        if senses:
            parts.append(f"**Senses** {', '.join(senses)}, passive Perception {passive}")
        else:
            parts.append(f"**Senses** passive Perception {passive}")

        languages = monster.get('languages', [])
        if languages:
            parts.append(f"**Languages** {', '.join(languages)}")
        else:
            parts.append("**Languages** —")

        cr = monster.get('cr', '0')
        if isinstance(cr, dict):
            cr = cr.get('cr', '0')
        parts.append(f"**Challenge** {cr}")

        parts.append("")
        parts.append("---")
        parts.append("")

        # Traits
        traits = monster.get('trait', [])
        for trait in traits:
            trait_name = trait.get('name', '')
            entries = trait.get('entries', [])
            content = self.converter.convert(entries, 0)
            parts.append(f"***{trait_name}.*** {content}")
            parts.append("")

        # Spellcasting
        spellcasting = monster.get('spellcasting', [])
        for sc in spellcasting:
            sc_name = sc.get('name', 'Spellcasting')
            header = sc.get('headerEntries', [])
            header_text = self.converter.convert(header, 0)
            parts.append(f"***{sc_name}.*** {header_text}")

            # Daily spells
            daily = sc.get('daily', {})
            for uses, spells in daily.items():
                uses_str = uses.replace('e', '/day each: ').replace('1', '1').replace('2', '2').replace('3', '3')
                if not uses_str.endswith(': '):
                    uses_str = f"{uses}/day: "
                parts.append(f"- {uses_str}{', '.join([TagConverter.convert_tags(s) for s in spells])}")

            # At will spells
            will = sc.get('will', [])
            if will:
                parts.append(f"- At will: {', '.join([TagConverter.convert_tags(s) for s in will])}")

            parts.append("")

        # Actions
        actions = monster.get('action', [])
        if actions:
            parts.append("## Actions")
            parts.append("")
            for action in actions:
                action_name = action.get('name', '')
                entries = action.get('entries', [])
                content = self.converter.convert(entries, 0)
                parts.append(f"***{action_name}.*** {content}")
                parts.append("")

        # Bonus Actions
        bonus = monster.get('bonus', [])
        if bonus:
            parts.append("## Bonus Actions")
            parts.append("")
            for ba in bonus:
                ba_name = ba.get('name', '')
                entries = ba.get('entries', [])
                content = self.converter.convert(entries, 0)
                parts.append(f"***{ba_name}.*** {content}")
                parts.append("")

        # Reactions
        reactions = monster.get('reaction', [])
        if reactions:
            parts.append("## Reactions")
            parts.append("")
            for reaction in reactions:
                r_name = reaction.get('name', '')
                entries = reaction.get('entries', [])
                content = self.converter.convert(entries, 0)
                parts.append(f"***{r_name}.*** {content}")
                parts.append("")

        # Legendary Actions
        legendary = monster.get('legendary', [])
        if legendary:
            parts.append("## Legendary Actions")
            parts.append("")
            legendary_header = monster.get('legendaryHeader', [])
            if legendary_header:
                parts.append(self.converter.convert(legendary_header, 0))
                parts.append("")
            for leg in legendary:
                l_name = leg.get('name', '')
                entries = leg.get('entries', [])
                content = self.converter.convert(entries, 0)
                parts.append(f"***{l_name}.*** {content}")
                parts.append("")

        return "\n".join(parts)

    def _create_bestiary_index(self, entries: list) -> str:
        """Create an index for the bestiary."""
        parts = ["# Creature Index", "", "| Creature | CR | File |", "|----------|----|----|"]

        # Sort by name
        entries.sort(key=lambda x: x[0])

        for name, cr, filename in entries:
            parts.append(f"| {name} | {cr} | [{filename}](creatures/{filename}) |")

        return "\n".join(parts)

    @staticmethod
    def _make_safe_filename(name: str) -> str:
        """Convert a name to a safe filename."""
        # Remove or replace problematic characters
        safe = name.lower()
        safe = re.sub(r'[^\w\s-]', '', safe)
        safe = re.sub(r'[-\s]+', '-', safe)
        return safe.strip('-')[:50]


def main():
    parser = argparse.ArgumentParser(description='Extract 5etools JSON to markdown')
    parser.add_argument('source', help='Path to source JSON file')
    parser.add_argument('output', help='Path to output directory')
    parser.add_argument('--type', choices=['book', 'adventure', 'bestiary'],
                        default='book', help='Type of content to extract')

    args = parser.parse_args()

    print(f"Extracting: {args.source}")
    print(f"Output to: {args.output}")

    extractor = BookExtractor(args.source, args.output)
    extractor.extract()

    print("Done!")


if __name__ == '__main__':
    main()

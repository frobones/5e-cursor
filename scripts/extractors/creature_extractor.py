"""Creature/monster extractor for 5etools data."""

import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_book import TagConverter, EntryConverter
from extractors.base import make_safe_filename


class CreatureExtractor:
    """Extracts creatures to individual markdown files."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract creatures from a source file. Returns count extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        monsters = data.get('monster', [])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for monster in monsters:
            if not isinstance(monster, dict):
                continue
            self._extract_creature(monster)
            count += 1

        return count

    def _extract_creature(self, monster: dict) -> None:
        """Extract a single creature to a markdown file."""
        name = monster.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        content = self._creature_to_markdown(monster)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to index with enriched data
        cr = monster.get('cr', '0')
        if isinstance(cr, dict):
            cr = cr.get('cr', '0')

        monster_type = monster.get('type', '')
        if isinstance(monster_type, dict):
            monster_type = monster_type.get('type', '')

        source = monster.get('source', '')

        # Size
        size_map = {'T': 'Tiny', 'S': 'Small', 'M': 'Medium', 'L': 'Large', 'H': 'Huge', 'G': 'Gargantuan'}
        sizes = monster.get('size', ['M'])
        size = size_map.get(sizes[0], sizes[0]) if sizes else 'Medium'

        # AC
        ac_data = monster.get('ac', [])
        if ac_data:
            if isinstance(ac_data[0], dict):
                ac = ac_data[0].get('ac', 10)
            else:
                ac = ac_data[0]
        else:
            ac = 10

        # HP
        hp_data = monster.get('hp', {})
        if isinstance(hp_data, dict):
            hp = hp_data.get('average', hp_data.get('special', 0))
        else:
            hp = hp_data

        # Speed types
        speed_data = monster.get('speed', {})
        speed_types = []
        if isinstance(speed_data, dict):
            for speed_type in ['walk', 'fly', 'swim', 'climb', 'burrow']:
                if speed_type in speed_data:
                    speed_types.append(speed_type)

        # Damage immunities
        immunities = []
        immune_data = monster.get('immune', [])
        for imm in immune_data:
            if isinstance(imm, str):
                immunities.append(imm)
            elif isinstance(imm, dict):
                for i in imm.get('immune', []):
                    if isinstance(i, str):
                        immunities.append(i)

        # Damage resistances
        resist_data = monster.get('resist', [])
        resistances = []
        for res in resist_data:
            if isinstance(res, str):
                resistances.append(res)
            elif isinstance(res, dict):
                for r in res.get('resist', []):
                    if isinstance(r, str):
                        resistances.append(r)

        self.index_entries.append({
            'name': name,
            'cr': cr,
            'type': monster_type,
            'source': source,
            'path': filename,
            'size': size,
            'ac': ac,
            'hp': hp,
            'speed_types': speed_types,
            'immunities': immunities,
            'resistances': resistances,
        })

    def _creature_to_markdown(self, monster: dict) -> str:
        """Convert a creature to markdown."""
        parts = []

        name = monster.get('name', 'Unknown')
        source = monster.get('source', '')
        page = monster.get('page', '')

        parts.append(f"# {name}")
        parts.append("")

        # Source info
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Basic info
        size_map = {
            'T': 'Tiny', 'S': 'Small', 'M': 'Medium',
            'L': 'Large', 'H': 'Huge', 'G': 'Gargantuan'
        }
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

        # Saving throws
        saves = monster.get('save', {})
        if saves:
            save_parts = [f"{k.capitalize()} {v}" for k, v in saves.items()]
            parts.append(f"**Saving Throws** {', '.join(save_parts)}")

        # Skills
        skills = monster.get('skill', {})
        if skills:
            skill_parts = [f"{k.capitalize()} {v}" for k, v in skills.items()]
            parts.append(f"**Skills** {', '.join(skill_parts)}")

        # Damage resistances/immunities/vulnerabilities
        resist = monster.get('resist', [])
        if resist:
            parts.append(f"**Damage Resistances** {self._format_damage_types(resist)}")

        immune = monster.get('immune', [])
        if immune:
            parts.append(f"**Damage Immunities** {self._format_damage_types(immune)}")

        vuln = monster.get('vulnerable', [])
        if vuln:
            parts.append(f"**Damage Vulnerabilities** {self._format_damage_types(vuln)}")

        # Condition immunities
        cond_immune = monster.get('conditionImmune', [])
        if cond_immune:
            cond_list = []
            for c in cond_immune:
                if isinstance(c, str):
                    cond_list.append(c)
                elif isinstance(c, dict):
                    # Complex entry with conditions and notes
                    sub_conds = c.get('conditionImmune', [])
                    note = c.get('note', '')
                    if sub_conds:
                        cond_str = ', '.join(sub_conds)
                        if note:
                            cond_str += f" {note}"
                        cond_list.append(cond_str)
            if cond_list:
                parts.append(f"**Condition Immunities** {', '.join(cond_list)}")

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

            daily = sc.get('daily', {})
            for uses, spells in daily.items():
                uses_str = uses.replace('e', '/day each: ')
                if not uses_str.endswith(': '):
                    uses_str = f"{uses}/day: "
                spell_list = ', '.join([TagConverter.convert_tags(s) for s in spells])
                parts.append(f"- {uses_str}{spell_list}")

            will = sc.get('will', [])
            if will:
                spell_list = ', '.join([TagConverter.convert_tags(s) for s in will])
                parts.append(f"- At will: {spell_list}")

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

        # Mythic Actions
        mythic = monster.get('mythic', [])
        if mythic:
            parts.append("## Mythic Actions")
            parts.append("")
            mythic_header = monster.get('mythicHeader', [])
            if mythic_header:
                parts.append(self.converter.convert(mythic_header, 0))
                parts.append("")
            for myth in mythic:
                m_name = myth.get('name', '')
                entries = myth.get('entries', [])
                content = self.converter.convert(entries, 0)
                parts.append(f"***{m_name}.*** {content}")
                parts.append("")

        return "\n".join(parts)

    def _format_damage_types(self, damage_list: list) -> str:
        """Format a list of damage types."""
        parts = []
        for item in damage_list:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                # Complex damage type with conditions
                dtype = item.get('special', item.get('damage', ''))
                parts.append(str(dtype))
        return ', '.join(parts)

    def create_index(self) -> None:
        """Create the creature index file."""
        parts = ["# Creature Index", ""]

        # Summary
        parts.append(f"**Total Creatures:** {len(self.index_entries)}")
        parts.append("")

        # Group by CR
        by_cr = {}
        for creature in self.index_entries:
            cr = creature['cr']
            if cr not in by_cr:
                by_cr[cr] = []
            by_cr[cr].append(creature)

        # Sort CRs properly
        def cr_sort_key(cr):
            if cr == '0':
                return 0
            elif '/' in str(cr):
                num, den = str(cr).split('/')
                return float(num) / float(den)
            else:
                try:
                    return float(cr)
                except ValueError:
                    return 999

        sorted_crs = sorted(by_cr.keys(), key=cr_sort_key)

        parts.append("## By Challenge Rating")
        parts.append("")

        for cr in sorted_crs:
            parts.append(f"### CR {cr}")
            parts.append("")
            parts.append("| Creature | Type | Source |")
            parts.append("| -------- | ---- | ------ |")

            for creature in sorted(by_cr[cr], key=lambda x: x['name']):
                name = creature['name']
                ctype = creature['type']
                source = creature['source']
                path = creature['path']
                parts.append(f"| [{name}]({path}) | {ctype} | {source} |")

            parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

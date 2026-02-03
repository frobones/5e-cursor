import { Shield, Heart, Footprints, Swords, Sparkles, User, Wrench } from 'lucide-react';

import type { CharacterStats } from '@/types';

interface CharacterStatsPanelProps {
  stats: CharacterStats;
}

/**
 * Calculate ability modifier from ability score.
 */
function getModifier(score: number): string {
  const mod = Math.floor((score - 10) / 2);
  return mod >= 0 ? `+${mod}` : `${mod}`;
}

/**
 * Format speed for display.
 */
function formatSpeed(speed: Record<string, number>): string {
  return Object.entries(speed)
    .map(([type, value]) => (type === 'walk' ? `${value} ft.` : `${type} ${value} ft.`))
    .join(', ');
}

/**
 * Display a character's stat block for combat reference.
 */
export default function CharacterStatsPanel({ stats }: CharacterStatsPanelProps) {
  const abilities = [
    { key: 'str', label: 'STR', value: stats.abilities?.str ?? 10 },
    { key: 'dex', label: 'DEX', value: stats.abilities?.dex ?? 10 },
    { key: 'con', label: 'CON', value: stats.abilities?.con ?? 10 },
    { key: 'int', label: 'INT', value: stats.abilities?.int ?? 10 },
    { key: 'wis', label: 'WIS', value: stats.abilities?.wis ?? 10 },
    { key: 'cha', label: 'CHA', value: stats.abilities?.cha ?? 10 },
  ];

  return (
    <div className="space-y-4 text-sm">
      {/* Header */}
      <div className="border-b border-ink-200 dark:border-ink-700 pb-2">
        <h3 className="font-display text-lg font-semibold">{stats.name}</h3>
        <p className="text-ink-500 dark:text-parchment-400 italic">
          {stats.species} {stats.character_class}
          {stats.background && ` • ${stats.background}`}
        </p>
        <p className="text-xs text-ink-400 flex items-center gap-1 mt-1">
          <User className="h-3 w-3" />
          Played by {stats.player}
        </p>
      </div>

      {/* AC, HP, Speed */}
      <div className="grid grid-cols-3 gap-2">
        <div className="flex items-center gap-1">
          <Shield className="h-4 w-4 text-blue-500" />
          <div>
            <span className="font-medium">{stats.ac}</span>
            {stats.ac_source && (
              <span className="text-xs text-ink-500 ml-1">({stats.ac_source})</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Heart className="h-4 w-4 text-red-500" />
          <div>
            <span className="font-medium">{stats.hp?.current ?? '?'}</span>
            <span className="text-xs text-ink-500">/{stats.hp?.max ?? '?'}</span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Footprints className="h-4 w-4 text-green-500" />
          <span>{formatSpeed(stats.speed ?? { walk: 30 })}</span>
        </div>
      </div>

      {/* Ability Scores */}
      <div className="grid grid-cols-6 gap-1 text-center bg-parchment-50 dark:bg-ink-800 rounded-lg p-2">
        {abilities.map((ability) => (
          <div key={ability.key}>
            <div className="text-xs font-medium text-ink-500">{ability.label}</div>
            <div className="font-medium">{ability.value}</div>
            <div className="text-xs text-ink-400">({getModifier(ability.value)})</div>
          </div>
        ))}
      </div>

      {/* Proficiency Bonus */}
      <div className="text-xs">
        <span className="font-medium">Proficiency Bonus: </span>
        <span>+{stats.proficiency_bonus}</span>
      </div>

      {/* Saves & Skills */}
      {(stats.saves || stats.skills) && (
        <div className="space-y-1 text-xs">
          {stats.saves && (
            <div>
              <span className="font-medium">Saving Throws: </span>
              {Object.entries(stats.saves)
                .map(([key, val]) => `${key.toUpperCase()} ${val}`)
                .join(', ')}
            </div>
          )}
          {stats.skills && (
            <div>
              <span className="font-medium">Skills: </span>
              {Object.entries(stats.skills)
                .map(([key, val]) => `${key} ${val}`)
                .join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Languages & Tools */}
      <div className="space-y-1 text-xs">
        <div>
          <span className="font-medium">Passive Perception: </span>
          {stats.passive_perception}
        </div>
        {stats.languages && stats.languages.length > 0 && (
          <div>
            <span className="font-medium">Languages: </span>
            {stats.languages.join(', ')}
          </div>
        )}
        {stats.tools && stats.tools.length > 0 && (
          <div className="flex items-start gap-1">
            <Wrench className="h-3 w-3 mt-0.5 text-ink-400" />
            <span>
              <span className="font-medium">Tools: </span>
              {stats.tools.join(', ')}
            </span>
          </div>
        )}
      </div>

      {/* Traits/Features */}
      {stats.traits && stats.traits.length > 0 && (
        <div className="border-t border-ink-200 dark:border-ink-700 pt-2">
          <div className="flex items-center gap-1 mb-2">
            <Sparkles className="h-4 w-4 text-purple-500" />
            <span className="font-medium">Features & Traits</span>
          </div>
          <div className="space-y-2">
            {stats.traits.map((trait, idx) => (
              <div key={idx}>
                <span className="font-medium italic">{trait.name}. </span>
                <span className="text-ink-600 dark:text-parchment-400">{trait.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions (Weapons) */}
      {stats.actions && stats.actions.length > 0 && (
        <div className="border-t border-ink-200 dark:border-ink-700 pt-2">
          <div className="flex items-center gap-1 mb-2">
            <Swords className="h-4 w-4 text-red-500" />
            <span className="font-medium">Actions</span>
          </div>
          <div className="space-y-2">
            {stats.actions.map((action, idx) => (
              <div key={idx}>
                <span className="font-medium italic">{action.name}. </span>
                <span className="text-ink-600 dark:text-parchment-400">{action.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bonus Actions */}
      {stats.bonus_actions && stats.bonus_actions.length > 0 && (
        <div className="border-t border-ink-200 dark:border-ink-700 pt-2">
          <div className="flex items-center gap-1 mb-2">
            <span className="font-medium">Bonus Actions</span>
          </div>
          <div className="space-y-2">
            {stats.bonus_actions.map((action, idx) => (
              <div key={idx}>
                <span className="font-medium italic">{action.name}. </span>
                <span className="text-ink-600 dark:text-parchment-400">{action.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reactions */}
      {stats.reactions && stats.reactions.length > 0 && (
        <div className="border-t border-ink-200 dark:border-ink-700 pt-2">
          <div className="flex items-center gap-1 mb-2">
            <span className="font-medium">Reactions</span>
          </div>
          <div className="space-y-2">
            {stats.reactions.map((reaction, idx) => (
              <div key={idx}>
                <span className="font-medium italic">{reaction.name}. </span>
                <span className="text-ink-600 dark:text-parchment-400">{reaction.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Feats */}
      {stats.feats && stats.feats.length > 0 && (
        <div className="border-t border-ink-200 dark:border-ink-700 pt-2">
          <div className="text-xs">
            <span className="font-medium">Feats: </span>
            {stats.feats.join(', ')}
          </div>
        </div>
      )}
    </div>
  );
}

import { Shield, Heart, Footprints, Brain, Swords, Sparkles } from 'lucide-react';
import clsx from 'clsx';

import type { CreatureStats } from '@/types';

interface CreatureStatsPanelProps {
  stats: CreatureStats;
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
 * Display a creature's full stat block for combat reference.
 */
export default function CreatureStatsPanel({ stats }: CreatureStatsPanelProps) {
  const abilities = [
    { key: 'str', label: 'STR', value: stats.abilities.str },
    { key: 'dex', label: 'DEX', value: stats.abilities.dex },
    { key: 'con', label: 'CON', value: stats.abilities.con },
    { key: 'int', label: 'INT', value: stats.abilities.int },
    { key: 'wis', label: 'WIS', value: stats.abilities.wis },
    { key: 'cha', label: 'CHA', value: stats.abilities.cha },
  ];

  return (
    <div className="space-y-4 text-sm">
      {/* Header */}
      <div className="border-b border-ink-200 dark:border-ink-700 pb-2">
        <h3 className="font-display text-lg font-semibold">{stats.name}</h3>
        <p className="text-ink-500 dark:text-parchment-400 italic">
          {stats.size} {stats.creatureType}
          {stats.alignment && `, ${stats.alignment}`}
        </p>
      </div>

      {/* AC, HP, Speed */}
      <div className="grid grid-cols-3 gap-2">
        <div className="flex items-center gap-1">
          <Shield className="h-4 w-4 text-blue-500" />
          <div>
            <span className="font-medium">{stats.ac}</span>
            {stats.acSource && (
              <span className="text-xs text-ink-500 ml-1">({stats.acSource})</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Heart className="h-4 w-4 text-red-500" />
          <div>
            <span className="font-medium">{stats.hp.average}</span>
            <span className="text-xs text-ink-500 ml-1">({stats.hp.formula})</span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Footprints className="h-4 w-4 text-green-500" />
          <span>{formatSpeed(stats.speed)}</span>
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

      {/* Saves & Skills */}
      {(stats.saves || stats.skills) && (
        <div className="space-y-1 text-xs">
          {stats.saves && (
            <div>
              <span className="font-medium">Saves: </span>
              {Object.entries(stats.saves)
                .map(([key, val]) => `${key.toUpperCase()} ${val}`)
                .join(', ')}
            </div>
          )}
          {stats.skills && (
            <div>
              <span className="font-medium">Skills: </span>
              {Object.entries(stats.skills)
                .map(([key, val]) => `${key.charAt(0).toUpperCase() + key.slice(1)} ${val}`)
                .join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Damage Modifiers */}
      {(stats.damageResistances ||
        stats.damageImmunities ||
        stats.damageVulnerabilities ||
        stats.conditionImmunities) && (
        <div className="space-y-1 text-xs">
          {stats.damageVulnerabilities && (
            <div>
              <span className="font-medium text-red-600">Vulnerabilities: </span>
              {stats.damageVulnerabilities.join(', ')}
            </div>
          )}
          {stats.damageResistances && (
            <div>
              <span className="font-medium text-yellow-600">Resistances: </span>
              {stats.damageResistances.join(', ')}
            </div>
          )}
          {stats.damageImmunities && (
            <div>
              <span className="font-medium text-green-600">Immunities: </span>
              {stats.damageImmunities.join(', ')}
            </div>
          )}
          {stats.conditionImmunities && (
            <div>
              <span className="font-medium text-purple-600">Condition Immunities: </span>
              {stats.conditionImmunities.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Senses & Languages */}
      <div className="space-y-1 text-xs">
        {stats.senses && (
          <div>
            <span className="font-medium">Senses: </span>
            {stats.senses.join(', ')}, passive Perception {stats.passivePerception}
          </div>
        )}
        {!stats.senses && (
          <div>
            <span className="font-medium">Senses: </span>
            passive Perception {stats.passivePerception}
          </div>
        )}
        {stats.languages && (
          <div>
            <span className="font-medium">Languages: </span>
            {stats.languages.join(', ')}
          </div>
        )}
        <div>
          <span className="font-medium">CR: </span>
          {stats.cr}
        </div>
      </div>

      {/* Traits */}
      {stats.traits && stats.traits.length > 0 && (
        <div className="border-t border-ink-200 dark:border-ink-700 pt-2">
          <div className="flex items-center gap-1 mb-2">
            <Sparkles className="h-4 w-4 text-purple-500" />
            <span className="font-medium">Traits</span>
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

      {/* Actions */}
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
      {stats.bonusActions && stats.bonusActions.length > 0 && (
        <div className="border-t border-ink-200 dark:border-ink-700 pt-2">
          <div className="flex items-center gap-1 mb-2">
            <span className="font-medium">Bonus Actions</span>
          </div>
          <div className="space-y-2">
            {stats.bonusActions.map((action, idx) => (
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

      {/* Legendary Actions */}
      {stats.legendaryActions && stats.legendaryActions.length > 0 && (
        <div className="border-t border-ink-200 dark:border-ink-700 pt-2">
          <div className="flex items-center gap-1 mb-2">
            <span className="font-medium text-yellow-600">Legendary Actions</span>
          </div>
          <div className="space-y-2">
            {stats.legendaryActions.map((action, idx) => (
              <div key={idx}>
                <span className="font-medium italic">{action.name}. </span>
                <span className="text-ink-600 dark:text-parchment-400">{action.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

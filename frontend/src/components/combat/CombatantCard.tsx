import clsx from 'clsx';
import { Heart, Shield, Skull, Swords } from 'lucide-react';

import type { Combatant } from '@/types';

interface CombatantCardProps {
  combatant: Combatant;
  isSelected?: boolean;
  onClick?: () => void;
  onToggleCondition?: (condition: string) => void;
}

export default function CombatantCard({
  combatant,
  isSelected,
  onClick,
  onToggleCondition,
}: CombatantCardProps) {
  const isMonster = combatant.type === 'monster';
  const isDefeated = isMonster && combatant.currentHp <= 0;
  const hpPercentage = isMonster
    ? Math.max(0, Math.min(100, (combatant.currentHp / combatant.maxHp) * 100))
    : 100;
  const damageTaken = combatant.damageTaken || 0;

  const getHPColor = () => {
    if (isDefeated) return 'bg-red-500';
    if (hpPercentage <= 25) return 'bg-red-500';
    if (hpPercentage <= 50) return 'bg-orange-500';
    if (hpPercentage <= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div
      onClick={onClick}
      className={clsx(
        'p-4 rounded-lg border-2 transition-all cursor-pointer',
        combatant.isActive && 'ring-2 ring-yellow-400 ring-offset-2',
        isSelected
          ? 'border-parchment-500 bg-parchment-50 dark:bg-ink-800'
          : 'border-ink-200 dark:border-ink-700 hover:border-parchment-400',
        isDefeated && 'opacity-60'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {isDefeated && <Skull className="h-4 w-4 text-red-500" />}
          <span className={clsx('font-medium', isDefeated && 'line-through text-ink-500')}>
            {combatant.name}
          </span>
        </div>
        <span
          className={clsx(
            'text-xs px-2 py-0.5 rounded-full',
            combatant.type === 'player'
              ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
              : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
          )}
        >
          {combatant.type === 'player' ? 'PC' : 'NPC'}
        </span>
      </div>

      {/* Quick Stats: Initiative + AC */}
      <div className="flex items-center gap-3 text-sm text-ink-500 mb-2">
        <span>Init: {combatant.initiative}</span>
        <span className="flex items-center gap-1">
          <Shield className="h-3 w-3" />
          AC {combatant.ac}
        </span>
      </div>

      {/* HP/Damage display - different for monsters vs players */}
      <div className="mb-3">
        {isMonster ? (
          // Monsters: Show HP bar with current/max
          <>
            <div className="flex items-center justify-between text-sm mb-1">
              <div className="flex items-center gap-1">
                <Heart className="h-4 w-4 text-red-500" />
                <span>
                  {combatant.currentHp} / {combatant.maxHp}
                </span>
              </div>
              {combatant.tempHp > 0 && (
                <div className="flex items-center gap-1 text-blue-500">
                  <Shield className="h-4 w-4" />
                  <span>+{combatant.tempHp}</span>
                </div>
              )}
            </div>
            <div className="h-2 bg-ink-200 dark:bg-ink-700 rounded-full overflow-hidden">
              <div
                className={clsx('h-full transition-all', getHPColor())}
                style={{ width: `${hpPercentage}%` }}
              />
            </div>
          </>
        ) : (
          // Players: Show damage taken (DM doesn't know their HP)
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-1">
              <Swords className="h-4 w-4 text-orange-500" />
              <span className={clsx(damageTaken > 0 && 'text-red-600 dark:text-red-400 font-medium')}>
                Damage Taken: {damageTaken}
              </span>
            </div>
            {combatant.tempHp > 0 && (
              <div className="flex items-center gap-1 text-blue-500">
                <Shield className="h-4 w-4" />
                <span>+{combatant.tempHp}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Conditions */}
      {combatant.conditions.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {combatant.conditions.map((condition) => (
            <span
              key={condition}
              onClick={(e) => {
                e.stopPropagation();
                onToggleCondition?.(condition);
              }}
              className="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300 cursor-pointer hover:bg-purple-200 dark:hover:bg-purple-800"
            >
              {condition}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

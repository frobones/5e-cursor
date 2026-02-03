import { useState } from 'react';
import { Minus, Plus, Heart, Shield, Zap, Swords } from 'lucide-react';
import clsx from 'clsx';

import type { Combatant } from '@/types';
import { CONDITIONS } from '@/utils/combatState';

interface CombatTrackerProps {
  selectedCombatant: Combatant | null;
  onApplyDamage: (amount: number, source?: string) => void;
  onApplyHealing: (amount: number, source?: string) => void;
  onAddTempHp: (amount: number) => void;
  onToggleCondition: (condition: string) => void;
}

export default function CombatTracker({
  selectedCombatant,
  onApplyDamage,
  onApplyHealing,
  onAddTempHp,
  onToggleCondition,
}: CombatTrackerProps) {
  const [amount, setAmount] = useState<number>(0);
  const [source, setSource] = useState('');
  const [mode, setMode] = useState<'damage' | 'healing' | 'temp'>('damage');

  if (!selectedCombatant) {
    return (
      <div className="p-6 text-center text-ink-500 bg-ink-50 dark:bg-ink-800 rounded-lg">
        <p>Select a combatant to track</p>
      </div>
    );
  }

  const isMonster = selectedCombatant.type === 'monster';
  const damageTaken = selectedCombatant.damageTaken || 0;

  const handleApply = () => {
    if (amount <= 0) return;

    switch (mode) {
      case 'damage':
        onApplyDamage(amount, source || undefined);
        break;
      case 'healing':
        onApplyHealing(amount, source || undefined);
        break;
      case 'temp':
        onAddTempHp(amount);
        break;
    }

    setAmount(0);
    setSource('');
  };

  const quickAmounts = [1, 5, 10, 20];

  return (
    <div className="space-y-4">
      {/* Selected combatant info */}
      <div className="p-4 bg-parchment-50 dark:bg-ink-800 rounded-lg">
        <h3 className="font-semibold text-lg mb-2">{selectedCombatant.name}</h3>
        <div className="flex items-center gap-4 text-sm">
          {isMonster ? (
            // Monsters: show HP
            <div className="flex items-center gap-1">
              <Heart className="h-4 w-4 text-red-500" />
              <span>
                {selectedCombatant.currentHp} / {selectedCombatant.maxHp}
              </span>
            </div>
          ) : (
            // Players: show damage taken
            <div className="flex items-center gap-1">
              <Swords className="h-4 w-4 text-orange-500" />
              <span className={clsx(damageTaken > 0 && 'text-red-600 dark:text-red-400 font-medium')}>
                Damage Taken: {damageTaken}
              </span>
            </div>
          )}
          {selectedCombatant.tempHp > 0 && (
            <div className="flex items-center gap-1 text-blue-500">
              <Shield className="h-4 w-4" />
              <span>+{selectedCombatant.tempHp}</span>
            </div>
          )}
        </div>
      </div>

      {/* Mode selector */}
      <div className="flex gap-2">
        <button
          onClick={() => setMode('damage')}
          className={clsx(
            'flex-1 py-2 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2',
            mode === 'damage'
              ? 'bg-red-500 text-white'
              : 'bg-ink-100 dark:bg-ink-800 hover:bg-ink-200 dark:hover:bg-ink-700'
          )}
        >
          <Zap className="h-4 w-4" />
          Damage
        </button>
        <button
          onClick={() => setMode('healing')}
          className={clsx(
            'flex-1 py-2 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2',
            mode === 'healing'
              ? 'bg-green-500 text-white'
              : 'bg-ink-100 dark:bg-ink-800 hover:bg-ink-200 dark:hover:bg-ink-700'
          )}
        >
          <Heart className="h-4 w-4" />
          Heal
        </button>
        <button
          onClick={() => setMode('temp')}
          className={clsx(
            'flex-1 py-2 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2',
            mode === 'temp'
              ? 'bg-blue-500 text-white'
              : 'bg-ink-100 dark:bg-ink-800 hover:bg-ink-200 dark:hover:bg-ink-700'
          )}
        >
          <Shield className="h-4 w-4" />
          Temp HP
        </button>
      </div>

      {/* Amount input */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAmount((a) => Math.max(0, a - 1))}
            className="p-2 rounded-lg bg-ink-100 dark:bg-ink-800 hover:bg-ink-200 dark:hover:bg-ink-700 transition-colors"
          >
            <Minus className="h-4 w-4" />
          </button>
          <input
            type="number"
            min={0}
            value={amount}
            onChange={(e) => setAmount(Math.max(0, parseInt(e.target.value) || 0))}
            className="flex-1 px-4 py-2 text-center text-xl font-bold border border-ink-200 dark:border-ink-700 rounded-lg bg-white dark:bg-ink-900 focus:outline-none focus:ring-2 focus:ring-parchment-500"
          />
          <button
            onClick={() => setAmount((a) => a + 1)}
            className="p-2 rounded-lg bg-ink-100 dark:bg-ink-800 hover:bg-ink-200 dark:hover:bg-ink-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>

        {/* Quick amounts */}
        <div className="flex gap-2">
          {quickAmounts.map((qa) => (
            <button
              key={qa}
              onClick={() => setAmount(qa)}
              className="flex-1 py-1 text-sm bg-ink-100 dark:bg-ink-800 hover:bg-ink-200 dark:hover:bg-ink-700 rounded-lg transition-colors"
            >
              {qa}
            </button>
          ))}
        </div>
      </div>

      {/* Source input (for damage/healing) */}
      {mode !== 'temp' && (
        <input
          type="text"
          placeholder="Source (optional, e.g., Fireball)"
          value={source}
          onChange={(e) => setSource(e.target.value)}
          className="w-full px-4 py-2 border border-ink-200 dark:border-ink-700 rounded-lg bg-white dark:bg-ink-900 focus:outline-none focus:ring-2 focus:ring-parchment-500"
        />
      )}

      {/* Apply button */}
      <button
        onClick={handleApply}
        disabled={amount <= 0}
        className={clsx(
          'w-full py-3 rounded-lg font-semibold text-white transition-colors',
          amount <= 0 && 'opacity-50 cursor-not-allowed',
          mode === 'damage' && 'bg-red-500 hover:bg-red-600',
          mode === 'healing' && 'bg-green-500 hover:bg-green-600',
          mode === 'temp' && 'bg-blue-500 hover:bg-blue-600'
        )}
      >
        Apply {mode === 'damage' ? 'Damage' : mode === 'healing' ? 'Healing' : 'Temp HP'}
      </button>

      {/* Conditions */}
      <div className="pt-4 border-t border-ink-200 dark:border-ink-700">
        <h4 className="text-sm font-medium mb-2">Conditions</h4>
        <div className="flex flex-wrap gap-1">
          {CONDITIONS.map((condition) => {
            const isActive = selectedCombatant.conditions.includes(condition);
            return (
              <button
                key={condition}
                onClick={() => onToggleCondition(condition)}
                className={clsx(
                  'text-xs px-2 py-1 rounded-full transition-colors',
                  isActive
                    ? 'bg-purple-500 text-white'
                    : 'bg-ink-100 dark:bg-ink-800 hover:bg-ink-200 dark:hover:bg-ink-700'
                )}
              >
                {condition}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { Dices } from 'lucide-react';
import clsx from 'clsx';

import type { Combatant } from '@/types';

// Roll a d20 and return detailed result
function rollD20(): number {
  return Math.floor(Math.random() * 20) + 1;
}

// Get the base creature name (without the number suffix like "Goblin 1" -> "Goblin")
function getBaseCreatureName(name: string): string {
  // Remove trailing number and space (e.g., "Goblin 1" -> "Goblin")
  return name.replace(/\s+\d+$/, '');
}

interface RollLogEntry {
  creatureName: string;
  d20: number;
  modifier: number;
  total: number;
  affectedCount: number;
}

interface InitiativeSetupProps {
  combatants: Combatant[];
  onUpdateInitiative: (combatantId: string, initiative: number) => void;
  onBatchUpdateInitiative?: (updates: Array<{ id: string; initiative: number }>) => void;
  onStartCombat: () => void;
}

export default function InitiativeSetup({
  combatants,
  onUpdateInitiative,
  onBatchUpdateInitiative,
  onStartCombat,
}: InitiativeSetupProps) {
  const [rolling, setRolling] = useState<string | null>(null);
  const [rollLog, setRollLog] = useState<RollLogEntry[]>([]);

  const handleRollAll = () => {
    const monsters = combatants.filter((c) => c.type === 'monster');
    
    // Group monsters by base name (e.g., "Goblin 1" and "Goblin 2" share a roll)
    const groupedByName = new Map<string, Combatant[]>();
    for (const monster of monsters) {
      const baseName = getBaseCreatureName(monster.name);
      if (!groupedByName.has(baseName)) {
        groupedByName.set(baseName, []);
      }
      groupedByName.get(baseName)!.push(monster);
    }

    // Roll once per group
    const updates: Array<{ id: string; initiative: number }> = [];
    const newLogEntries: RollLogEntry[] = [];

    for (const [baseName, group] of groupedByName) {
      // Use the first creature's DEX modifier (they should all be the same for same creature type)
      const dexMod = group[0].dexModifier || 0;
      const d20 = rollD20();
      const total = d20 + dexMod;

      // Apply same initiative to all creatures in group
      for (const creature of group) {
        updates.push({ id: creature.id, initiative: total });
      }

      // Log the roll
      newLogEntries.push({
        creatureName: baseName,
        d20,
        modifier: dexMod,
        total,
        affectedCount: group.length,
      });
    }

    // Update log (most recent first)
    setRollLog([...newLogEntries, ...rollLog].slice(0, 10));

    // Use batch update if available, otherwise fall back to individual updates
    if (onBatchUpdateInitiative) {
      onBatchUpdateInitiative(updates);
    } else {
      updates.forEach((u) => onUpdateInitiative(u.id, u.initiative));
    }
  };

  const handleRollOne = (combatant: Combatant) => {
    setRolling(combatant.id);
    const dexMod = combatant.dexModifier || 0;
    const d20 = rollD20();
    const total = d20 + dexMod;
    
    onUpdateInitiative(combatant.id, total);
    
    // Log the roll
    setRollLog([
      {
        creatureName: combatant.name,
        d20,
        modifier: dexMod,
        total,
        affectedCount: 1,
      },
      ...rollLog,
    ].slice(0, 10));

    setTimeout(() => setRolling(null), 300);
  };

  const allHaveInitiative = combatants.every((c) => c.initiative > 0);

  // Sort combatants: players first, then monsters
  const sortedCombatants = [...combatants].sort((a, b) => {
    if (a.type === 'player' && b.type !== 'player') return -1;
    if (a.type !== 'player' && b.type === 'player') return 1;
    return a.name.localeCompare(b.name);
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Set Initiative</h2>
        <button
          onClick={handleRollAll}
          className="btn btn-secondary flex items-center gap-2"
        >
          <Dices className="h-4 w-4" />
          Roll All Monsters
        </button>
      </div>

      <div className="space-y-3">
        {sortedCombatants.map((combatant) => (
          <div
            key={combatant.id}
            className={clsx(
              'flex items-center justify-between p-3 rounded-lg border',
              'border-ink-200 dark:border-ink-700 bg-white dark:bg-ink-900'
            )}
          >
            <div className="flex items-center gap-3">
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
              <span className="font-medium">{combatant.name}</span>
            </div>

            <div className="flex items-center gap-2">
              {combatant.type === 'monster' && (
                <button
                  onClick={() => handleRollOne(combatant)}
                  className="p-2 rounded-lg hover:bg-ink-100 dark:hover:bg-ink-800 transition-colors"
                  title="Roll initiative"
                >
                  <Dices className="h-4 w-4" />
                </button>
              )}
              <input
                type="number"
                min={1}
                max={30}
                value={combatant.initiative || ''}
                onChange={(e) =>
                  onUpdateInitiative(combatant.id, parseInt(e.target.value) || 0)
                }
                placeholder="Init"
                className={clsx(
                  'w-20 px-3 py-1 text-center border rounded-lg',
                  'border-ink-200 dark:border-ink-700 bg-white dark:bg-ink-800',
                  'focus:outline-none focus:ring-2 focus:ring-parchment-500',
                  rolling === combatant.id && 'animate-pulse'
                )}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Roll Log Console */}
      {rollLog.length > 0 && (
        <div className="bg-ink-800 dark:bg-ink-900 rounded-lg p-3 font-mono text-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-parchment-400 text-xs uppercase tracking-wide">Roll Log</span>
            <button
              onClick={() => setRollLog([])}
              className="text-xs text-parchment-500 hover:text-parchment-300"
            >
              Clear
            </button>
          </div>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {rollLog.map((entry, i) => (
              <div key={i} className="text-parchment-200 flex items-center gap-2">
                <span className="text-parchment-400">&gt;</span>
                <span className="text-amber-400 font-semibold">{entry.creatureName}</span>
                {entry.affectedCount > 1 && (
                  <span className="text-parchment-500">×{entry.affectedCount}</span>
                )}
                <span className="text-parchment-500">:</span>
                <span className="text-cyan-400">{entry.d20}</span>
                <span className="text-parchment-500">
                  {entry.modifier >= 0 ? '+' : ''}
                  {entry.modifier}
                </span>
                <span className="text-parchment-500">=</span>
                <span className="text-green-400 font-bold">{entry.total}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={onStartCombat}
        disabled={!allHaveInitiative}
        className={clsx(
          'w-full btn btn-primary py-3 text-lg',
          !allHaveInitiative && 'opacity-50 cursor-not-allowed'
        )}
      >
        {allHaveInitiative ? 'Begin Combat' : 'Enter all initiative values to begin'}
      </button>
    </div>
  );
}

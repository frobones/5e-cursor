import { Minus, Plus, Trash2 } from 'lucide-react';
import clsx from 'clsx';

import type { EncounterBuilderCreature } from '@/types';

interface EncounterPanelProps {
  creatures: EncounterBuilderCreature[];
  onUpdateCount: (slug: string, delta: number) => void;
  onRemoveCreature: (slug: string) => void;
}

export default function EncounterPanel({
  creatures,
  onUpdateCount,
  onRemoveCreature,
}: EncounterPanelProps) {
  const totalCreatures = creatures.reduce((sum, c) => sum + c.count, 0);
  const totalXP = creatures.reduce((sum, c) => sum + c.xp * c.count, 0);

  if (creatures.length === 0) {
    return (
      <div className="border-2 border-dashed border-ink-200 dark:border-ink-700 rounded-lg p-8 text-center">
        <p className="text-ink-500">
          No creatures added yet. Click creatures on the left to add them to your encounter.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center text-sm text-ink-600 dark:text-ink-400">
        <span>{totalCreatures} creature{totalCreatures !== 1 ? 's' : ''}</span>
        <span>{totalXP.toLocaleString()} base XP</span>
      </div>

      <ul className="space-y-2">
        {creatures.map((creature) => (
          <li
            key={creature.slug}
            className={clsx(
              'flex items-center justify-between p-3 rounded-lg',
              'bg-parchment-50 dark:bg-ink-800 border border-ink-200 dark:border-ink-700'
            )}
          >
            <div className="flex-1 min-w-0">
              <div className="font-medium truncate">{creature.name}</div>
              <div className="text-sm text-ink-500">
                CR {creature.cr} &bull; {creature.xp.toLocaleString()} XP each
              </div>
            </div>

            <div className="flex items-center gap-2 ml-4">
              <button
                type="button"
                onClick={() => onUpdateCount(creature.slug, -1)}
                disabled={creature.count <= 1}
                className={clsx(
                  'p-1.5 rounded-full transition-colors',
                  creature.count <= 1
                    ? 'text-ink-300 cursor-not-allowed'
                    : 'hover:bg-ink-200 dark:hover:bg-ink-700'
                )}
              >
                <Minus className="h-4 w-4" />
              </button>

              <span className="w-8 text-center font-medium">{creature.count}</span>

              <button
                type="button"
                onClick={() => onUpdateCount(creature.slug, 1)}
                className="p-1.5 rounded-full hover:bg-ink-200 dark:hover:bg-ink-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
              </button>

              <button
                type="button"
                onClick={() => onRemoveCreature(creature.slug)}
                className="p-1.5 rounded-full text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors ml-2"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </li>
        ))}
      </ul>

      <div className="pt-2 border-t border-ink-200 dark:border-ink-700">
        <div className="flex justify-between text-sm">
          <span className="text-ink-600 dark:text-ink-400">Total XP:</span>
          <span className="font-medium">{totalXP.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

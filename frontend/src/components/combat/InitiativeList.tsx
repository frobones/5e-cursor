import clsx from 'clsx';

import type { Combatant } from '@/types';
import { sortByInitiative } from '@/utils/combatState';

import CombatantCard from './CombatantCard';

interface InitiativeListProps {
  combatants: Combatant[];
  selectedId?: string;
  onSelectCombatant: (id: string) => void;
  onToggleCondition: (combatantId: string, condition: string) => void;
}

export default function InitiativeList({
  combatants,
  selectedId,
  onSelectCombatant,
  onToggleCondition,
}: InitiativeListProps) {
  const sortedCombatants = sortByInitiative(combatants);

  return (
    <div className="space-y-2">
      {sortedCombatants.map((combatant, index) => (
        <div key={combatant.id} className="flex items-start gap-3">
          {/* Turn indicator */}
          <div
            className={clsx(
              'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0',
              combatant.isActive
                ? 'bg-yellow-400 text-yellow-900'
                : 'bg-ink-200 dark:bg-ink-700 text-ink-600 dark:text-ink-400'
            )}
          >
            {index + 1}
          </div>

          {/* Combatant card */}
          <div className="flex-1">
            <CombatantCard
              combatant={combatant}
              isSelected={combatant.id === selectedId}
              onClick={() => onSelectCombatant(combatant.id)}
              onToggleCondition={(condition) => onToggleCondition(combatant.id, condition)}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

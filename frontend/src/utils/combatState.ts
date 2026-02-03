/**
 * Combat state management utilities.
 */

import type { Combatant, CombatState, DamageEvent } from '@/types';

/**
 * Generate a unique ID for combatants and events.
 */
export function generateId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Expand creature quantities into individual combatant instances.
 * E.g., "3 Goblins" becomes "Goblin 1", "Goblin 2", "Goblin 3"
 */
export function expandCreatures(
  creatures: Array<{ name: string; slug: string; count: number; maxHp: number }>
): Combatant[] {
  const combatants: Combatant[] = [];

  for (const creature of creatures) {
    for (let i = 1; i <= creature.count; i++) {
      combatants.push({
        id: generateId('monster'),
        name: creature.count > 1 ? `${creature.name} ${i}` : creature.name,
        type: 'monster',
        creatureSlug: creature.slug,
        initiative: 0,
        maxHp: creature.maxHp,
        currentHp: creature.maxHp,
        tempHp: 0,
        damageTaken: 0,
        conditions: [],
        isActive: false,
      });
    }
  }

  return combatants;
}

/**
 * Roll initiative for a monster (d20 + dex modifier).
 * For simplicity, we just roll d20 here.
 */
export function rollInitiative(dexModifier: number = 0): number {
  const roll = Math.floor(Math.random() * 20) + 1;
  return roll + dexModifier;
}

/**
 * Sort combatants by initiative (descending).
 * Stable sort for ties.
 */
export function sortByInitiative(combatants: Combatant[]): Combatant[] {
  return [...combatants].sort((a, b) => b.initiative - a.initiative);
}

/**
 * Apply damage to a combatant.
 * - For monsters: Temp HP is consumed first, then current HP.
 * - For players: Track damage taken (DM doesn't know player HP).
 */
export function applyDamage(combatant: Combatant, amount: number): Combatant {
  let remaining = amount;

  // Consume temp HP first (for both players and monsters)
  if (combatant.tempHp > 0) {
    if (combatant.tempHp >= remaining) {
      return {
        ...combatant,
        tempHp: combatant.tempHp - remaining,
      };
    } else {
      remaining -= combatant.tempHp;
      combatant = { ...combatant, tempHp: 0 };
    }
  }

  // For players: track damage taken instead of reducing HP
  if (combatant.type === 'player') {
    return {
      ...combatant,
      damageTaken: (combatant.damageTaken || 0) + remaining,
    };
  }

  // For monsters: apply remaining damage to current HP
  return {
    ...combatant,
    currentHp: Math.max(0, combatant.currentHp - remaining),
  };
}

/**
 * Apply healing to a combatant.
 * - For monsters: Cannot exceed max HP.
 * - For players: Reduces damage taken (cannot go below 0).
 */
export function applyHealing(combatant: Combatant, amount: number): Combatant {
  // For players: reduce damage taken
  if (combatant.type === 'player') {
    return {
      ...combatant,
      damageTaken: Math.max(0, (combatant.damageTaken || 0) - amount),
    };
  }

  // For monsters: heal up to max HP
  return {
    ...combatant,
    currentHp: Math.min(combatant.maxHp, combatant.currentHp + amount),
  };
}

/**
 * Add temporary HP to a combatant.
 * Temp HP doesn't stack - use the higher value.
 */
export function addTempHp(combatant: Combatant, amount: number): Combatant {
  return {
    ...combatant,
    tempHp: Math.max(combatant.tempHp, amount),
  };
}

/**
 * Advance to the next turn in initiative order.
 * Returns updated combat state.
 */
export function nextTurn(state: CombatState): CombatState {
  const { combatants, turn, round } = state;
  const sortedCombatants = sortByInitiative(combatants);

  let nextTurn = turn + 1;
  let nextRound = round;

  // Wrap around to next round
  if (nextTurn >= sortedCombatants.length) {
    nextTurn = 0;
    nextRound = round + 1;
  }

  // Update active status
  const updatedCombatants = sortedCombatants.map((c, i) => ({
    ...c,
    isActive: i === nextTurn,
  }));

  return {
    ...state,
    combatants: updatedCombatants,
    turn: nextTurn,
    round: nextRound,
  };
}

/**
 * Go back to the previous turn.
 */
export function previousTurn(state: CombatState): CombatState {
  const { combatants, turn, round } = state;
  const sortedCombatants = sortByInitiative(combatants);

  let prevTurn = turn - 1;
  let prevRound = round;

  // Wrap around to previous round
  if (prevTurn < 0) {
    if (round > 1) {
      prevTurn = sortedCombatants.length - 1;
      prevRound = round - 1;
    } else {
      prevTurn = 0;
      prevRound = 1;
    }
  }

  // Update active status
  const updatedCombatants = sortedCombatants.map((c, i) => ({
    ...c,
    isActive: i === prevTurn,
  }));

  return {
    ...state,
    combatants: updatedCombatants,
    turn: prevTurn,
    round: prevRound,
  };
}

/**
 * Get the current active combatant.
 */
export function getCurrentCombatant(state: CombatState): Combatant | undefined {
  return state.combatants.find((c) => c.isActive);
}

/**
 * Log a damage event.
 */
export function logDamageEvent(
  state: CombatState,
  targetId: string,
  targetName: string,
  amount: number,
  type: 'damage' | 'healing' | 'temp_hp',
  source?: string
): DamageEvent {
  return {
    id: generateId('evt'),
    round: state.round,
    turn: state.turn,
    targetId,
    targetName,
    amount,
    type,
    source,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Toggle a condition on a combatant.
 */
export function toggleCondition(combatant: Combatant, condition: string): Combatant {
  const hasCondition = combatant.conditions.includes(condition);
  return {
    ...combatant,
    conditions: hasCondition
      ? combatant.conditions.filter((c) => c !== condition)
      : [...combatant.conditions, condition],
  };
}

/**
 * Common D&D conditions.
 */
export const CONDITIONS = [
  'Blinded',
  'Charmed',
  'Deafened',
  'Frightened',
  'Grappled',
  'Incapacitated',
  'Invisible',
  'Paralyzed',
  'Petrified',
  'Poisoned',
  'Prone',
  'Restrained',
  'Stunned',
  'Unconscious',
] as const;

export type Condition = (typeof CONDITIONS)[number];

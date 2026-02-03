/**
 * Encounter difficulty calculator based on DMG 2024 rules.
 * Ported from scripts/campaign/encounter_builder.py
 */

// DMG XP Thresholds by Character Level
// Format: level -> [easy, medium, hard, deadly]
export const XP_THRESHOLDS: Record<number, [number, number, number, number]> = {
  1: [25, 50, 75, 100],
  2: [50, 100, 150, 200],
  3: [75, 150, 225, 400],
  4: [125, 250, 375, 500],
  5: [250, 500, 750, 1100],
  6: [300, 600, 900, 1400],
  7: [350, 750, 1100, 1700],
  8: [450, 900, 1400, 2100],
  9: [550, 1100, 1600, 2400],
  10: [600, 1200, 1900, 2800],
  11: [800, 1600, 2400, 3600],
  12: [1000, 2000, 3000, 4500],
  13: [1100, 2200, 3400, 5100],
  14: [1250, 2500, 3800, 5700],
  15: [1400, 2800, 4300, 6400],
  16: [1600, 3200, 4800, 7200],
  17: [2000, 3900, 5900, 8800],
  18: [2100, 4200, 6300, 9500],
  19: [2400, 4900, 7300, 10900],
  20: [2800, 5700, 8500, 12700],
};

// XP values by Challenge Rating
export const CR_XP: Record<string, number> = {
  '0': 10,
  '1/8': 25,
  '1/4': 50,
  '1/2': 100,
  '1': 200,
  '2': 450,
  '3': 700,
  '4': 1100,
  '5': 1800,
  '6': 2300,
  '7': 2900,
  '8': 3900,
  '9': 5000,
  '10': 5900,
  '11': 7200,
  '12': 8400,
  '13': 10000,
  '14': 11500,
  '15': 13000,
  '16': 15000,
  '17': 18000,
  '18': 20000,
  '19': 22000,
  '20': 25000,
  '21': 33000,
  '22': 41000,
  '23': 50000,
  '24': 62000,
  '25': 75000,
  '26': 90000,
  '27': 105000,
  '28': 120000,
  '29': 135000,
  '30': 155000,
};

// Encounter multipliers based on number of monsters (DMG)
const ENCOUNTER_MULTIPLIERS: [number, number, number][] = [
  [1, 1, 1.0],
  [2, 2, 1.5],
  [3, 6, 2.0],
  [7, 10, 2.5],
  [11, 14, 3.0],
  [15, Infinity, 4.0],
];

export type Difficulty = 'trivial' | 'easy' | 'medium' | 'hard' | 'deadly';

export interface PartyThresholds {
  easy: number;
  medium: number;
  hard: number;
  deadly: number;
}

export interface DifficultyResult {
  difficulty: Difficulty;
  baseXP: number;
  multiplier: number;
  adjustedXP: number;
  thresholds: PartyThresholds;
}

/**
 * Get XP value for a Challenge Rating.
 */
export function getXPForCR(cr: string): number {
  return CR_XP[cr] ?? 0;
}

/**
 * Calculate party XP thresholds based on level and size.
 */
export function getPartyThresholds(level: number, size: number): PartyThresholds {
  const clampedLevel = Math.max(1, Math.min(20, level));
  const thresholds = XP_THRESHOLDS[clampedLevel];

  return {
    easy: thresholds[0] * size,
    medium: thresholds[1] * size,
    hard: thresholds[2] * size,
    deadly: thresholds[3] * size,
  };
}

/**
 * Get encounter multiplier based on number of creatures.
 */
export function getEncounterMultiplier(numCreatures: number): number {
  for (const [min, max, mult] of ENCOUNTER_MULTIPLIERS) {
    if (numCreatures >= min && numCreatures <= max) {
      return mult;
    }
  }
  return 4.0; // Default to max multiplier
}

/**
 * Calculate encounter difficulty.
 */
export function calculateDifficulty(
  baseXP: number,
  numCreatures: number,
  partyLevel: number,
  partySize: number
): DifficultyResult {
  const multiplier = getEncounterMultiplier(numCreatures);
  const adjustedXP = Math.floor(baseXP * multiplier);
  const thresholds = getPartyThresholds(partyLevel, partySize);

  let difficulty: Difficulty;
  if (adjustedXP < thresholds.easy) {
    difficulty = 'trivial';
  } else if (adjustedXP < thresholds.medium) {
    difficulty = 'easy';
  } else if (adjustedXP < thresholds.hard) {
    difficulty = 'medium';
  } else if (adjustedXP < thresholds.deadly) {
    difficulty = 'hard';
  } else {
    difficulty = 'deadly';
  }

  return {
    difficulty,
    baseXP,
    multiplier,
    adjustedXP,
    thresholds,
  };
}

/**
 * Get color class for difficulty badge.
 */
export function getDifficultyColor(difficulty: Difficulty): string {
  switch (difficulty) {
    case 'trivial':
      return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
    case 'easy':
      return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300';
    case 'medium':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300';
    case 'hard':
      return 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300';
    case 'deadly':
      return 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300';
  }
}

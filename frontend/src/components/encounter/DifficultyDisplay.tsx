import clsx from 'clsx';

import {
  calculateDifficulty,
  getDifficultyColor,
  type DifficultyResult,
} from '@/utils/encounterCalculator';

import type { EncounterBuilderCreature } from '@/types';

interface DifficultyDisplayProps {
  creatures: EncounterBuilderCreature[];
  partyLevel: number;
  partySize: number;
}

export default function DifficultyDisplay({
  creatures,
  partyLevel,
  partySize,
}: DifficultyDisplayProps) {
  const totalCreatures = creatures.reduce((sum, c) => sum + c.count, 0);
  const baseXP = creatures.reduce((sum, c) => sum + c.xp * c.count, 0);

  const result: DifficultyResult = calculateDifficulty(
    baseXP,
    totalCreatures,
    partyLevel,
    partySize
  );

  if (creatures.length === 0) {
    return (
      <div className="p-4 bg-ink-50 dark:bg-ink-800 rounded-lg text-center text-ink-500">
        Add creatures to see difficulty
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Difficulty Badge */}
      <div className="flex items-center justify-center">
        <span
          className={clsx(
            'px-4 py-2 rounded-full text-lg font-semibold capitalize',
            getDifficultyColor(result.difficulty)
          )}
        >
          {result.difficulty}
        </span>
      </div>

      {/* XP Breakdown */}
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="p-2 bg-ink-50 dark:bg-ink-800 rounded text-center">
          <div className="text-ink-500">Base XP</div>
          <div className="font-medium">{result.baseXP.toLocaleString()}</div>
        </div>
        <div className="p-2 bg-ink-50 dark:bg-ink-800 rounded text-center">
          <div className="text-ink-500">Multiplier</div>
          <div className="font-medium">&times;{result.multiplier}</div>
        </div>
        <div className="col-span-2 p-2 bg-parchment-100 dark:bg-ink-700 rounded text-center">
          <div className="text-ink-500">Adjusted XP</div>
          <div className="font-semibold text-lg">{result.adjustedXP.toLocaleString()}</div>
        </div>
      </div>

      {/* Party Thresholds */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-ink-600 dark:text-ink-400">
          Party Thresholds (Level {partyLevel} × {partySize})
        </h4>
        <div className="grid grid-cols-4 gap-1 text-xs">
          <ThresholdBar
            label="Easy"
            value={result.thresholds.easy}
            current={result.adjustedXP}
            color="bg-green-500"
          />
          <ThresholdBar
            label="Medium"
            value={result.thresholds.medium}
            current={result.adjustedXP}
            color="bg-blue-500"
          />
          <ThresholdBar
            label="Hard"
            value={result.thresholds.hard}
            current={result.adjustedXP}
            color="bg-orange-500"
          />
          <ThresholdBar
            label="Deadly"
            value={result.thresholds.deadly}
            current={result.adjustedXP}
            color="bg-red-500"
          />
        </div>
      </div>
    </div>
  );
}

interface ThresholdBarProps {
  label: string;
  value: number;
  current: number;
  color: string;
}

function ThresholdBar({ label, value, current, color }: ThresholdBarProps) {
  const isActive = current >= value;

  return (
    <div className="text-center">
      <div
        className={clsx(
          'h-2 rounded-full mb-1',
          isActive ? color : 'bg-ink-200 dark:bg-ink-700'
        )}
      />
      <div className="text-ink-500">{label}</div>
      <div className={clsx('font-medium', isActive && 'text-ink-900 dark:text-ink-100')}>
        {value.toLocaleString()}
      </div>
    </div>
  );
}

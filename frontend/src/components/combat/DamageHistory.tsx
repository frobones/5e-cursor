import clsx from 'clsx';
import { Zap, Heart, Shield } from 'lucide-react';

import type { DamageEvent } from '@/types';

interface DamageHistoryProps {
  events: DamageEvent[];
  currentRound: number;
}

export default function DamageHistory({ events, currentRound }: DamageHistoryProps) {
  if (events.length === 0) {
    return (
      <div className="p-4 text-center text-ink-500 bg-ink-50 dark:bg-ink-800 rounded-lg">
        <p>No events yet. Apply damage or healing to see history.</p>
      </div>
    );
  }

  // Group events by round
  const eventsByRound = events.reduce(
    (acc, event) => {
      const round = event.round;
      if (!acc[round]) acc[round] = [];
      acc[round].push(event);
      return acc;
    },
    {} as Record<number, DamageEvent[]>
  );

  // Get rounds in descending order (most recent first)
  const rounds = Object.keys(eventsByRound)
    .map(Number)
    .sort((a, b) => b - a);

  const getEventIcon = (type: DamageEvent['type']) => {
    switch (type) {
      case 'damage':
        return <Zap className="h-4 w-4 text-red-500" />;
      case 'healing':
        return <Heart className="h-4 w-4 text-green-500" />;
      case 'temp_hp':
        return <Shield className="h-4 w-4 text-blue-500" />;
    }
  };

  const getEventText = (event: DamageEvent) => {
    switch (event.type) {
      case 'damage':
        return (
          <>
            <span className="font-medium">{event.targetName}</span> took{' '}
            <span className="text-red-500 font-medium">{event.amount} damage</span>
            {event.source && <span className="text-ink-500"> ({event.source})</span>}
          </>
        );
      case 'healing':
        return (
          <>
            <span className="font-medium">{event.targetName}</span> healed for{' '}
            <span className="text-green-500 font-medium">{event.amount}</span>
            {event.source && <span className="text-ink-500"> ({event.source})</span>}
          </>
        );
      case 'temp_hp':
        return (
          <>
            <span className="font-medium">{event.targetName}</span> gained{' '}
            <span className="text-blue-500 font-medium">{event.amount} temp HP</span>
          </>
        );
    }
  };

  return (
    <div className="space-y-4 max-h-[400px] overflow-y-auto">
      {rounds.map((round) => (
        <div key={round}>
          <h4
            className={clsx(
              'text-sm font-semibold mb-2 sticky top-0 bg-white dark:bg-ink-900 py-1',
              round === currentRound && 'text-parchment-600'
            )}
          >
            Round {round}
            {round === currentRound && ' (Current)'}
          </h4>
          <div className="space-y-2 pl-2 border-l-2 border-ink-200 dark:border-ink-700">
            {eventsByRound[round].map((event) => (
              <div key={event.id} className="flex items-start gap-2 text-sm">
                {getEventIcon(event.type)}
                <span>{getEventText(event)}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

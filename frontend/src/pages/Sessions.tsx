import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Calendar, ArrowDown01, ArrowUp01 } from 'lucide-react';
import clsx from 'clsx';

import { getSessions } from '@services/api';

export default function Sessions() {
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc'); // Default newest first

  const { data: sessions, isLoading, error } = useQuery({
    queryKey: ['sessions'],
    queryFn: getSessions,
  });

  const sortedSessions = useMemo(() => {
    if (!sessions) return [];
    return [...sessions].sort((a, b) => {
      // Sort by date (chronological)
      const cmp = (a.date ?? '').localeCompare(b.date ?? '');
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [sessions, sortDir]);

  return (
    <div className="space-y-6">
      <header className="flex items-center gap-3">
        <Calendar className="h-8 w-8 text-purple-600" />
        <h1>Sessions</h1>
      </header>

      {/* Sort Controls */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-ink-500 dark:text-parchment-400">Sort:</span>
        <span className="text-sm">Date</span>
        <button
          type="button"
          onClick={() => setSortDir(sortDir === 'asc' ? 'desc' : 'asc')}
          className={clsx(
            'p-1.5 rounded-lg border border-parchment-200 dark:border-ink-600',
            'bg-white dark:bg-ink-800 hover:bg-parchment-100 dark:hover:bg-ink-700',
            'cursor-pointer transition-colors'
          )}
          title={sortDir === 'asc' ? 'Oldest first' : 'Newest first'}
        >
          {sortDir === 'asc' ? (
            <ArrowUp01 className="h-4 w-4" />
          ) : (
            <ArrowDown01 className="h-4 w-4" />
          )}
        </button>
      </div>

      {isLoading && <p>Loading sessions...</p>}
      {error && <p className="text-red-600">Error loading sessions</p>}

      {sortedSessions.length > 0 && (
        <div className="space-y-2">
          {sortedSessions.map((session) => (
            <Link
              key={session.number}
              to={`/sessions/${session.number}`}
              className="card card-link flex items-center gap-4 hover:border-parchment-400 dark:hover:border-ink-500 no-underline text-inherit"
            >
              <div className="flex-shrink-0 w-20 font-display font-semibold text-parchment-700 dark:text-parchment-400">
                Session {session.number}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">{session.title}</h3>
              </div>
              <div className="text-sm text-ink-500 dark:text-parchment-400">
                {session.date}
              </div>
              {session.in_game_date && (
                <div className="text-sm text-parchment-600 dark:text-parchment-500">
                  {session.in_game_date}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}

      {!isLoading && sortedSessions.length === 0 && (
        <p className="text-center text-ink-500 dark:text-parchment-400 py-8">
          No sessions found. Create one with the session manager.
        </p>
      )}
    </div>
  );
}

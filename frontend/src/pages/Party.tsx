import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Shield, ArrowDownAZ, ArrowUpAZ } from 'lucide-react';
import clsx from 'clsx';

import { getParty } from '@services/api';

export default function Party() {
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  const { data: party, isLoading, error } = useQuery({
    queryKey: ['party'],
    queryFn: getParty,
  });

  const sortedCharacters = useMemo(() => {
    if (!party?.characters) return [];
    return [...party.characters].sort((a, b) => {
      const cmp = a.name.localeCompare(b.name);
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [party?.characters, sortDir]);

  return (
    <div className="space-y-6">
      <header className="flex items-center gap-3">
        <Shield className="h-8 w-8 text-amber-600" />
        <h1>Party</h1>
      </header>

      {isLoading && <p>Loading party...</p>}
      {error && <p className="text-red-600">Error loading party</p>}

      {party && (
        <>
          <div className="flex gap-6 text-ink-600 dark:text-parchment-400">
            <span>Party Size: {party.size}</span>
            {party.average_level && (
              <span>Average Level: {party.average_level.toFixed(1)}</span>
            )}
          </div>

          {/* Sort Controls */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-ink-500 dark:text-parchment-400">Sort:</span>
            <span className="text-sm">Name</span>
            <button
              type="button"
              onClick={() => setSortDir(sortDir === 'asc' ? 'desc' : 'asc')}
              className={clsx(
                'p-1.5 rounded-lg border border-parchment-200 dark:border-ink-600',
                'bg-white dark:bg-ink-800 hover:bg-parchment-100 dark:hover:bg-ink-700',
                'cursor-pointer transition-colors'
              )}
              title={sortDir === 'asc' ? 'A to Z' : 'Z to A'}
            >
              {sortDir === 'asc' ? (
                <ArrowDownAZ className="h-4 w-4" />
              ) : (
                <ArrowUpAZ className="h-4 w-4" />
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sortedCharacters.map((char) => (
              <Link
                key={char.slug}
                to={`/party/characters/${char.slug}`}
                className="card card-link hover:border-parchment-400 dark:hover:border-ink-500 no-underline text-inherit"
              >
                <h3 className="font-display font-semibold text-lg mb-1">
                  {char.name}
                </h3>
                {char.player && (
                  <p className="text-sm text-ink-500 dark:text-parchment-400">
                    Player: {char.player}
                  </p>
                )}
                <div className="mt-2 flex flex-wrap gap-2">
                  {char.species && (
                    <span className="badge badge-neutral">{char.species}</span>
                  )}
                  {char.class_info && (
                    <span className="badge badge-neutral">{char.class_info}</span>
                  )}
                  {char.level && (
                    <span className="badge badge-ally">Level {char.level}</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </>
      )}

      {!isLoading && sortedCharacters.length === 0 && (
        <p className="text-center text-ink-500 dark:text-parchment-400 py-8">
          No party members found. Import characters from D&D Beyond.
        </p>
      )}
    </div>
  );
}

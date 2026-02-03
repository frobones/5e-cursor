import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Sword, Plus, Play, Filter, TrendingDown, TrendingUp, ArrowDownAZ, ArrowUpAZ, ArrowDown01, ArrowUp01 } from 'lucide-react';
import clsx from 'clsx';

import { getEncounters, getActiveCombats, getParty } from '@services/api';
import { calculateDifficulty } from '@/utils/encounterCalculator';

import type { EncounterListItem } from '@/types';

const difficultyColors: Record<string, string> = {
  Trivial: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
  trivial: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
  Easy: 'badge-ally',
  easy: 'badge-ally',
  Medium: 'badge-neutral',
  medium: 'badge-neutral',
  Hard: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  hard: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  Deadly: 'badge-enemy',
  deadly: 'badge-enemy',
};

const difficultyOrder = ['Trivial', 'Easy', 'Medium', 'Hard', 'Deadly'];

type SortField = 'created' | 'name' | 'difficulty' | 'current-difficulty' | 'level';

const sortFieldOptions: { value: SortField; label: string; type: 'alpha' | 'numeric' | 'difficulty' }[] = [
  { value: 'created', label: 'Date Created', type: 'numeric' },
  { value: 'name', label: 'Name', type: 'alpha' },
  { value: 'difficulty', label: 'Original Difficulty', type: 'difficulty' },
  { value: 'current-difficulty', label: 'Current Difficulty', type: 'difficulty' },
  { value: 'level', label: 'Party Level', type: 'numeric' },
];

// Calculate current difficulty for an encounter based on current party
function getCurrentDifficulty(enc: EncounterListItem, partyLevel: number, partySize: number): string {
  if (!enc.base_xp || enc.base_xp === 0) {
    return enc.difficulty; // Fall back to stored difficulty
  }
  const result = calculateDifficulty(enc.base_xp, enc.total_creatures, partyLevel, partySize);
  // Capitalize first letter to match stored format
  return result.difficulty.charAt(0).toUpperCase() + result.difficulty.slice(1);
}

export default function Encounters() {
  const [sortField, setSortField] = useState<SortField>('created');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [filterDifficulty, setFilterDifficulty] = useState<string>('all');

  const { data: encounters, isLoading, error } = useQuery({
    queryKey: ['encounters'],
    queryFn: getEncounters,
  });

  const { data: activeCombats } = useQuery({
    queryKey: ['activeCombats'],
    queryFn: getActiveCombats,
    staleTime: 0, // Always refetch on mount to ensure fresh combat status
  });

  const { data: party } = useQuery({
    queryKey: ['party'],
    queryFn: getParty,
  });

  // Current party stats (fallback to reasonable defaults)
  const currentPartyLevel = party?.average_level ? Math.round(party.average_level) : 1;
  const currentPartySize = party?.size ?? 4;

  // Get unique difficulties for filter dropdown
  const availableDifficulties = useMemo(() => {
    if (!encounters) return [];
    const difficulties = [...new Set(encounters.map((e) => e.difficulty))];
    return difficulties.sort((a, b) => difficultyOrder.indexOf(a) - difficultyOrder.indexOf(b));
  }, [encounters]);

  // Sort and filter encounters
  const sortedEncounters = useMemo(() => {
    if (!encounters) return [];

    let filtered = encounters;

    // Apply difficulty filter
    if (filterDifficulty !== 'all') {
      filtered = filtered.filter((e) => e.difficulty === filterDifficulty);
    }

    // Apply sorting
    return [...filtered].sort((a, b) => {
      const currentDiffA = getCurrentDifficulty(a, currentPartyLevel, currentPartySize);
      const currentDiffB = getCurrentDifficulty(b, currentPartyLevel, currentPartySize);

      let cmp = 0;
      switch (sortField) {
        case 'created':
          cmp = (a.created || '').localeCompare(b.created || '');
          break;
        case 'name':
          cmp = a.name.localeCompare(b.name);
          break;
        case 'difficulty':
          cmp = difficultyOrder.indexOf(a.difficulty) - difficultyOrder.indexOf(b.difficulty);
          break;
        case 'current-difficulty':
          cmp = difficultyOrder.indexOf(currentDiffA) - difficultyOrder.indexOf(currentDiffB);
          break;
        case 'level':
          cmp = a.party_level - b.party_level;
          break;
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [encounters, sortField, sortDir, filterDifficulty, currentPartyLevel, currentPartySize]);

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Sword className="h-8 w-8 text-red-600" />
          <h1>Encounters</h1>
        </div>
        <Link to="/encounters/new" className="btn btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Build New Encounter
        </Link>
      </header>

      {/* Sort and Filter Controls */}
      {encounters && encounters.length > 0 && (
        <div className="flex flex-wrap gap-4 items-center">
          {/* Sort Controls */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-ink-500 dark:text-parchment-400">Sort:</span>
            <select
              value={sortField}
              onChange={(e) => setSortField(e.target.value as SortField)}
              className="px-3 py-1.5 border border-parchment-200 dark:border-ink-600 rounded-lg bg-white dark:bg-ink-800 text-sm cursor-pointer"
            >
              {sortFieldOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => setSortDir(sortDir === 'asc' ? 'desc' : 'asc')}
              className={clsx(
                'p-1.5 rounded-lg border border-parchment-200 dark:border-ink-600',
                'bg-white dark:bg-ink-800 hover:bg-parchment-100 dark:hover:bg-ink-700',
                'cursor-pointer transition-colors'
              )}
              title={sortDir === 'asc' ? 'Ascending' : 'Descending'}
            >
              {sortFieldOptions.find(o => o.value === sortField)?.type === 'alpha' ? (
                sortDir === 'asc' ? <ArrowDownAZ className="h-4 w-4" /> : <ArrowUpAZ className="h-4 w-4" />
              ) : (
                sortDir === 'asc' ? <ArrowUp01 className="h-4 w-4" /> : <ArrowDown01 className="h-4 w-4" />
              )}
            </button>
          </div>

          <div className="h-6 w-px bg-parchment-200 dark:bg-ink-600" />

          {/* Difficulty Filter */}
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-ink-400" />
            <select
              value={filterDifficulty}
              onChange={(e) => setFilterDifficulty(e.target.value)}
              className="px-3 py-1.5 border border-parchment-200 dark:border-ink-600 rounded-lg bg-white dark:bg-ink-800 text-sm cursor-pointer"
            >
              <option value="all">All Difficulties</option>
              {availableDifficulties.map((diff) => (
                <option key={diff} value={diff}>
                  {diff}
                </option>
              ))}
            </select>
          </div>

          {/* Results Count */}
          <span className="text-sm text-ink-500 dark:text-parchment-500">
            {sortedEncounters.length} encounter{sortedEncounters.length !== 1 ? 's' : ''}
            {filterDifficulty !== 'all' && ` (${filterDifficulty})`}
          </span>
        </div>
      )}

      {isLoading && <p>Loading encounters...</p>}
      {error && <p className="text-red-600">Error loading encounters</p>}

      {/* Party info banner */}
      {party && (
        <div className="text-sm text-ink-500 dark:text-parchment-500 bg-parchment-100 dark:bg-ink-800 px-4 py-2 rounded-lg">
          Current party: {party.size} characters, level {currentPartyLevel}
        </div>
      )}

      {sortedEncounters.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedEncounters.map((enc) => {
            const hasActiveCombat = activeCombats?.includes(enc.slug) ?? false;
            const currentDiff = getCurrentDifficulty(enc, currentPartyLevel, currentPartySize);
            const originalDiffIndex = difficultyOrder.indexOf(enc.difficulty);
            const currentDiffIndex = difficultyOrder.indexOf(currentDiff);
            const diffChanged = currentDiff !== enc.difficulty;
            const isEasier = currentDiffIndex < originalDiffIndex;
            const isHarder = currentDiffIndex > originalDiffIndex;

            return (
              <Link
                key={enc.slug}
                to={`/encounters/${enc.slug}`}
                className={clsx(
                  'card card-link hover:border-parchment-400 dark:hover:border-ink-500 no-underline text-inherit',
                  hasActiveCombat && 'border-orange-400 dark:border-orange-600'
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-display font-semibold text-lg">
                    {enc.name}
                  </h3>
                  <div className="flex flex-col items-end gap-1">
                    {hasActiveCombat && (
                      <span className="badge bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300 flex items-center gap-1">
                        <Play className="h-3 w-3" />
                        In Combat
                      </span>
                    )}
                    {/* Current difficulty badge */}
                    <span className={clsx('badge', difficultyColors[currentDiff] || 'badge-neutral')}>
                      {currentDiff}
                    </span>
                    {/* Show change indicator if difficulty changed */}
                    {diffChanged && (
                      <span className="flex items-center gap-1 text-xs">
                        {isEasier && (
                          <>
                            <TrendingDown className="h-3 w-3 text-green-600" />
                            <span className="text-green-600">was {enc.difficulty}</span>
                          </>
                        )}
                        {isHarder && (
                          <>
                            <TrendingUp className="h-3 w-3 text-red-600" />
                            <span className="text-red-600">was {enc.difficulty}</span>
                          </>
                        )}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-sm text-ink-600 dark:text-parchment-400">
                  {enc.total_creatures} creature{enc.total_creatures !== 1 ? 's' : ''}
                </p>
                <div className="flex justify-between text-sm text-ink-500 dark:text-parchment-500">
                  <span>Built for: Lv{enc.party_level} × {enc.party_size}</span>
                  {enc.created && (
                    <span>{new Date(enc.created).toLocaleDateString()}</span>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {encounters && encounters.length > 0 && sortedEncounters.length === 0 && (
        <p className="text-center text-ink-500 dark:text-parchment-400 py-8">
          No encounters match your filter.
        </p>
      )}

      {encounters?.length === 0 && (
        <p className="text-center text-ink-500 dark:text-parchment-400 py-8">
          No encounters saved. Build one with the encounter builder.
        </p>
      )}
    </div>
  );
}

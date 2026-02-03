import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Plus, Filter, Eye, X } from 'lucide-react';
import clsx from 'clsx';

import { getReference, getCreatureStats } from '@services/api';
import { getXPForCR } from '@/utils/encounterCalculator';
import { CreatureStatsPanel } from '@components/combat';

import type { ReferenceListItem, EncounterBuilderCreature } from '@/types';

interface CreatureSelectorProps {
  onAddCreature: (creature: EncounterBuilderCreature) => void;
}

const CR_OPTIONS = [
  { label: 'All CRs', value: '' },
  { label: 'CR 0-1/4', value: '0,1/8,1/4' },
  { label: 'CR 1/2-1', value: '1/2,1' },
  { label: 'CR 2-4', value: '2,3,4' },
  { label: 'CR 5-10', value: '5,6,7,8,9,10' },
  { label: 'CR 11-16', value: '11,12,13,14,15,16' },
  { label: 'CR 17+', value: '17,18,19,20,21,22,23,24,25,26,27,28,29,30' },
];

export default function CreatureSelector({ onAddCreature }: CreatureSelectorProps) {
  const [search, setSearch] = useState('');
  const [crFilter, setCrFilter] = useState('');
  const [selectedCreature, setSelectedCreature] = useState<ReferenceListItem | null>(null);

  const { data: creatures, isLoading } = useQuery({
    queryKey: ['reference', 'creatures'],
    queryFn: () => getReference('creatures'),
  });

  // Fetch stats for selected creature
  const { data: creatureStats, isLoading: isLoadingStats } = useQuery({
    queryKey: ['creatureStats', selectedCreature?.slug],
    queryFn: () => getCreatureStats(selectedCreature!.slug),
    enabled: !!selectedCreature,
  });

  // Filter creatures by search and CR
  const filteredCreatures = (creatures ?? []).filter((creature: ReferenceListItem) => {
    // Search filter
    if (search && !creature.name.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }

    // CR filter
    if (crFilter) {
      const allowedCRs = crFilter.split(',');
      const creatureCR = creature.metadata?.cr?.toString() ?? '';
      if (!allowedCRs.includes(creatureCR)) {
        return false;
      }
    }

    return true;
  });

  const handleAddCreature = (creature: ReferenceListItem) => {
    const cr = creature.metadata?.cr?.toString() ?? '0';
    const xp = getXPForCR(cr);

    onAddCreature({
      name: creature.name,
      slug: creature.slug,
      cr,
      xp,
      count: 1,
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-400" />
          <input
            type="text"
            placeholder="Search creatures..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-ink-200 dark:border-ink-700 rounded-lg bg-white dark:bg-ink-900 focus:outline-none focus:ring-2 focus:ring-parchment-500"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-400" />
          <select
            value={crFilter}
            onChange={(e) => setCrFilter(e.target.value)}
            className="pl-10 pr-8 py-2 border border-ink-200 dark:border-ink-700 rounded-lg bg-white dark:bg-ink-900 focus:outline-none focus:ring-2 focus:ring-parchment-500 appearance-none cursor-pointer"
          >
            {CR_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex gap-4">
        {/* Creature List */}
        <div
          className={clsx(
            'overflow-y-auto border border-ink-200 dark:border-ink-700 rounded-lg transition-all',
            selectedCreature ? 'w-1/2 h-[500px]' : 'flex-1 h-[400px]'
          )}
        >
          {isLoading ? (
            <div className="p-4 text-center text-ink-500">Loading creatures...</div>
          ) : filteredCreatures.length === 0 ? (
            <div className="p-4 text-center text-ink-500">
              {search || crFilter ? 'No creatures match your filters' : 'No creatures found'}
            </div>
          ) : (
            <ul className="divide-y divide-ink-100 dark:divide-ink-800">
              {filteredCreatures.slice(0, 100).map((creature: ReferenceListItem) => {
                const cr = creature.metadata?.cr?.toString() ?? '0';
                const xp = getXPForCR(cr);
                const isSelected = selectedCreature?.slug === creature.slug;

                return (
                  <li
                    key={creature.slug}
                    className={clsx(
                      'flex items-center justify-between p-3 transition-colors',
                      isSelected
                        ? 'bg-parchment-100 dark:bg-ink-700'
                        : 'hover:bg-parchment-50 dark:hover:bg-ink-800'
                    )}
                  >
                    <div
                      className="flex-1 cursor-pointer"
                      onClick={() => setSelectedCreature(isSelected ? null : creature)}
                    >
                      <div className="font-medium">{creature.name}</div>
                      <div className="text-sm text-ink-500">
                        CR {cr} &bull; {xp.toLocaleString()} XP
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        className={clsx(
                          'p-2 rounded-full transition-colors',
                          isSelected
                            ? 'bg-parchment-200 dark:bg-ink-600'
                            : 'hover:bg-parchment-200 dark:hover:bg-ink-700'
                        )}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedCreature(isSelected ? null : creature);
                        }}
                        title="View stats"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        type="button"
                        className="p-2 rounded-full hover:bg-parchment-200 dark:hover:bg-ink-700 transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAddCreature(creature);
                        }}
                        title="Add to encounter"
                      >
                        <Plus className="h-4 w-4" />
                      </button>
                    </div>
                  </li>
                );
              })}
              {filteredCreatures.length > 100 && (
                <li className="p-3 text-center text-ink-500 text-sm">
                  Showing first 100 of {filteredCreatures.length} creatures. Refine your search.
                </li>
              )}
            </ul>
          )}
        </div>

        {/* Stats Panel */}
        {selectedCreature && (
          <div className="w-1/2 h-[500px] overflow-y-auto border border-ink-200 dark:border-ink-700 rounded-lg p-4 bg-parchment-50 dark:bg-ink-800">
            <div className="flex justify-between items-start mb-4">
              <button
                type="button"
                onClick={() => {
                  handleAddCreature(selectedCreature);
                }}
                className="btn btn-primary btn-sm flex items-center gap-1"
              >
                <Plus className="h-4 w-4" />
                Add to Encounter
              </button>
              <button
                type="button"
                onClick={() => setSelectedCreature(null)}
                className="p-1 rounded-full hover:bg-ink-200 dark:hover:bg-ink-700 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {isLoadingStats ? (
              <div className="text-center text-ink-500 py-8">Loading stats...</div>
            ) : creatureStats ? (
              <CreatureStatsPanel stats={creatureStats} />
            ) : (
              <div className="text-center text-ink-500 py-8">
                Unable to load creature stats
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

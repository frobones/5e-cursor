import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Users, Heart, Circle, Swords } from 'lucide-react';
import clsx from 'clsx';

import { FilterBar } from '@components/ui';
import { getNPCs } from '@services/api';

import type { SortOption } from '@components/ui';
import type { Role } from '@/types';

const roleFilters: { value: string | null; label: string }[] = [
  { value: null, label: 'All' },
  { value: 'ally', label: 'Allies' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'enemy', label: 'Enemies' },
];

const roleIcons: Record<Role, React.ComponentType<{ className?: string }>> = {
  ally: Heart,
  neutral: Circle,
  enemy: Swords,
  unknown: Circle,
};

const roleBadgeClass: Record<Role, string> = {
  ally: 'badge-ally',
  neutral: 'badge-neutral',
  enemy: 'badge-enemy',
  unknown: 'badge-neutral',
};

const sortOptions: SortOption[] = [
  { value: 'name', label: 'Name', type: 'alpha' },
  { value: 'role', label: 'Role', type: 'alpha' },
  { value: 'location', label: 'Location', type: 'alpha' },
  { value: 'first_seen', label: 'First Seen', type: 'alpha' },
];

export default function NPCs() {
  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const [sortField, setSortField] = useState('name');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  const { data: npcs, isLoading, error } = useQuery({
    queryKey: ['npcs', roleFilter],
    queryFn: () => getNPCs(roleFilter || undefined),
  });

  const sortedNpcs = useMemo(() => {
    if (!npcs) return [];
    return [...npcs].sort((a, b) => {
      const aVal = a[sortField as keyof typeof a] ?? '';
      const bVal = b[sortField as keyof typeof b] ?? '';
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [npcs, sortField, sortDir]);

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="h-8 w-8 text-green-600" />
          <h1>NPCs</h1>
        </div>
      </header>

      {/* Role Filters */}
      <div className="flex gap-2">
        {roleFilters.map(({ value, label }) => (
          <button
            key={label}
            onClick={() => setRoleFilter(value)}
            className={clsx(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              roleFilter === value
                ? 'bg-parchment-600 text-white'
                : 'bg-parchment-100 text-ink-700 hover:bg-parchment-200 dark:bg-ink-700 dark:text-parchment-200 dark:hover:bg-ink-600'
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Sort Controls */}
      <FilterBar
        sortOptions={sortOptions}
        sortValue={sortField}
        sortDirection={sortDir}
        onSortChange={setSortField}
        onDirectionChange={setSortDir}
      />

      {/* Loading/Error states */}
      {isLoading && <p>Loading NPCs...</p>}
      {error && <p className="text-red-600">Error loading NPCs</p>}

      {/* NPC Grid */}
      {sortedNpcs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedNpcs.map((npc) => {
            const Icon = roleIcons[npc.role] || Circle;
            return (
              <Link
                key={npc.slug}
                to={`/npcs/${npc.slug}`}
                className="card card-link hover:border-parchment-400 dark:hover:border-ink-500 no-underline text-inherit"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-display font-semibold text-lg">
                    {npc.name}
                  </h3>
                  <span className={clsx('badge', roleBadgeClass[npc.role])}>
                    <Icon className="h-3 w-3 mr-1" />
                    {npc.role}
                  </span>
                </div>
                {npc.occupation && (
                  <p className="text-ink-600 dark:text-parchment-400">
                    {npc.occupation}
                  </p>
                )}
                {npc.location && (
                  <p className="text-sm text-ink-500 dark:text-parchment-500 mt-1">
                    📍 {npc.location}
                  </p>
                )}
                {npc.first_seen && (
                  <p className="text-sm text-parchment-600 dark:text-parchment-500 mt-1">
                    First seen: {npc.first_seen}
                  </p>
                )}
              </Link>
            );
          })}
        </div>
      )}

      {!isLoading && sortedNpcs.length === 0 && (
        <p className="text-center text-ink-500 dark:text-parchment-400 py-8">
          No NPCs found. Add some with the campaign manager.
        </p>
      )}
    </div>
  );
}

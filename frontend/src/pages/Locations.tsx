import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { MapPin } from 'lucide-react';

import { FilterBar } from '@components/ui';
import { getLocations } from '@services/api';

import type { SortOption, FilterConfig } from '@components/ui';

const sortOptions: SortOption[] = [
  { value: 'name', label: 'Name', type: 'alpha' },
  { value: 'type', label: 'Type', type: 'alpha' },
  { value: 'region', label: 'Region', type: 'alpha' },
  { value: 'discovered', label: 'Discovered', type: 'alpha' },
];

export default function Locations() {
  const [sortField, setSortField] = useState('name');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [typeFilter, setTypeFilter] = useState('');
  const [regionFilter, setRegionFilter] = useState('');

  const { data: locations, isLoading, error } = useQuery({
    queryKey: ['locations'],
    queryFn: () => getLocations(),
  });

  // Build unique type and region options from data
  const { typeOptions, regionOptions } = useMemo(() => {
    if (!locations) return { typeOptions: [], regionOptions: [] };

    const types = new Set<string>();
    const regions = new Set<string>();

    locations.forEach((loc) => {
      if (loc.type) types.add(loc.type);
      if (loc.region) regions.add(loc.region);
    });

    return {
      typeOptions: [
        { value: '', label: 'All Types' },
        ...[...types].sort().map((t) => ({ value: t, label: t })),
      ],
      regionOptions: [
        { value: '', label: 'All Regions' },
        ...[...regions].sort().map((r) => ({ value: r, label: r })),
      ],
    };
  }, [locations]);

  // Filter and sort locations
  const filteredLocations = useMemo(() => {
    if (!locations) return [];

    let result = [...locations];

    // Apply filters
    if (typeFilter) {
      result = result.filter((loc) => loc.type === typeFilter);
    }
    if (regionFilter) {
      result = result.filter((loc) => loc.region === regionFilter);
    }

    // Sort
    result.sort((a, b) => {
      const aVal = a[sortField as keyof typeof a] ?? '';
      const bVal = b[sortField as keyof typeof b] ?? '';
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return result;
  }, [locations, typeFilter, regionFilter, sortField, sortDir]);

  const filters: FilterConfig[] = [
    {
      label: 'Type',
      options: typeOptions,
      value: typeFilter,
      onChange: setTypeFilter,
    },
    {
      label: 'Region',
      options: regionOptions,
      value: regionFilter,
      onChange: setRegionFilter,
    },
  ];

  const hasActiveFilters = typeFilter !== '' || regionFilter !== '';

  const clearFilters = () => {
    setTypeFilter('');
    setRegionFilter('');
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center gap-3">
        <MapPin className="h-8 w-8 text-blue-600" />
        <h1>Locations</h1>
      </header>

      {/* Sort and Filter Controls */}
      <FilterBar
        sortOptions={sortOptions}
        sortValue={sortField}
        sortDirection={sortDir}
        onSortChange={setSortField}
        onDirectionChange={setSortDir}
        filters={filters}
        showClear={hasActiveFilters}
        onClearFilters={clearFilters}
      />

      {isLoading && <p>Loading locations...</p>}
      {error && <p className="text-red-600">Error loading locations</p>}

      {filteredLocations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredLocations.map((loc) => (
            <Link
              key={loc.slug}
              to={`/locations/${loc.slug}`}
              className="card card-link hover:border-parchment-400 dark:hover:border-ink-500 no-underline text-inherit"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-display font-semibold text-lg">
                  {loc.name}
                </h3>
                <span className="badge badge-neutral">{loc.type}</span>
              </div>
              {loc.region && (
                <p className="text-ink-600 dark:text-parchment-400">
                  {loc.region}
                </p>
              )}
              {loc.discovered && (
                <p className="text-sm text-parchment-600 dark:text-parchment-500 mt-1">
                  Discovered: {loc.discovered}
                </p>
              )}
            </Link>
          ))}
        </div>
      )}

      {!isLoading && filteredLocations.length === 0 && (
        <p className="text-center text-ink-500 dark:text-parchment-400 py-8">
          No locations found{hasActiveFilters ? ' matching filters' : ''}. 
          {!hasActiveFilters && ' Add some with the campaign manager.'}
        </p>
      )}
    </div>
  );
}

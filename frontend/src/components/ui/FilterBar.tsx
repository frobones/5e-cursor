import { ArrowDownAZ, ArrowUpAZ, ArrowDown01, ArrowUp01, Filter } from 'lucide-react';
import clsx from 'clsx';

export interface SortOption {
  value: string;
  label: string;
  type?: 'alpha' | 'numeric';
}

export interface FilterOption {
  value: string;
  label: string;
}

export interface FilterConfig {
  label: string;
  options: FilterOption[];
  value: string;
  onChange: (value: string) => void;
}

interface FilterBarProps {
  sortOptions: SortOption[];
  sortValue: string;
  sortDirection: 'asc' | 'desc';
  onSortChange: (value: string) => void;
  onDirectionChange: (dir: 'asc' | 'desc') => void;
  filters?: FilterConfig[];
  onClearFilters?: () => void;
  showClear?: boolean;
}

export default function FilterBar({
  sortOptions,
  sortValue,
  sortDirection,
  onSortChange,
  onDirectionChange,
  filters = [],
  onClearFilters,
  showClear = false,
}: FilterBarProps) {
  const currentSortOption = sortOptions.find((opt) => opt.value === sortValue);
  const isNumeric = currentSortOption?.type === 'numeric';

  const toggleDirection = () => {
    onDirectionChange(sortDirection === 'asc' ? 'desc' : 'asc');
  };

  const DirectionIcon =
    isNumeric
      ? sortDirection === 'asc'
        ? ArrowUp01
        : ArrowDown01
      : sortDirection === 'asc'
        ? ArrowDownAZ
        : ArrowUpAZ;

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Sort controls */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-ink-500 dark:text-parchment-400">Sort:</span>
        <select
          value={sortValue}
          onChange={(e) => onSortChange(e.target.value)}
          className="px-3 py-1.5 rounded-lg border border-parchment-200 dark:border-ink-600 bg-white dark:bg-ink-800 text-sm cursor-pointer"
        >
          {sortOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={toggleDirection}
          className={clsx(
            'p-1.5 rounded-lg border border-parchment-200 dark:border-ink-600',
            'bg-white dark:bg-ink-800 hover:bg-parchment-100 dark:hover:bg-ink-700',
            'cursor-pointer transition-colors'
          )}
          title={sortDirection === 'asc' ? 'Ascending' : 'Descending'}
        >
          <DirectionIcon className="h-4 w-4" />
        </button>
      </div>

      {/* Filter controls */}
      {filters.length > 0 && (
        <>
          <div className="h-6 w-px bg-parchment-200 dark:bg-ink-600" />
          <Filter className="h-4 w-4 text-ink-400" />
          {filters.map((filter) => (
            <div key={filter.label} className="flex items-center gap-2">
              <span className="text-sm text-ink-500 dark:text-parchment-400">
                {filter.label}:
              </span>
              <select
                value={filter.value}
                onChange={(e) => filter.onChange(e.target.value)}
                className="px-3 py-1.5 rounded-lg border border-parchment-200 dark:border-ink-600 bg-white dark:bg-ink-800 text-sm cursor-pointer"
              >
                {filter.options.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </>
      )}

      {/* Clear button */}
      {showClear && onClearFilters && (
        <button
          type="button"
          onClick={onClearFilters}
          className="text-sm text-parchment-600 hover:text-parchment-800 dark:text-parchment-400 cursor-pointer underline underline-offset-2"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}

import { useState, useEffect, useRef, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { BookOpen, Wand2, Skull, Gem, ScrollText, Filter, Loader2, ArrowDownAZ, ArrowUpAZ } from 'lucide-react';
import clsx from 'clsx';

import { getReferenceIndex, getReferenceByType } from '@services/api';

import type { ReferenceListItem } from '@/types';

const tabs = [
  { id: 'spells', label: 'Spells', icon: Wand2 },
  { id: 'creatures', label: 'Creatures', icon: Skull },
  { id: 'items', label: 'Items', icon: Gem },
  { id: 'rules', label: 'Rules', icon: ScrollText },
];

// Spell levels
const spellLevels = [
  { value: '', label: 'All Levels' },
  { value: '0', label: 'Cantrip' },
  { value: '1', label: '1st Level' },
  { value: '2', label: '2nd Level' },
  { value: '3', label: '3rd Level' },
  { value: '4', label: '4th Level' },
  { value: '5', label: '5th Level' },
  { value: '6', label: '6th Level' },
  { value: '7', label: '7th Level' },
  { value: '8', label: '8th Level' },
  { value: '9', label: '9th Level' },
];

// Creature CRs
const creatureCRs = [
  { value: '', label: 'All CRs' },
  { value: '0', label: 'CR 0' },
  { value: '1/8', label: 'CR 1/8' },
  { value: '1/4', label: 'CR 1/4' },
  { value: '1/2', label: 'CR 1/2' },
  { value: '1', label: 'CR 1' },
  { value: '2', label: 'CR 2' },
  { value: '3', label: 'CR 3' },
  { value: '4', label: 'CR 4' },
  { value: '5', label: 'CR 5' },
  { value: '6', label: 'CR 6' },
  { value: '7', label: 'CR 7' },
  { value: '8', label: 'CR 8' },
  { value: '9', label: 'CR 9' },
  { value: '10', label: 'CR 10' },
  { value: '11', label: 'CR 11' },
  { value: '12', label: 'CR 12' },
  { value: '13', label: 'CR 13' },
  { value: '14', label: 'CR 14' },
  { value: '15', label: 'CR 15' },
  { value: '16+', label: 'CR 16+' },
];

// Item rarities
const itemRarities = [
  { value: '', label: 'All Rarities' },
  { value: 'common', label: 'Common' },
  { value: 'uncommon', label: 'Uncommon' },
  { value: 'rare', label: 'Rare' },
  { value: 'very rare', label: 'Very Rare' },
  { value: 'legendary', label: 'Legendary' },
  { value: 'artifact', label: 'Artifact' },
];

const ITEMS_PER_PAGE = 50;

export default function Reference() {
  const { type: urlType } = useParams<{ type?: string }>();
  const [activeTab, setActiveTab] = useState(urlType || 'spells');
  
  // Filter states
  const [spellLevel, setSpellLevel] = useState('');
  const [creatureCR, setCreatureCR] = useState('');
  const [itemRarity, setItemRarity] = useState('');

  // Sort state (name only)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  // Pagination state
  const [offset, setOffset] = useState(0);
  const [allItems, setAllItems] = useState<ReferenceListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  // Track previous urlType to detect actual URL navigation (not just activeTab changes)
  const prevUrlTypeRef = useRef(urlType);

  // Sync activeTab with URL parameter only when URL actually changes (navigation)
  useEffect(() => {
    // Only sync if urlType changed from previous value (real navigation happened)
    if (urlType !== prevUrlTypeRef.current) {
      prevUrlTypeRef.current = urlType;
      if (urlType && urlType !== activeTab) {
        setActiveTab(urlType);
        setSpellLevel('');
        setCreatureCR('');
        setItemRarity('');
        setOffset(0);
        setAllItems([]);
      }
    }
  }, [urlType, activeTab]);

  const { data: index } = useQuery({
    queryKey: ['reference-index'],
    queryFn: getReferenceIndex,
  });

  // Build filter options based on active tab
  const filterOptions = () => {
    if (activeTab === 'spells' && spellLevel) {
      return { level: parseInt(spellLevel) };
    }
    if (activeTab === 'creatures' && creatureCR) {
      return { cr: creatureCR };
    }
    if (activeTab === 'items' && itemRarity) {
      return { rarity: itemRarity };
    }
    return {};
  };

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['reference', activeTab, spellLevel, creatureCR, itemRarity, offset],
    queryFn: () => getReferenceByType(activeTab, { ...filterOptions(), offset, limit: ITEMS_PER_PAGE }),
  });

  // Update accumulated items when data changes
  useEffect(() => {
    if (data) {
      if (offset === 0) {
        // New query - replace items
        setAllItems(data.items);
      } else {
        // Load more - append items
        setAllItems((prev) => [...prev, ...data.items]);
      }
      setTotal(data.total);
      setHasMore(data.has_more);
    }
  }, [data, offset]);

  const handleLoadMore = () => {
    setOffset((prev) => prev + ITEMS_PER_PAGE);
  };

  // Sort items client-side by name
  const sortedItems = useMemo(() => {
    if (!allItems.length) return [];
    return [...allItems].sort((a, b) => {
      const cmp = a.name.localeCompare(b.name);
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [allItems, sortDir]);

  // Reset filters and pagination when switching tabs
  const handleTabChange = (tabId: string) => {
    // Don't reset if clicking the same tab
    if (tabId === activeTab) return;

    setActiveTab(tabId);
    setSpellLevel('');
    setCreatureCR('');
    setItemRarity('');
    setSortDir('asc');
    setOffset(0);
    setAllItems([]);
  };

  // Track previous filter values to detect actual changes
  const prevFiltersRef = useRef({ spellLevel: '', creatureCR: '', itemRarity: '' });

  // Reset pagination when filters actually change (not on initial mount)
  useEffect(() => {
    const prev = prevFiltersRef.current;
    const filtersChanged = 
      prev.spellLevel !== spellLevel || 
      prev.creatureCR !== creatureCR || 
      prev.itemRarity !== itemRarity;

    // Only reset if filters actually changed from a non-empty previous value
    if (filtersChanged && (prev.spellLevel !== '' || prev.creatureCR !== '' || prev.itemRarity !== '')) {
      setOffset(0);
      setAllItems([]);
    }

    // Update ref for next comparison
    prevFiltersRef.current = { spellLevel, creatureCR, itemRarity };
  }, [spellLevel, creatureCR, itemRarity]);

  return (
    <div className="space-y-6">
      <header className="flex items-center gap-3">
        <BookOpen className="h-8 w-8 text-indigo-600" />
        <h1>Reference</h1>
      </header>

      {/* Stats */}
      {index && (
        <div className="text-sm text-ink-600 dark:text-parchment-400">
          {index.total_entries.toLocaleString()} total entries
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-parchment-200 dark:border-ink-700">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => handleTabChange(id)}
            type="button"
            className={clsx(
              'flex items-center gap-2 px-4 py-2 border-b-2 transition-colors cursor-pointer',
              activeTab === id
                ? 'border-parchment-600 text-parchment-700 dark:text-parchment-300'
                : 'border-transparent text-ink-500 hover:text-ink-700 dark:text-parchment-400'
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
            {index?.by_type[id] && (
              <span className="text-xs text-ink-400">
                ({index.by_type[id]})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Sort and Filters */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Sort controls */}
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
            title={sortDir === 'asc' ? 'Ascending' : 'Descending'}
          >
            {sortDir === 'asc' ? (
              <ArrowDownAZ className="h-4 w-4" />
            ) : (
              <ArrowUpAZ className="h-4 w-4" />
            )}
          </button>
        </div>

        <div className="h-6 w-px bg-parchment-200 dark:bg-ink-600" />

        <Filter className="h-4 w-4 text-ink-400" />
        
        {activeTab === 'spells' && (
          <select
            value={spellLevel}
            onChange={(e) => setSpellLevel(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-parchment-200 dark:border-ink-600 bg-white dark:bg-ink-800 text-sm cursor-pointer"
          >
            {spellLevels.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        )}

        {activeTab === 'creatures' && (
          <select
            value={creatureCR}
            onChange={(e) => setCreatureCR(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-parchment-200 dark:border-ink-600 bg-white dark:bg-ink-800 text-sm cursor-pointer"
          >
            {creatureCRs.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        )}

        {activeTab === 'items' && (
          <select
            value={itemRarity}
            onChange={(e) => setItemRarity(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-parchment-200 dark:border-ink-600 bg-white dark:bg-ink-800 text-sm cursor-pointer"
          >
            {itemRarities.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        )}

        {(spellLevel || creatureCR || itemRarity) && (
          <button
            onClick={() => {
              setSpellLevel('');
              setCreatureCR('');
              setItemRarity('');
            }}
            className="text-sm text-parchment-600 hover:text-parchment-800 dark:text-parchment-400 cursor-pointer underline underline-offset-2"
          >
            Clear filter
          </button>
        )}
      </div>

      {/* Content */}
      {isLoading && offset === 0 && <p>Loading...</p>}

      {sortedItems.length > 0 && (
        <>
          {/* Results count */}
          <div className="text-sm text-ink-500 dark:text-parchment-400">
            Showing {sortedItems.length} of {total} {activeTab}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {sortedItems.map((item) => (
              <Link
                key={item.slug}
                to={`/reference/${activeTab}/${item.slug}`}
                className="card card-link py-3 hover:border-parchment-400 dark:hover:border-ink-500 no-underline text-inherit"
              >
                <h3 className="font-semibold">{item.name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  {item.source && (
                    <span className="text-xs text-ink-500 dark:text-parchment-500">
                      {item.source}
                    </span>
                  )}
                  {/* Show metadata badges */}
                  {typeof item.metadata.level === 'number' ? (
                    <span className="badge badge-neutral text-xs">
                      {item.metadata.level === 0 ? 'Cantrip' : `Level ${item.metadata.level}`}
                    </span>
                  ) : null}
                  {item.metadata.cr ? (
                    <span className="badge badge-neutral text-xs">
                      CR {String(item.metadata.cr)}
                    </span>
                  ) : null}
                  {item.metadata.rarity ? (
                    <span className="badge badge-neutral text-xs capitalize">
                      {String(item.metadata.rarity)}
                    </span>
                  ) : null}
                </div>
              </Link>
            ))}
          </div>

          {/* Load More button */}
          {hasMore && (
            <div className="flex justify-center pt-4">
              <button
                onClick={handleLoadMore}
                disabled={isFetching}
                className="btn btn-secondary flex items-center gap-2"
              >
                {isFetching ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  `Load More (${total - sortedItems.length} remaining)`
                )}
              </button>
            </div>
          )}
        </>
      )}

      {!isLoading && sortedItems.length === 0 && (
        <p className="text-center text-ink-500 dark:text-parchment-400 py-8">
          No {activeTab} found{spellLevel || creatureCR || itemRarity ? ' with selected filter' : ''}. 
          {!index?.total_entries && ' Extract reference data with: make'}
        </p>
      )}
    </div>
  );
}

import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Command } from 'cmdk';
import {
  Search,
  Users,
  MapPin,
  Calendar,
  Shield,
  Sword,
  BookOpen,
  X,
} from 'lucide-react';
import { search } from '@services/api';
import type { SearchResult } from '@/types';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const typeIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  npc: Users,
  location: MapPin,
  session: Calendar,
  character: Shield,
  encounter: Sword,
  spells: BookOpen,
  creatures: BookOpen,
  items: BookOpen,
  rules: BookOpen,
};

export default function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Search when query changes
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const response = await search(query, 20);
        setResults(response.results);
      } catch (err) {
        console.error('Search error:', err);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  // Handle selection
  const handleSelect = useCallback(
    (path: string) => {
      navigate(path);
      onClose();
      setQuery('');
    },
    [navigate, onClose]
  );

  // Close on escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-ink-900/50 dark:bg-ink-950/70"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-xl mx-4 bg-white dark:bg-ink-800 rounded-xl shadow-2xl overflow-hidden">
        <Command
          className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-ink-500"
          shouldFilter={false}
        >
          {/* Input */}
          <div className="flex items-center border-b border-parchment-200 dark:border-ink-700 px-4">
            <Search className="h-5 w-5 text-ink-400 mr-3" />
            <Command.Input
              value={query}
              onValueChange={setQuery}
              placeholder="Search campaign and reference data..."
              className="flex-1 py-4 text-lg bg-transparent outline-none placeholder:text-ink-400"
              autoFocus
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="p-1 hover:bg-parchment-100 dark:hover:bg-ink-700 rounded"
              >
                <X className="h-4 w-4 text-ink-400" />
              </button>
            )}
          </div>

          {/* Results */}
          <Command.List className="max-h-[60vh] overflow-y-auto p-2">
            {isLoading && (
              <Command.Loading className="py-6 text-center text-ink-500">
                Searching...
              </Command.Loading>
            )}

            {!isLoading && query && results.length === 0 && (
              <Command.Empty className="py-6 text-center text-ink-500">
                No results found for "{query}"
              </Command.Empty>
            )}

            {!query && (
              <div className="py-6 text-center text-ink-400 dark:text-parchment-500">
                Start typing to search...
              </div>
            )}

            {/* Campaign Results */}
            {results.filter((r) => r.category === 'campaign').length > 0 && (
              <Command.Group heading="Campaign">
                {results
                  .filter((r) => r.category === 'campaign')
                  .map((result) => {
                    const Icon = typeIcons[result.type] || BookOpen;
                    return (
                      <Command.Item
                        key={`${result.type}-${result.slug}`}
                        value={result.path}
                        onSelect={handleSelect}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer aria-selected:bg-parchment-100 dark:aria-selected:bg-ink-700"
                      >
                        <Icon className="h-4 w-4 text-ink-400" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{result.name}</p>
                          <p className="text-xs text-ink-500 dark:text-parchment-400 capitalize">
                            {result.type}
                          </p>
                        </div>
                      </Command.Item>
                    );
                  })}
              </Command.Group>
            )}

            {/* Reference Results */}
            {results.filter((r) => r.category === 'reference').length > 0 && (
              <Command.Group heading="Reference">
                {results
                  .filter((r) => r.category === 'reference')
                  .map((result) => {
                    const Icon = typeIcons[result.type] || BookOpen;
                    return (
                      <Command.Item
                        key={`${result.type}-${result.slug}`}
                        value={result.path}
                        onSelect={handleSelect}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer aria-selected:bg-parchment-100 dark:aria-selected:bg-ink-700"
                      >
                        <Icon className="h-4 w-4 text-ink-400" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{result.name}</p>
                          <p className="text-xs text-ink-500 dark:text-parchment-400 capitalize">
                            {result.type}
                          </p>
                        </div>
                      </Command.Item>
                    );
                  })}
              </Command.Group>
            )}
          </Command.List>

          {/* Footer */}
          <div className="flex items-center gap-4 px-4 py-2 border-t border-parchment-200 dark:border-ink-700 text-xs text-ink-400">
            <span>
              <kbd className="px-1.5 py-0.5 bg-parchment-100 dark:bg-ink-700 rounded">↑↓</kbd> to navigate
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 bg-parchment-100 dark:bg-ink-700 rounded">↵</kbd> to select
            </span>
            <span>
              <kbd className="px-1.5 py-0.5 bg-parchment-100 dark:bg-ink-700 rounded">esc</kbd> to close
            </span>
          </div>
        </Command>
      </div>
    </div>
  );
}

import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { BookOpen, ChevronRight } from 'lucide-react';
import { getDocs } from '@services/api';

export default function Docs() {
  const { data: docs, isLoading, error } = useQuery({
    queryKey: ['docs'],
    queryFn: getDocs,
  });

  return (
    <div className="space-y-6">
      <header className="flex items-center gap-3">
        <BookOpen className="h-8 w-8 text-parchment-600 dark:text-parchment-500" />
        <h1>Documentation</h1>
      </header>
      <p className="text-ink-600 dark:text-parchment-400">
        User guide and reference for 5e-cursor. Read in order or jump to any section.
      </p>

      {isLoading && <p>Loading...</p>}
      {error && <p className="text-red-600">Error loading documentation</p>}

      {docs && docs.length > 0 && (
        <div className="space-y-2">
          {docs.map((doc) => (
            <Link
              key={doc.slug}
              to={`/docs/${doc.slug}`}
              className="card card-link flex items-center gap-4 hover:border-parchment-400 dark:hover:border-ink-500 no-underline text-inherit"
            >
              <span className="flex-1 font-medium">{doc.title}</span>
              <ChevronRight className="h-5 w-5 text-ink-400 dark:text-parchment-500 flex-shrink-0" />
            </Link>
          ))}
        </div>
      )}

      {docs?.length === 0 && (
        <p className="text-center text-ink-500 dark:text-parchment-400 py-8">
          No documentation found.
        </p>
      )}
    </div>
  );
}

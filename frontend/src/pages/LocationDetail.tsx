import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getLocation } from '@services/api';
import MarkdownViewer from '@components/markdown/MarkdownViewer';
import { Breadcrumbs } from '@components/ui';

export default function LocationDetail() {
  const { slug } = useParams<{ slug: string }>();

  const { data: location, isLoading, error } = useQuery({
    queryKey: ['location', slug],
    queryFn: () => getLocation(slug!),
    enabled: !!slug,
  });

  if (isLoading) return <p>Loading location...</p>;
  if (error || !location) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Location not found</p>
        <Link to="/locations" className="btn btn-secondary">Back to Locations</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Locations', path: '/locations' },
          { label: location.name },
        ]}
      />

      <header className="flex items-start justify-between">
        <h1>{location.name}</h1>
        <span className="badge badge-neutral">{location.type}</span>
      </header>

      <div className="flex flex-wrap gap-4 text-sm text-ink-600 dark:text-parchment-400">
        {location.region && <span>Region: {location.region}</span>}
        {location.discovered && <span>Discovered: {location.discovered}</span>}
      </div>

      <div className="card prose max-w-none">
        <MarkdownViewer content={location.content} basePath="/locations" />
      </div>
    </div>
  );
}

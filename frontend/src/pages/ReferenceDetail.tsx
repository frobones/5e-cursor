import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getReferenceDetail } from '@services/api';
import MarkdownViewer from '@components/markdown/MarkdownViewer';
import { Breadcrumbs } from '@components/ui';

export default function ReferenceDetail() {
  const { type, '*': slug } = useParams<{ type: string; '*': string }>();

  const { data: reference, isLoading, error } = useQuery({
    queryKey: ['reference', type, slug],
    queryFn: () => getReferenceDetail(type!, slug!),
    enabled: !!type && !!slug,
  });

  if (isLoading) return <p>Loading...</p>;
  if (error || !reference) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Reference not found</p>
        <Link to="/reference" className="btn btn-secondary">Back to Reference</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Reference', path: '/reference' },
          { label: type ? type.charAt(0).toUpperCase() + type.slice(1) : '', path: `/reference/${type}` },
          { label: reference.name },
        ]}
      />

      <header>
        <h1>{reference.name}</h1>
        {reference.source && (
          <p className="text-ink-600 dark:text-parchment-400">
            Source: {reference.source}
          </p>
        )}
      </header>

      <div className="card prose max-w-none">
        <MarkdownViewer content={reference.content} basePath={`/reference/${type}`} />
      </div>
    </div>
  );
}

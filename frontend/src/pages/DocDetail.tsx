import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getDoc } from '@services/api';
import MarkdownViewer from '@components/markdown/MarkdownViewer';
import { Breadcrumbs } from '@components/ui';

export default function DocDetail() {
  const { slug } = useParams<{ slug: string }>();

  const { data: doc, isLoading, error } = useQuery({
    queryKey: ['doc', slug],
    queryFn: () => getDoc(slug!),
    enabled: !!slug,
  });

  if (isLoading) return <p>Loading...</p>;
  if (error || !doc) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Documentation not found</p>
        <Link to="/docs" className="btn btn-secondary">
          Back to Documentation
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Documentation', path: '/docs' },
          { label: doc.title },
        ]}
      />

      <header>
        <h1>{doc.title}</h1>
      </header>

      <div className="card prose max-w-none">
        <MarkdownViewer content={doc.content} basePath="/docs" />
      </div>
    </div>
  );
}

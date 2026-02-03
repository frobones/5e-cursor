import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getCharacter } from '@services/api';
import MarkdownViewer from '@components/markdown/MarkdownViewer';
import { Breadcrumbs } from '@components/ui';

export default function CharacterDetail() {
  const { slug } = useParams<{ slug: string }>();

  const { data: character, isLoading, error } = useQuery({
    queryKey: ['character', slug],
    queryFn: () => getCharacter(slug!),
    enabled: !!slug,
  });

  if (isLoading) return <p>Loading character...</p>;
  if (error || !character) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Character not found</p>
        <Link to="/party" className="btn btn-secondary">Back to Party</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Party', path: '/party' },
          { label: character.name },
        ]}
      />

      <header>
        <h1>{character.name}</h1>
        {character.player && (
          <p className="text-ink-600 dark:text-parchment-400">
            Player: {character.player}
          </p>
        )}
      </header>

      <div className="flex flex-wrap gap-2">
        {character.species && <span className="badge badge-neutral">{character.species}</span>}
        {character.class_info && <span className="badge badge-neutral">{character.class_info}</span>}
        {character.level && <span className="badge badge-ally">Level {character.level}</span>}
      </div>

      <div className="card prose max-w-none">
        <MarkdownViewer content={character.content} basePath="/party" />
      </div>
    </div>
  );
}

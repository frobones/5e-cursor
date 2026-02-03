import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getSession } from '@services/api';
import MarkdownViewer from '@components/markdown/MarkdownViewer';
import { Breadcrumbs } from '@components/ui';

export default function SessionDetail() {
  const { number } = useParams<{ number: string }>();
  const sessionNum = Number(number);

  const { data: session, isLoading, error } = useQuery({
    queryKey: ['session', sessionNum],
    queryFn: () => getSession(sessionNum),
    enabled: !isNaN(sessionNum),
  });

  if (isLoading) return <p>Loading session...</p>;
  if (error || !session) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Session not found</p>
        <Link to="/sessions" className="btn btn-secondary">Back to Sessions</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Sessions', path: '/sessions' },
          { label: `Session ${session.number}` },
        ]}
      />

      <header>
        <p className="text-parchment-600 dark:text-parchment-400 font-display">
          Session {session.number}
        </p>
        <h1>{session.title}</h1>
      </header>

      <div className="flex flex-wrap gap-4 text-sm text-ink-600 dark:text-parchment-400">
        <span>Date: {session.date}</span>
        {session.in_game_date && <span>In-Game: {session.in_game_date}</span>}
      </div>

      {session.summary && (
        <div className="card">
          <h2 className="font-display font-semibold mb-2">Summary</h2>
          <p className="text-ink-700 dark:text-parchment-300">{session.summary}</p>
        </div>
      )}

      <div className="card prose max-w-none">
        <MarkdownViewer content={session.content} basePath="/sessions" />
      </div>
    </div>
  );
}

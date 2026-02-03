import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Heart, Circle, Swords } from 'lucide-react';
import { getNPC } from '@services/api';
import MarkdownViewer from '@components/markdown/MarkdownViewer';
import { Breadcrumbs } from '@components/ui';
import type { Role } from '@/types';
import clsx from 'clsx';

const roleIcons: Record<Role, React.ComponentType<{ className?: string }>> = {
  ally: Heart,
  neutral: Circle,
  enemy: Swords,
  unknown: Circle,
};

const roleBadgeClass: Record<Role, string> = {
  ally: 'badge-ally',
  neutral: 'badge-neutral',
  enemy: 'badge-enemy',
  unknown: 'badge-neutral',
};

export default function NPCDetail() {
  const { slug } = useParams<{ slug: string }>();

  const { data: npc, isLoading, error } = useQuery({
    queryKey: ['npc', slug],
    queryFn: () => getNPC(slug!),
    enabled: !!slug,
  });

  if (isLoading) {
    return <p>Loading NPC...</p>;
  }

  if (error || !npc) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">NPC not found</p>
        <Link to="/npcs" className="btn btn-secondary">
          Back to NPCs
        </Link>
      </div>
    );
  }

  const Icon = roleIcons[npc.role] || Circle;

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <Breadcrumbs
        items={[
          { label: 'NPCs', path: '/npcs' },
          { label: npc.name },
        ]}
      />

      {/* Header */}
      <header className="flex items-start justify-between">
        <div>
          <h1>{npc.name}</h1>
          {npc.occupation && (
            <p className="text-lg text-ink-600 dark:text-parchment-400 mt-1">
              {npc.occupation}
            </p>
          )}
        </div>
        <span className={clsx('badge', roleBadgeClass[npc.role])}>
          <Icon className="h-3 w-3 mr-1" />
          {npc.role}
        </span>
      </header>

      {/* Meta info */}
      <div className="flex flex-wrap gap-4 text-sm text-ink-600 dark:text-parchment-400">
        {npc.location && (
          <span>📍 {npc.location}</span>
        )}
        {npc.first_seen && (
          <span>First seen: {npc.first_seen}</span>
        )}
      </div>

      {/* Connections */}
      {npc.connections.length > 0 && (
        <section className="card">
          <h2 className="font-display font-semibold text-lg mb-3">Connections</h2>
          <ul className="space-y-2">
            {npc.connections.map((conn, idx) => (
              <li key={idx} className="flex items-center gap-2">
                {conn.target_slug ? (
                  <Link
                    to={`/npcs/${conn.target_slug}`}
                    className="font-medium hover:underline"
                  >
                    {conn.target_name}
                  </Link>
                ) : (
                  <span className="font-medium">{conn.target_name}</span>
                )}
                <span className="badge badge-neutral">{conn.type}</span>
                {conn.description && (
                  <span className="text-ink-500 dark:text-parchment-400">
                    — {conn.description}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Content */}
      <div className="card prose max-w-none">
        <MarkdownViewer content={npc.content} basePath="/npcs" />
      </div>
    </div>
  );
}

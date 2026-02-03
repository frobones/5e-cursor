import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Edit, Swords, Play } from 'lucide-react';
import { getEncounter, getActiveCombats } from '@services/api';
import MarkdownViewer from '@components/markdown/MarkdownViewer';
import { Breadcrumbs } from '@components/ui';

export default function EncounterDetail() {
  const { slug } = useParams<{ slug: string }>();

  const { data: encounter, isLoading, error } = useQuery({
    queryKey: ['encounter', slug],
    queryFn: () => getEncounter(slug!),
    enabled: !!slug,
  });

  // Check for active combat
  const { data: activeCombats } = useQuery({
    queryKey: ['activeCombats'],
    queryFn: getActiveCombats,
    staleTime: 0, // Always refetch on mount to ensure fresh combat status
  });

  const hasActiveCombat = activeCombats?.includes(slug ?? '') ?? false;

  if (isLoading) return <p>Loading encounter...</p>;
  if (error || !encounter) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Encounter not found</p>
        <Link to="/encounters" className="btn btn-secondary">Back to Encounters</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Encounters', path: '/encounters' },
          { label: encounter.name },
        ]}
      />

      <header className="flex items-start justify-between">
        <div>
          <h1>{encounter.name}</h1>
          <span className="badge badge-neutral">{encounter.difficulty}</span>
        </div>
        <div className="flex gap-2">
          <Link
            to={`/encounters/${slug}/edit`}
            className="btn btn-secondary flex items-center gap-2"
          >
            <Edit className="h-4 w-4" />
            Edit
          </Link>
          <Link
            to={`/encounters/${slug}/combat`}
            className={`btn flex items-center gap-2 ${hasActiveCombat ? 'bg-orange-500 hover:bg-orange-600 text-white' : 'btn-primary'}`}
          >
            {hasActiveCombat ? (
              <>
                <Play className="h-4 w-4" />
                Resume Combat
              </>
            ) : (
              <>
                <Swords className="h-4 w-4" />
                Start Combat
              </>
            )}
          </Link>
        </div>
      </header>

      <div className="flex flex-wrap gap-4 text-sm text-ink-600 dark:text-parchment-400">
        <span>Party Level: {encounter.party_level}</span>
        <span>Party Size: {encounter.party_size}</span>
        <span>Total XP: {encounter.total_xp.toLocaleString()}</span>
      </div>

      {encounter.creatures.length > 0 && (
        <div className="card">
          <h2 className="font-display font-semibold mb-3">Creatures</h2>
          <table className="w-full">
            <thead>
              <tr className="border-b border-parchment-200 dark:border-ink-600">
                <th className="text-left py-2">Creature</th>
                <th className="text-left py-2">CR</th>
                <th className="text-right py-2">Count</th>
                <th className="text-right py-2">XP</th>
              </tr>
            </thead>
            <tbody>
              {encounter.creatures.map((c, i) => (
                <tr key={i} className="border-b border-parchment-100 dark:border-ink-700">
                  <td className="py-2">{c.name}</td>
                  <td className="py-2">{c.cr}</td>
                  <td className="py-2 text-right">{c.count}</td>
                  <td className="py-2 text-right">{(c.xp * c.count).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card prose max-w-none">
        <MarkdownViewer content={encounter.content} basePath="/encounters" />
      </div>
    </div>
  );
}

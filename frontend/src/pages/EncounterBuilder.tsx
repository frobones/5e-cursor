import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Save, ArrowLeft } from 'lucide-react';

import { Breadcrumbs } from '@components/ui';
import { CreatureSelector, EncounterPanel, DifficultyDisplay } from '@components/encounter';
import { getParty, getEncounter, createEncounter, updateEncounter } from '@services/api';

import type { EncounterBuilderCreature, EncounterBuilderState } from '@/types';

export default function EncounterBuilder() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = !!slug;

  // State
  const [name, setName] = useState('');
  const [partyLevel, setPartyLevel] = useState(1);
  const [partySize, setPartySize] = useState(4);
  const [creatures, setCreatures] = useState<EncounterBuilderCreature[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch party info for auto-population
  const { data: party } = useQuery({
    queryKey: ['party'],
    queryFn: getParty,
  });

  // Fetch existing encounter if editing
  const { data: existingEncounter, isLoading: loadingEncounter } = useQuery({
    queryKey: ['encounter', slug],
    queryFn: () => getEncounter(slug!),
    enabled: isEditing,
  });

  // Auto-populate party settings
  useEffect(() => {
    if (party && !isEditing) {
      setPartySize(party.size || 4);
      if (party.average_level) {
        setPartyLevel(Math.round(party.average_level));
      }
    }
  }, [party, isEditing]);

  // Load existing encounter data
  useEffect(() => {
    if (existingEncounter) {
      setName(existingEncounter.name);
      setPartyLevel(existingEncounter.party_level);
      setPartySize(existingEncounter.party_size);
      setCreatures(
        existingEncounter.creatures.map((c) => ({
          name: c.name,
          slug: c.name.toLowerCase().replace(/\s+/g, '-'),
          cr: c.cr,
          xp: c.xp,
          count: c.count,
        }))
      );
    }
  }, [existingEncounter]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: createEncounter,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['encounters'] });
      navigate(`/encounters/${data.slug}`);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ slug, data }: { slug: string; data: Parameters<typeof updateEncounter>[1] }) =>
      updateEncounter(slug, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['encounters'] });
      queryClient.invalidateQueries({ queryKey: ['encounter', slug] });
      navigate(`/encounters/${data.slug}`);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const handleAddCreature = (creature: EncounterBuilderCreature) => {
    setCreatures((prev) => {
      const existing = prev.find((c) => c.slug === creature.slug);
      if (existing) {
        return prev.map((c) =>
          c.slug === creature.slug ? { ...c, count: c.count + 1 } : c
        );
      }
      return [...prev, creature];
    });
  };

  const handleUpdateCount = (slug: string, delta: number) => {
    setCreatures((prev) =>
      prev.map((c) =>
        c.slug === slug ? { ...c, count: Math.max(1, c.count + delta) } : c
      )
    );
  };

  const handleRemoveCreature = (slug: string) => {
    setCreatures((prev) => prev.filter((c) => c.slug !== slug));
  };

  const handleSave = () => {
    setError(null);

    if (!name.trim()) {
      setError('Please enter an encounter name');
      return;
    }

    if (creatures.length === 0) {
      setError('Please add at least one creature');
      return;
    }

    const data = {
      name: name.trim(),
      party_level: partyLevel,
      party_size: partySize,
      creatures: creatures.map((c) => ({
        name: c.name,
        slug: c.slug,
        cr: c.cr,
        xp: c.xp,
        count: c.count,
      })),
    };

    if (isEditing) {
      updateMutation.mutate({ slug: slug!, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const isSaving = createMutation.isPending || updateMutation.isPending;

  if (isEditing && loadingEncounter) {
    return <p>Loading encounter...</p>;
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Encounters', path: '/encounters' },
          { label: isEditing ? `Edit: ${existingEncounter?.name}` : 'Build New Encounter' },
        ]}
      />

      <header className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/encounters"
            className="p-2 rounded-lg hover:bg-ink-100 dark:hover:bg-ink-800 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1>{isEditing ? 'Edit Encounter' : 'Build New Encounter'}</h1>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving || creatures.length === 0}
          className="btn btn-primary flex items-center gap-2"
        >
          <Save className="h-4 w-4" />
          {isSaving ? 'Saving...' : 'Save Encounter'}
        </button>
      </header>

      {error && (
        <div className="p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Encounter Name & Party Settings */}
      <div className="card p-4 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Encounter Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Goblin Ambush"
            className="w-full px-4 py-2 border border-ink-200 dark:border-ink-700 rounded-lg bg-white dark:bg-ink-900 focus:outline-none focus:ring-2 focus:ring-parchment-500"
          />
        </div>

        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Party Level</label>
            <input
              type="number"
              min={1}
              max={20}
              value={partyLevel}
              onChange={(e) => setPartyLevel(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
              className="w-full px-4 py-2 border border-ink-200 dark:border-ink-700 rounded-lg bg-white dark:bg-ink-900 focus:outline-none focus:ring-2 focus:ring-parchment-500"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Party Size</label>
            <input
              type="number"
              min={1}
              max={10}
              value={partySize}
              onChange={(e) => setPartySize(Math.max(1, Math.min(10, parseInt(e.target.value) || 1)))}
              className="w-full px-4 py-2 border border-ink-200 dark:border-ink-700 rounded-lg bg-white dark:bg-ink-900 focus:outline-none focus:ring-2 focus:ring-parchment-500"
            />
          </div>
        </div>
      </div>

      {/* Main Builder Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Creature Selector */}
        <div className="lg:col-span-2 card p-4">
          <h2 className="text-lg font-semibold mb-4">Add Creatures</h2>
          <CreatureSelector onAddCreature={handleAddCreature} />
        </div>

        {/* Encounter Panel & Difficulty */}
        <div className="space-y-6">
          <div className="card p-4">
            <h2 className="text-lg font-semibold mb-4">Encounter</h2>
            <EncounterPanel
              creatures={creatures}
              onUpdateCount={handleUpdateCount}
              onRemoveCreature={handleRemoveCreature}
            />
          </div>

          <div className="card p-4">
            <h2 className="text-lg font-semibold mb-4">Difficulty</h2>
            <DifficultyDisplay
              creatures={creatures}
              partyLevel={partyLevel}
              partySize={partySize}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

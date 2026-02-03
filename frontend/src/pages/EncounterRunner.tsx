import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, ChevronLeft, ChevronRight, Flag, Users, Play, Save } from 'lucide-react';

import { Breadcrumbs } from '@components/ui';
import {
  InitiativeList,
  InitiativeSetup,
  CombatTracker,
  DamageHistory,
  CreatureStatsPanel,
  CharacterStatsPanel,
} from '@components/combat';
import {
  getEncounter,
  getCombat,
  startCombat,
  updateCombat,
  endCombat,
  getParty,
  getCreatureStats,
  getCharacterStats,
} from '@services/api';
import {
  applyDamage,
  applyHealing,
  addTempHp,
  toggleCondition,
  logDamageEvent,
  sortByInitiative,
  generateId,
} from '@/utils/combatState';

import type { CombatState, Combatant, DamageEvent, PartyOverview, CreatureStats, CharacterStats } from '@/types';

type CombatPhase = 'loading' | 'setup' | 'initiative' | 'running' | 'ended';

export default function EncounterRunner() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [phase, setPhase] = useState<CombatPhase>('loading');
  const [combat, setCombat] = useState<CombatState | null>(null);
  const [selectedCombatantId, setSelectedCombatantId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedPartyMembers, setSelectedPartyMembers] = useState<Set<string>>(new Set());

  // Fetch encounter details
  const { data: encounter } = useQuery({
    queryKey: ['encounter', slug],
    queryFn: () => getEncounter(slug!),
    enabled: !!slug,
  });

  // Fetch party data for setup phase
  const { data: party } = useQuery({
    queryKey: ['party'],
    queryFn: getParty,
  });

  // Try to load existing combat
  const { data: existingCombat, isLoading: loadingCombat, isError: combatError } = useQuery({
    queryKey: ['combat', slug],
    queryFn: () => getCombat(slug!),
    enabled: !!slug,
    retry: false,
  });

  // Start combat mutation
  const startCombatMutation = useMutation({
    mutationFn: (selectedMembers: string[]) => startCombat(slug!, true, selectedMembers),
    onSuccess: (data) => {
      setCombat(data);
      setPhase('initiative');
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  // Update combat mutation (with debounce for auto-save)
  const updateCombatMutation = useMutation({
    mutationFn: (data: CombatState) => updateCombat(slug!, data),
    onError: (err: Error) => {
      console.error('Failed to save combat state:', err);
    },
  });

  // End combat mutation
  const endCombatMutation = useMutation({
    mutationFn: () => endCombat(slug!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['combat', slug] });
      queryClient.invalidateQueries({ queryKey: ['activeCombats'] });
      navigate(`/encounters/${slug}`);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  // Initialize selected party members when party data loads
  useEffect(() => {
    if (party?.characters) {
      // Select all party members by default
      setSelectedPartyMembers(new Set(party.characters.map((c) => c.slug)));
    }
  }, [party]);

  // Initialize phase based on existing combat
  useEffect(() => {
    if (loadingCombat) return;

    // If there's an error (404 = no combat exists) or no active combat, go to setup
    if (combatError || !existingCombat || existingCombat.status !== 'active') {
      setPhase('setup');
      return;
    }

    // Resume existing combat
    setCombat(existingCombat);
    // Check if we're in initiative phase or running
    const hasInitiatives = existingCombat.combatants.every((c) => c.initiative > 0);
    setPhase(hasInitiatives ? 'running' : 'initiative');
  }, [existingCombat, loadingCombat, combatError]);

  // Auto-select the active combatant when combat loads or turn changes
  useEffect(() => {
    if (phase === 'running' && combat) {
      const activeCombatant = combat.combatants.find((c) => c.isActive);
      if (activeCombatant && selectedCombatantId !== activeCombatant.id) {
        setSelectedCombatantId(activeCombatant.id);
      }
    }
  }, [phase, combat?.turn, combat?.round]);

  // Toggle party member selection
  const togglePartyMember = (slug: string) => {
    setSelectedPartyMembers((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) {
        next.delete(slug);
      } else {
        next.add(slug);
      }
      return next;
    });
  };

  // Begin combat with selected party members
  const handleBeginCombat = () => {
    startCombatMutation.mutate(Array.from(selectedPartyMembers));
  };

  // Auto-save combat state when it changes
  const saveCombat = useCallback(
    (newCombat: CombatState) => {
      setCombat(newCombat);
      updateCombatMutation.mutate(newCombat);
    },
    [updateCombatMutation]
  );

  // Update initiative for a combatant
  const handleUpdateInitiative = (combatantId: string, initiative: number) => {
    if (!combat) return;

    const updatedCombatants = combat.combatants.map((c) =>
      c.id === combatantId ? { ...c, initiative } : c
    );

    const newCombat = { ...combat, combatants: updatedCombatants };
    saveCombat(newCombat);
  };

  // Batch update initiative for multiple combatants at once
  const handleBatchUpdateInitiative = (updates: Array<{ id: string; initiative: number }>) => {
    if (!combat) return;

    const updateMap = new Map(updates.map((u) => [u.id, u.initiative]));
    const updatedCombatants = combat.combatants.map((c) =>
      updateMap.has(c.id) ? { ...c, initiative: updateMap.get(c.id)! } : c
    );

    const newCombat = { ...combat, combatants: updatedCombatants };
    saveCombat(newCombat);
  };

  // Start combat after initiative setup
  const handleStartCombat = () => {
    if (!combat) return;

    // Sort combatants and set the first one as active
    const sorted = sortByInitiative(combat.combatants);
    const updatedCombatants = sorted.map((c, i) => ({ ...c, isActive: i === 0 }));

    const newCombat: CombatState = {
      ...combat,
      combatants: updatedCombatants,
      round: 1,
      turn: 0,
    };

    saveCombat(newCombat);
    setPhase('running');
  };

  // Apply damage to selected combatant
  const handleApplyDamage = (amount: number, source?: string) => {
    if (!combat || !selectedCombatantId) return;

    const combatant = combat.combatants.find((c) => c.id === selectedCombatantId);
    if (!combatant) return;

    const updatedCombatant = applyDamage(combatant, amount);
    const event = logDamageEvent(
      combat,
      combatant.id,
      combatant.name,
      amount,
      'damage',
      source
    );

    const newCombat: CombatState = {
      ...combat,
      combatants: combat.combatants.map((c) =>
        c.id === selectedCombatantId ? updatedCombatant : c
      ),
      damageLog: [...combat.damageLog, event],
    };

    saveCombat(newCombat);
  };

  // Apply healing to selected combatant
  const handleApplyHealing = (amount: number, source?: string) => {
    if (!combat || !selectedCombatantId) return;

    const combatant = combat.combatants.find((c) => c.id === selectedCombatantId);
    if (!combatant) return;

    const updatedCombatant = applyHealing(combatant, amount);
    const event = logDamageEvent(
      combat,
      combatant.id,
      combatant.name,
      amount,
      'healing',
      source
    );

    const newCombat: CombatState = {
      ...combat,
      combatants: combat.combatants.map((c) =>
        c.id === selectedCombatantId ? updatedCombatant : c
      ),
      damageLog: [...combat.damageLog, event],
    };

    saveCombat(newCombat);
  };

  // Add temp HP to selected combatant
  const handleAddTempHp = (amount: number) => {
    if (!combat || !selectedCombatantId) return;

    const combatant = combat.combatants.find((c) => c.id === selectedCombatantId);
    if (!combatant) return;

    const updatedCombatant = addTempHp(combatant, amount);
    const event = logDamageEvent(
      combat,
      combatant.id,
      combatant.name,
      amount,
      'temp_hp'
    );

    const newCombat: CombatState = {
      ...combat,
      combatants: combat.combatants.map((c) =>
        c.id === selectedCombatantId ? updatedCombatant : c
      ),
      damageLog: [...combat.damageLog, event],
    };

    saveCombat(newCombat);
  };

  // Toggle condition on a combatant
  const handleToggleCondition = (combatantId: string, condition: string) => {
    if (!combat) return;

    const combatant = combat.combatants.find((c) => c.id === combatantId);
    if (!combatant) return;

    const updatedCombatant = toggleCondition(combatant, condition);

    const newCombat: CombatState = {
      ...combat,
      combatants: combat.combatants.map((c) =>
        c.id === combatantId ? updatedCombatant : c
      ),
    };

    saveCombat(newCombat);
  };

  // Next turn
  const handleNextTurn = () => {
    if (!combat) return;

    const sorted = sortByInitiative(combat.combatants);
    let nextTurn = combat.turn + 1;
    let nextRound = combat.round;

    if (nextTurn >= sorted.length) {
      nextTurn = 0;
      nextRound += 1;
    }

    const updatedCombatants = sorted.map((c, i) => ({ ...c, isActive: i === nextTurn }));

    const newCombat: CombatState = {
      ...combat,
      combatants: updatedCombatants,
      turn: nextTurn,
      round: nextRound,
    };

    saveCombat(newCombat);
  };

  // Previous turn
  const handlePrevTurn = () => {
    if (!combat) return;

    const sorted = sortByInitiative(combat.combatants);
    let prevTurn = combat.turn - 1;
    let prevRound = combat.round;

    if (prevTurn < 0) {
      if (combat.round > 1) {
        prevTurn = sorted.length - 1;
        prevRound -= 1;
      } else {
        prevTurn = 0;
      }
    }

    const updatedCombatants = sorted.map((c, i) => ({ ...c, isActive: i === prevTurn }));

    const newCombat: CombatState = {
      ...combat,
      combatants: updatedCombatants,
      turn: prevTurn,
      round: prevRound,
    };

    saveCombat(newCombat);
  };

  // End combat
  const handleEndCombat = () => {
    if (confirm('Are you sure you want to end combat? This will archive the combat log.')) {
      endCombatMutation.mutate();
    }
  };

  // Save and exit (preserves combat state for later resumption)
  const handleSaveAndExit = () => {
    // Invalidate active combats so the list shows correct status
    queryClient.invalidateQueries({ queryKey: ['activeCombats'] });
    navigate('/encounters');
  };

  // Get selected combatant
  const selectedCombatant = combat?.combatants.find((c) => c.id === selectedCombatantId) || null;

  // Fetch creature stats when a monster is selected
  const { data: creatureStats, isLoading: loadingCreatureStats } = useQuery({
    queryKey: ['creatureStats', selectedCombatant?.creatureSlug],
    queryFn: () => getCreatureStats(selectedCombatant!.creatureSlug!),
    enabled: !!selectedCombatant && selectedCombatant.type === 'monster' && !!selectedCombatant.creatureSlug,
    staleTime: 1000 * 60 * 10, // Cache for 10 minutes
  });

  // Get character slug from combatant (set by backend for players)
  const characterSlug = selectedCombatant?.type === 'player' ? selectedCombatant.characterSlug : null;

  // Fetch character stats when a player is selected
  const { data: characterStats, isLoading: loadingCharacterStats } = useQuery<CharacterStats>({
    queryKey: ['characterStats', characterSlug],
    queryFn: () => getCharacterStats(characterSlug!),
    enabled: !!selectedCombatant && selectedCombatant.type === 'player' && !!characterSlug,
    staleTime: 1000 * 60 * 10, // Cache for 10 minutes
  });

  if (phase === 'loading' || !encounter) {
    return <p>Loading combat...</p>;
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Encounters', path: '/encounters' },
          { label: encounter.name, path: `/encounters/${slug}` },
          { label: 'Combat' },
        ]}
      />

      {error && (
        <div className="p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Party Selection Setup Phase */}
      {phase === 'setup' && (
        <div className="max-w-2xl mx-auto">
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-6">
              <Users className="h-6 w-6 text-parchment-600" />
              <h2 className="text-xl font-semibold">Select Party Members</h2>
            </div>

            <p className="text-ink-600 dark:text-parchment-400 mb-4">
              Choose which party members are present for this encounter:
            </p>

            {party?.characters && party.characters.length > 0 ? (
              <div className="space-y-2 mb-6">
                {party.characters.map((char) => (
                  <label
                    key={char.slug}
                    className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedPartyMembers.has(char.slug)
                        ? 'bg-ally-light dark:bg-green-900/30 border-ally dark:border-green-700'
                        : 'bg-ink-50 dark:bg-ink-800 border-ink-200 dark:border-ink-700 hover:border-ink-300 dark:hover:border-ink-600'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedPartyMembers.has(char.slug)}
                      onChange={() => togglePartyMember(char.slug)}
                      className="h-5 w-5 rounded border-ink-300 text-ally focus:ring-ally"
                    />
                    <div className="flex-1">
                      <div className="font-medium">{char.name}</div>
                      <div className="text-sm text-ink-500 dark:text-parchment-500">
                        {char.species && <span>{char.species} </span>}
                        {char.class_info && <span>{char.class_info}</span>}
                        {char.player && <span className="ml-2">({char.player})</span>}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            ) : (
              <p className="text-ink-500 dark:text-parchment-500 italic mb-6">
                No party members found. Combat will include only monsters.
              </p>
            )}

            <div className="flex items-center justify-between">
              <Link
                to={`/encounters/${slug}`}
                className="btn btn-secondary flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Cancel
              </Link>

              <button
                onClick={handleBeginCombat}
                disabled={startCombatMutation.isPending}
                className="btn btn-primary flex items-center gap-2"
              >
                <Play className="h-4 w-4" />
                {startCombatMutation.isPending ? 'Starting...' : 'Start Combat'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Initiative Setup Phase */}
      {phase === 'initiative' && combat && (
        <div className="max-w-2xl mx-auto">
          <div className="card p-6">
            <InitiativeSetup
              combatants={combat.combatants}
              onUpdateInitiative={handleUpdateInitiative}
              onBatchUpdateInitiative={handleBatchUpdateInitiative}
              onStartCombat={handleStartCombat}
            />
          </div>
        </div>
      )}

      {/* Combat Running Phase */}
      {phase === 'running' && combat && (
        <>
          {/* Header with round/turn controls */}
          <header className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                to={`/encounters/${slug}`}
                className="p-2 rounded-lg hover:bg-ink-100 dark:hover:bg-ink-800 transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1>{encounter.name}</h1>
                <p className="text-ink-500">
                  Round {combat.round} &bull; Turn {combat.turn + 1} of{' '}
                  {combat.combatants.length}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handlePrevTurn}
                disabled={combat.round === 1 && combat.turn === 0}
                className="btn btn-secondary flex items-center gap-1"
              >
                <ChevronLeft className="h-4 w-4" />
                Prev
              </button>
              <button
                onClick={handleNextTurn}
                className="btn btn-primary flex items-center gap-1"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </button>
              <button
                onClick={handleSaveAndExit}
                className="btn btn-secondary flex items-center gap-1"
              >
                <Save className="h-4 w-4" />
                Save &amp; Exit
              </button>
              <button
                onClick={handleEndCombat}
                className="btn bg-red-500 hover:bg-red-600 text-white flex items-center gap-1"
              >
                <Flag className="h-4 w-4" />
                End Combat
              </button>
            </div>
          </header>

          {/* Main combat grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Initiative list and creature stats */}
            <div className="lg:col-span-2 space-y-6">
              <div className="card p-4">
                <h2 className="text-lg font-semibold mb-4">Initiative Order</h2>
                <InitiativeList
                  combatants={combat.combatants}
                  selectedId={selectedCombatantId ?? undefined}
                  onSelectCombatant={setSelectedCombatantId}
                  onToggleCondition={handleToggleCondition}
                />
              </div>

              {/* Creature Stats (for monsters) - below initiative for more space */}
              {selectedCombatant?.type === 'monster' && (
                <div className="card p-4">
                  <h2 className="text-lg font-semibold mb-4">
                    Creature Stats: {selectedCombatant.name}
                  </h2>
                  {loadingCreatureStats && <p className="text-ink-500">Loading stats...</p>}
                  {creatureStats && <CreatureStatsPanel stats={creatureStats} />}
                  {!loadingCreatureStats && !creatureStats && selectedCombatant.creatureSlug && (
                    <p className="text-ink-500 italic">Stats not available</p>
                  )}
                </div>
              )}

              {/* Character Stats (for players) */}
              {selectedCombatant?.type === 'player' && (
                <div className="card p-4">
                  <h2 className="text-lg font-semibold mb-4">
                    Character Stats: {selectedCombatant.name}
                  </h2>
                  {loadingCharacterStats && <p className="text-ink-500">Loading stats...</p>}
                  {characterStats && <CharacterStatsPanel stats={characterStats} />}
                  {!loadingCharacterStats && !characterStats && characterSlug && (
                    <p className="text-ink-500 italic">
                      Stats not available. Create a JSON file at campaign/party/characters/{characterSlug}.json
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Combat tracker */}
              <div className="card p-4">
                <h2 className="text-lg font-semibold mb-4">Actions</h2>
                <CombatTracker
                  selectedCombatant={selectedCombatant}
                  onApplyDamage={handleApplyDamage}
                  onApplyHealing={handleApplyHealing}
                  onAddTempHp={handleAddTempHp}
                  onToggleCondition={(condition) =>
                    selectedCombatantId && handleToggleCondition(selectedCombatantId, condition)
                  }
                />
              </div>

              {/* Damage history */}
              <div className="card p-4">
                <h2 className="text-lg font-semibold mb-4">Damage History</h2>
                <DamageHistory events={combat.damageLog} currentRound={combat.round} />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

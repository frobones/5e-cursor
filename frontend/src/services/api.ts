/**
 * API client for the campaign web UI backend.
 */

import type {
  CampaignOverview,
  CampaignStats,
  DocDetail,
  DocListItem,
  NPCListItem,
  NPCDetail,
  LocationListItem,
  LocationDetail,
  SessionListItem,
  SessionDetail,
  CharacterListItem,
  CharacterDetail,
  PartyOverview,
  EncounterListItem,
  EncounterDetail,
  ReferenceIndex,
  ReferenceListItem,
  ReferenceDetail,
  SearchResponse,
  TimelineResponse,
  RelationshipGraphResponse,
} from '@/types';

const API_BASE = '/api';

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}

async function postJson<T>(url: string, data: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

async function putJson<T>(url: string, data: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Campaign
export const getCampaign = () => fetchJson<CampaignOverview>('/campaign');
export const getCampaignStats = () => fetchJson<CampaignStats>('/campaign/stats');

// NPCs
export const getNPCs = (role?: string) => {
  const params = role ? `?role=${role}` : '';
  return fetchJson<NPCListItem[]>(`/npcs${params}`);
};
export const getNPC = (slug: string) => fetchJson<NPCDetail>(`/npcs/${slug}`);

// Locations
export const getLocations = (type?: string) => {
  const params = type ? `?type=${type}` : '';
  return fetchJson<LocationListItem[]>(`/locations${params}`);
};
export const getLocation = (slug: string) => fetchJson<LocationDetail>(`/locations/${slug}`);

// Sessions
export const getSessions = () => fetchJson<SessionListItem[]>('/sessions');
export const getSession = (number: number) => fetchJson<SessionDetail>(`/sessions/${number}`);

// Party
export const getParty = () => fetchJson<PartyOverview>('/party');
export const getCharacters = () => fetchJson<CharacterListItem[]>('/party/characters');
export const getCharacter = (slug: string) => fetchJson<CharacterDetail>(`/party/characters/${slug}`);

// Encounters
export const getEncounters = () => fetchJson<EncounterListItem[]>('/encounters');
export const getEncounter = (slug: string) => fetchJson<EncounterDetail>(`/encounters/${slug}`);

export interface EncounterCreateData {
  name: string;
  party_level: number;
  party_size: number;
  creatures: Array<{
    name: string;
    slug: string;
    cr: string;
    xp: number;
    count: number;
  }>;
}

export const createEncounter = (data: EncounterCreateData) =>
  postJson<EncounterDetail>('/encounters', data);

export const updateEncounter = (slug: string, data: Partial<EncounterCreateData>) =>
  putJson<EncounterDetail>(`/encounters/${slug}`, data);

// Reference
export const getReferenceIndex = () => fetchJson<ReferenceIndex>('/reference');
export const searchReference = (query: string, type?: string, limit = 50) => {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  if (type) params.set('type', type);
  return fetchJson<ReferenceListItem[]>(`/reference/search?${params}`);
};
export interface PaginatedReferenceResponse {
  items: ReferenceListItem[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

export const getReferenceByType = (
  type: string,
  options?: { level?: number; cr?: string; rarity?: string; offset?: number; limit?: number }
) => {
  const params = new URLSearchParams();
  if (options?.level !== undefined) params.set('level', String(options.level));
  if (options?.cr) params.set('cr', options.cr);
  if (options?.rarity) params.set('rarity', options.rarity);
  if (options?.offset !== undefined) params.set('offset', String(options.offset));
  if (options?.limit) params.set('limit', String(options.limit));
  const queryStr = params.toString();
  return fetchJson<PaginatedReferenceResponse>(`/reference/${type}${queryStr ? `?${queryStr}` : ''}`);
};
export const getReferenceDetail = (type: string, slug: string) =>
  fetchJson<ReferenceDetail>(`/reference/${type}/${slug}`);

// Convenience function to get all items of a reference type (no pagination)
export const getReference = async (type: string): Promise<ReferenceListItem[]> => {
  const result = await getReferenceByType(type, { limit: 2000 });
  return result.items;
};

// Search
export const search = (query: string, limit = 50) => {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return fetchJson<SearchResponse>(`/search?${params}`);
};

// Visualizations
export const getTimeline = () => fetchJson<TimelineResponse>('/timeline');
export const getRelationships = () => fetchJson<RelationshipGraphResponse>('/relationships');

// Docs
export const getDocs = () => fetchJson<DocListItem[]>('/docs');
export const getDoc = (slug: string) => fetchJson<DocDetail>(`/docs/${slug}`);

// Combat
import type { CombatState } from '@/types';

export const getCombat = (slug: string) => fetchJson<CombatState>(`/combat/${slug}`);

export const startCombat = (
  slug: string,
  includeParty: boolean = true,
  selectedPartyMembers?: string[]
) =>
  postJson<CombatState>(`/combat/${slug}`, {
    includeParty,
    selectedPartyMembers: selectedPartyMembers ?? null,
  });

export const updateCombat = (slug: string, combat: CombatState) =>
  putJson<CombatState>(`/combat/${slug}`, combat);

export const endCombat = async (slug: string): Promise<void> => {
  const response = await fetch(`${API_BASE}/combat/${slug}`, { method: 'DELETE' });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
};

export const getActiveCombats = () => fetchJson<string[]>('/combat');

// Creature Stats (from 5etools JSON)
import type { CreatureStats, CharacterStats } from '@/types';

export const getCreatureStats = (slug: string) =>
  fetchJson<CreatureStats>(`/creatures/${slug}/stats`);

// Character Stats (from JSON files for PCs)
export const getCharacterStats = (slug: string) =>
  fetchJson<CharacterStats>(`/party/characters/${slug}/stats`);

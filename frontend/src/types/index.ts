// Campaign types
export interface CampaignStats {
  npcs: number;
  locations: number;
  sessions: number;
  encounters: number;
  party_size: number;
}

export interface CampaignOverview {
  name: string;
  setting?: string;
  current_session: number;
  created?: string;
  stats: CampaignStats;
}

// Entity types
export type Role = 'ally' | 'neutral' | 'enemy' | 'unknown';

export interface Connection {
  target_name: string;
  target_slug?: string;
  type: string;
  description?: string;
}

export interface NPCListItem {
  name: string;
  slug: string;
  role: Role;
  occupation?: string;
  location?: string;
  first_seen?: string;
}

export interface NPCDetail extends NPCListItem {
  content: string;
  connections: Connection[];
}

export interface LocationListItem {
  name: string;
  slug: string;
  type: string;
  region?: string;
  discovered?: string;
}

export interface LocationDetail extends LocationListItem {
  content: string;
  key_npcs: string[];
}

export interface SessionListItem {
  number: number;
  title: string;
  date: string;
  in_game_date?: string;
}

export interface SessionDetail extends SessionListItem {
  content: string;
  summary?: string;
  npcs_encountered: string[];
  locations_visited: string[];
}

export interface CharacterListItem {
  name: string;
  slug: string;
  player?: string;
  species?: string;
  class_info?: string;
  level?: number;
}

export interface CharacterDetail extends CharacterListItem {
  content: string;
}

export interface PartyOverview {
  size: number;
  average_level?: number;
  characters: CharacterListItem[];
}

export interface EncounterCreature {
  name: string;
  cr: string;
  count: number;
  xp: number;
}

export interface EncounterListItem {
  name: string;
  slug: string;
  difficulty: string;
  total_creatures: number;
  party_level: number;
  party_size: number;
  base_xp: number; // Base XP for recalculating difficulty
  created?: string; // ISO date string
}

export interface EncounterDetail extends EncounterListItem {
  content: string;
  party_size: number;
  creatures: EncounterCreature[];
  total_xp: number;
}

// Reference types
export interface ReferenceIndex {
  total_entries: number;
  by_type: Record<string, number>;
}

export interface ReferenceListItem {
  name: string;
  slug: string;
  type: string;
  source?: string;
  metadata: Record<string, unknown>;
}

export interface ReferenceDetail extends ReferenceListItem {
  content: string;
}

// Search types
export interface SearchResult {
  name: string;
  slug: string;
  type: string;
  category: 'campaign' | 'reference';
  excerpt?: string;
  path: string;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
  by_type: Record<string, SearchResult[]>;
}

// Timeline types
export interface TimelineEvent {
  in_game_date: string;
  day: number;
  title: string;
  category: string;
  description?: string;
  session_number?: number;
  entity_path?: string;
  entity_type?: string;
}

export interface TimelineDay {
  day: number;
  in_game_date: string;
  events: TimelineEvent[];
}

export interface TimelineResponse {
  current_day: number;
  total_events: number;
  days: TimelineDay[];
}

// Relationship types
export interface RelationshipNode {
  id: string;
  name: string;
  role?: string;
}

export interface RelationshipEdge {
  source: string;
  target: string;
  type: string;
  description?: string;
}

export interface RelationshipGraphResponse {
  nodes: RelationshipNode[];
  edges: RelationshipEdge[];
  mermaid: string;
}

// Docs types
export interface DocListItem {
  slug: string;
  title: string;
}

export interface DocDetail {
  slug: string;
  title: string;
  content: string;
}

// Combat types
export interface Combatant {
  id: string;
  name: string;
  type: 'monster' | 'player';
  creatureSlug?: string;
  characterSlug?: string;
  initiative: number;
  maxHp: number;
  currentHp: number;
  tempHp: number;
  damageTaken: number; // For players: tracks total damage taken (since DM doesn't know PC HP)
  conditions: string[];
  isActive: boolean;
  ac: number; // Armor Class for quick reference
  dexModifier: number; // For rolling initiative
}

export interface DamageEvent {
  id: string;
  round: number;
  turn: number;
  targetId: string;
  targetName: string;
  amount: number;
  type: 'damage' | 'healing' | 'temp_hp';
  source?: string;
  timestamp: string;
}

export interface CombatState {
  encounterId: string;
  encounterName: string;
  round: number;
  turn: number;
  status: 'active' | 'paused' | 'completed';
  startedAt: string;
  combatants: Combatant[];
  damageLog: DamageEvent[];
}

// Encounter builder types
export interface EncounterBuilderCreature {
  name: string;
  slug: string;
  cr: string;
  xp: number;
  count: number;
  maxHP?: number;
}

export interface EncounterBuilderState {
  name: string;
  partyLevel: number;
  partySize: number;
  creatures: EncounterBuilderCreature[];
}

// Creature stats (from 5etools JSON)
export interface CreatureHP {
  average: number;
  formula: string;
}

export interface CreatureStats {
  name: string;
  size: string;
  creatureType: string;
  alignment?: string;
  ac: number;
  acSource?: string;
  hp: CreatureHP;
  speed: Record<string, number>;
  abilities: {
    str: number;
    dex: number;
    con: number;
    int: number;
    wis: number;
    cha: number;
  };
  saves?: Record<string, string>;
  skills?: Record<string, string>;
  damageResistances?: string[];
  damageImmunities?: string[];
  damageVulnerabilities?: string[];
  conditionImmunities?: string[];
  senses?: string[];
  passivePerception: number;
  languages?: string[];
  cr: string;
  traits?: Array<{ name: string; description: string }>;
  actions?: Array<{ name: string; description: string }>;
  bonusActions?: Array<{ name: string; description: string }>;
  reactions?: Array<{ name: string; description: string }>;
  legendaryActions?: Array<{ name: string; description: string }>;
}

// Character stats (from JSON files for PCs)
// Note: Uses snake_case to match API response
export interface CharacterHP {
  current: number;
  max: number;
}

export interface CharacterStats {
  name: string;
  player: string;
  species: string;
  character_class: string;
  background?: string;
  alignment?: string;
  size: string;
  creature_type: string;
  ac: number;
  ac_source?: string;
  hp: CharacterHP;
  speed: Record<string, number>;
  abilities: {
    str: number;
    dex: number;
    con: number;
    int: number;
    wis: number;
    cha: number;
  };
  proficiency_bonus: number;
  saves?: Record<string, string>;
  skills?: Record<string, string>;
  passive_perception: number;
  languages?: string[];
  tools?: string[];
  traits?: Array<{ name: string; description: string }>;
  actions?: Array<{ name: string; description: string }>;
  bonus_actions?: Array<{ name: string; description: string }>;
  reactions?: Array<{ name: string; description: string }>;
  feats?: string[];
  source?: string;
  last_updated?: string;
}

// Theme
export type Theme = 'light' | 'dark' | 'system';

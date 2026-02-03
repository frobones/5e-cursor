# Specification: Campaign Web UI

**Feature**: Campaign Web UI  
**Status**: Draft  
**Created**: 2026-02-02

## Overview

A read-only web interface for navigating and viewing D&D campaign data. The UI renders markdown content, enables cross-entity navigation, visualizes timelines and relationships, and provides a reference browser for spells, creatures, and items.

## Goals

- Provide a modern, responsive web interface for campaign data
- Enable seamless navigation between NPCs, locations, sessions, and other entities
- Render markdown content with proper styling and clickable cross-references
- Visualize campaign timeline and NPC relationships
- Browse D&D reference data (spells, creatures, items, rules)
- Support dark/light theme modes

## Non-Goals

- Editing campaign data through the UI (read-only for initial version)
- Multi-user collaboration or authentication
- Hosting on the internet (local-only)
- Mobile app or native desktop application

## User Stories

### US-001: View Campaign Dashboard

**As a** DM  
**I want to** see an overview of my campaign when I open the web UI  
**So that** I can quickly access key information and navigate to any section

**Acceptance Criteria**:
- Dashboard shows campaign name and setting
- Quick stats display (NPCs, locations, sessions count)
- Recent sessions are listed
- Navigation links to all major sections

### US-002: Browse NPCs

**As a** DM  
**I want to** view a list of all NPCs with filtering by role  
**So that** I can quickly find NPCs by their relationship to the party

**Acceptance Criteria**:
- NPC list shows name, role badge, and brief description
- Filter by role (ally, neutral, enemy)
- Search by name
- Click to view full NPC details

### US-003: View Entity Details

**As a** DM  
**I want to** view the full markdown content of any entity  
**So that** I can see all details including connections and notes

**Acceptance Criteria**:
- Full markdown rendered with proper formatting
- Internal links are clickable and navigate within the app
- Reference links show tooltips on hover
- Mermaid diagrams render inline

### US-004: Navigate Cross-References

**As a** DM  
**I want to** click on linked entities to navigate to their details  
**So that** I can explore connections between NPCs, locations, and sessions

**Acceptance Criteria**:
- Links to campaign entities navigate within the app
- Links to reference data (spells, items) show tooltips
- Breadcrumb or back navigation available
- Browser history works correctly

### US-005: View Timeline

**As a** DM  
**I want to** see a chronological timeline of campaign events  
**So that** I can review what happened when in the campaign

**Acceptance Criteria**:
- Events grouped by in-game day
- Session events, NPC appearances, and location discoveries shown
- Icons indicate event type
- Click events to navigate to source entity

### US-006: View Relationship Graph

**As a** DM  
**I want to** see a visual graph of NPC relationships  
**So that** I can understand the connections between characters

**Acceptance Criteria**:
- Mermaid flowchart displays relationships
- Click nodes to navigate to NPC details
- Legend shows relationship types

### US-007: Browse Reference Data

**As a** DM  
**I want to** browse spells, creatures, and items from my source books  
**So that** I can look up game rules and stat blocks during play

**Acceptance Criteria**:
- Tabbed interface for different reference types
- Filter by level (spells), CR (creatures), rarity (items)
- Search by name
- View full reference content

### US-008: Global Search

**As a** DM  
**I want to** search across all campaign and reference data  
**So that** I can quickly find anything by name or keyword

**Acceptance Criteria**:
- Search bar in header
- Keyboard shortcut (Cmd+K) opens search modal
- Results grouped by type
- Click result to navigate

### US-009: Dark Mode

**As a** DM  
**I want to** toggle between light and dark themes  
**So that** I can use the UI in different lighting conditions

**Acceptance Criteria**:
- Theme toggle in header
- Preference persisted in localStorage
- All components properly styled for both themes

## Technical Requirements

### Backend (FastAPI)

- REST API serving campaign and reference data
- Markdown parsing and metadata extraction
- Reference index integration
- File system watching for live updates
- WebSocket for change notifications

### Frontend (React + TypeScript)

- Vite build tooling
- React Router for navigation
- TanStack Query for data fetching
- TailwindCSS + CSS Modules for styling
- Lucide React for icons
- react-markdown for content rendering
- Mermaid for diagrams

## Constraints

- Local-only deployment (localhost)
- Read-only access (no write operations)
- Must work offline (no external API dependencies)
- Campaign data stored as markdown files
- Reference data from extracted JSON indexes

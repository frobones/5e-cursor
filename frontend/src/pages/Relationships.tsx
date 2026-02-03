import { useEffect, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, GitBranch, Users } from 'lucide-react';
import { getRelationships } from '@services/api';
import mermaid from 'mermaid';

// Initialize mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'neutral',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis',
  },
});

// Counter for unique Mermaid diagram IDs
let mermaidIdCounter = 0;

export default function Relationships() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [renderError, setRenderError] = useState<string | null>(null);
  const [svgContent, setSvgContent] = useState<string | null>(null);
  const location = useLocation();

  const { data: graph, isLoading, error } = useQuery({
    queryKey: ['relationships'],
    queryFn: getRelationships,
  });

  // Re-render diagram when route changes (handles back navigation)
  useEffect(() => {
    if (!graph?.mermaid) {
      setSvgContent(null);
      return;
    }

    const renderDiagram = async () => {
      try {
        setRenderError(null);

        // Use unique ID for each render to avoid Mermaid caching issues
        const diagramId = `mermaid-rel-${++mermaidIdCounter}`;

        const { svg } = await mermaid.render(diagramId, graph.mermaid);
        setSvgContent(svg);
      } catch (err) {
        console.error('Mermaid render error:', err);
        setRenderError('Failed to render relationship diagram');
        setSvgContent(null);
      }
    };

    renderDiagram();
  }, [graph?.mermaid, location.key]);

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <GitBranch className="h-8 w-8 text-pink-600" />
          <h1>NPC Relationships</h1>
        </div>
        {graph && (
          <div className="text-sm text-ink-500 dark:text-parchment-400">
            {graph.nodes.length} NPCs · {graph.edges.length} connections
          </div>
        )}
      </header>

      {isLoading && <p>Loading relationships...</p>}
      {error && <p className="text-red-600">Error loading relationships</p>}

      {graph && graph.nodes.length === 0 && (
        <div className="card text-center py-8">
          <p className="text-ink-500 dark:text-parchment-400 mb-4">
            No relationships found.
          </p>
          <p className="text-sm text-ink-400 dark:text-parchment-500">
            Add relationships between NPCs using the campaign manager CLI.
          </p>
        </div>
      )}

      {graph && graph.nodes.length > 0 && (
        <>
          {/* Mermaid Diagram */}
          <div className="card overflow-x-auto">
            <h2 className="font-display font-semibold text-lg mb-4">Relationship Graph</h2>
            {renderError ? (
              <div className="text-red-600 p-4">{renderError}</div>
            ) : svgContent ? (
              <div
                ref={containerRef}
                className="min-h-[300px] flex items-center justify-center"
                dangerouslySetInnerHTML={{ __html: svgContent }}
              />
            ) : (
              <div className="min-h-[300px] flex items-center justify-center text-ink-400">
                Loading diagram...
              </div>
            )}
          </div>

          {/* Node List */}
          <div className="card">
            <h2 className="font-display font-semibold text-lg mb-3">NPCs</h2>
            <p className="text-sm text-ink-500 dark:text-parchment-400 mb-4">
              Click an NPC to view their full profile and relationships.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {graph.nodes.map((node) => {
                const nodeEdges = graph.edges.filter(
                  (e) => e.source === node.id || e.target === node.id
                );

                return (
                  <Link
                    key={node.id}
                    to={`/npcs/${node.id}`}
                    className="card-link flex items-center gap-3 p-4 rounded-lg border border-parchment-200 dark:border-ink-700 bg-white dark:bg-ink-800 no-underline text-inherit hover:border-parchment-400 dark:hover:border-ink-500 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-parchment-500 focus-visible:ring-offset-2 dark:focus-visible:ring-parchment-400 dark:focus-visible:ring-offset-ink-900"
                  >
                    <Users className="h-5 w-5 shrink-0 text-ink-400 dark:text-parchment-500" aria-hidden />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium truncate">{node.name}</p>
                      <p className="text-xs text-ink-500 dark:text-parchment-400">
                        {nodeEdges.length} connection{nodeEdges.length !== 1 ? 's' : ''}
                        {node.role && ` · ${node.role}`}
                      </p>
                    </div>
                    <ChevronRight className="h-5 w-5 shrink-0 text-ink-400 dark:text-parchment-500" aria-hidden />
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Edges List */}
          <div className="card">
            <h2 className="font-display font-semibold text-lg mb-3">All Connections</h2>
            <div className="space-y-2">
              {graph.edges.map((edge, idx) => {
                const sourceNode = graph.nodes.find((n) => n.id === edge.source);
                const targetNode = graph.nodes.find((n) => n.id === edge.target);

                return (
                  <div
                    key={idx}
                    className="flex items-center gap-2 p-2 text-sm border-b border-parchment-100 dark:border-ink-700 last:border-0"
                  >
                    <Link
                      to={`/npcs/${edge.source}`}
                      className="font-medium text-parchment-700 dark:text-parchment-400 underline underline-offset-2 hover:text-parchment-900 dark:hover:text-parchment-200 cursor-pointer"
                    >
                      {sourceNode?.name || edge.source}
                    </Link>
                    <span className="text-ink-400">→</span>
                    <span className="badge badge-neutral">{edge.type}</span>
                    <span className="text-ink-400">→</span>
                    <Link
                      to={`/npcs/${edge.target}`}
                      className="font-medium text-parchment-700 dark:text-parchment-400 underline underline-offset-2 hover:text-parchment-900 dark:hover:text-parchment-200 cursor-pointer"
                    >
                      {targetNode?.name || edge.target}
                    </Link>
                    {edge.description && (
                      <span className="text-ink-500 dark:text-parchment-400 ml-2">
                        — {edge.description}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

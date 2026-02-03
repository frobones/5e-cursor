import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Link } from 'react-router-dom';
import type { Components } from 'react-markdown';

interface MarkdownViewerProps {
  content: string;
  /** Base path for resolving relative links (e.g., '/npcs' for NPC pages) */
  basePath?: string;
}

/**
 * Creates custom link renderer that converts internal markdown links to React Router links.
 */
function createComponents(basePath?: string): Components {
  return {
    a: ({ href, children, ...props }) => {
      // Check if it's an internal link (relative path to .md file)
      if (href && !href.startsWith('http') && !href.startsWith('mailto:')) {
        // Convert markdown file paths to routes
        // e.g., "../npcs/elara.md" -> "/npcs/elara"
        // e.g., "../../books/reference/spells/fireball.md" -> "/reference/spells/fireball"
        // e.g., "../../books/reference/species/human.md#resourceful" -> "/reference/species/human#resourceful"
        let routePath = href
          .replace(/\.md(#|$)/, '$1') // Remove .md before anchor or end
          .replace(/^\.\//, ''); // Remove leading ./

        // Handle reference paths
        if (routePath.includes('books/reference/')) {
          routePath = routePath.replace('books/reference/', 'reference/');
          routePath = routePath.replace(/^(\.\.\/)+/, ''); // Remove ../ for absolute reference paths
        } else if (routePath.startsWith('../')) {
          // Path goes up directory levels - remove ../ and use absolute path
          routePath = routePath.replace(/^(\.\.\/)+/, '');
        } else if (basePath && !routePath.startsWith('/') && !routePath.includes('/')) {
          // Simple relative path (just a filename) - prepend base path
          routePath = basePath + '/' + routePath;
        } else {
          // Remove any remaining ../ 
          routePath = routePath.replace(/^(\.\.\/)+/, '');
        }

        // Normalize to absolute path
        if (!routePath.startsWith('/')) {
          routePath = '/' + routePath;
        }

        return (
          <Link to={routePath} {...props}>
            {children}
          </Link>
        );
      }

      // External link
      return (
        <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
          {children}
        </a>
      );
    },
  };
}

export default function MarkdownViewer({ content, basePath }: MarkdownViewerProps) {
  // Remove the title heading if it's the first line (we show it separately)
  const processedContent = content.replace(/^#\s+.+\n/, '');
  const components = createComponents(basePath);

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {processedContent}
    </ReactMarkdown>
  );
}

import { ChevronRight, Home } from 'lucide-react';
import { Link } from 'react-router-dom';

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export default function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <nav className="flex items-center gap-1 text-sm text-ink-500 dark:text-parchment-400 mb-4">
      <Link
        to="/"
        className="flex items-center hover:text-ink-700 dark:hover:text-parchment-200 cursor-pointer hover:underline underline-offset-2"
      >
        <Home className="h-4 w-4" />
      </Link>

      {items.map((item, index) => (
        <span key={index} className="flex items-center gap-1">
          <ChevronRight className="h-4 w-4" />
          {item.path ? (
            <Link
              to={item.path}
              className="hover:text-ink-700 dark:hover:text-parchment-200 cursor-pointer hover:underline underline-offset-2"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-ink-700 dark:text-parchment-200 font-medium">
              {item.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
}

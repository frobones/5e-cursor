import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
      <h1 className="text-6xl font-display mb-4">404</h1>
      <p className="text-xl text-ink-600 dark:text-parchment-400 mb-6">
        Page not found
      </p>
      <Link to="/" className="btn btn-primary">
        <Home className="h-4 w-4 mr-2" />
        Back to Dashboard
      </Link>
    </div>
  );
}

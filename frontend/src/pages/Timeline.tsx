import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Clock, Calendar, Users, MapPin, Sword, Star, Sparkles, ChevronRight } from 'lucide-react';
import { getTimeline } from '@services/api';
import type { TimelineEvent } from '@/types';

const categoryIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  session: Calendar,
  npc: Users,
  location: MapPin,
  battle: Sword,
  start: Star,
  discovery: Sparkles,
  plot: Star,
  custom: Star,
  event: Star,
};

const categoryColors: Record<string, string> = {
  session: 'text-purple-600 bg-purple-100 dark:bg-purple-900/30',
  npc: 'text-green-600 bg-green-100 dark:bg-green-900/30',
  location: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30',
  battle: 'text-red-600 bg-red-100 dark:bg-red-900/30',
  start: 'text-amber-600 bg-amber-100 dark:bg-amber-900/30',
  discovery: 'text-cyan-600 bg-cyan-100 dark:bg-cyan-900/30',
  plot: 'text-pink-600 bg-pink-100 dark:bg-pink-900/30',
  custom: 'text-gray-600 bg-gray-100 dark:bg-gray-900/30',
  event: 'text-gray-600 bg-gray-100 dark:bg-gray-900/30',
};

function EventItem({ event }: { event: TimelineEvent }) {
  const Icon = categoryIcons[event.category] || Star;
  const colorClass = categoryColors[event.category] || categoryColors.custom;
  const isClickable = !!event.entity_path;

  const content = (
    <div className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
      isClickable
        ? 'hover:bg-parchment-100 dark:hover:bg-ink-700 cursor-pointer group'
        : ''
    }`}>
      <div className={`p-2 rounded-lg flex-shrink-0 ${colorClass}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className={`font-medium ${
          isClickable
            ? 'text-parchment-600 dark:text-parchment-400 underline decoration-parchment-400 dark:decoration-parchment-600 underline-offset-2 group-hover:text-parchment-800 dark:group-hover:text-parchment-200 group-hover:decoration-parchment-600 dark:group-hover:decoration-parchment-400'
            : 'text-ink-900 dark:text-parchment-100'
        }`}>
          {event.title}
        </p>
        {event.description && (
          <p className="text-sm text-ink-500 dark:text-parchment-400 mt-1">
            {event.description}
          </p>
        )}
        <div className="flex items-center gap-3 mt-1 text-xs text-ink-400 dark:text-parchment-500">
          <span className="capitalize">{event.category}</span>
          {event.session_number && (
            <span>Session {event.session_number}</span>
          )}
        </div>
      </div>
      {isClickable && (
        <ChevronRight className="h-4 w-4 text-ink-400 dark:text-parchment-500 flex-shrink-0 group-hover:text-parchment-600 dark:group-hover:text-parchment-300" />
      )}
    </div>
  );

  if (event.entity_path) {
    return (
      <Link
        to={event.entity_path}
        className="block rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-parchment-500 focus-visible:ring-offset-2 dark:focus-visible:ring-parchment-400 dark:focus-visible:ring-offset-ink-900"
      >
        {content}
      </Link>
    );
  }

  return content;
}

export default function Timeline() {
  const { data: timeline, isLoading, error } = useQuery({
    queryKey: ['timeline'],
    queryFn: getTimeline,
  });

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="h-8 w-8 text-cyan-600" />
          <h1>Timeline</h1>
        </div>
        {timeline && (
          <div className="text-sm text-ink-500 dark:text-parchment-400">
            Current Day: <span className="font-semibold">Day {timeline.current_day}</span>
            {' · '}
            {timeline.total_events} events
          </div>
        )}
      </header>

      {isLoading && <p>Loading timeline...</p>}
      {error && <p className="text-red-600">Error loading timeline</p>}

      {timeline && timeline.days.length === 0 && (
        <div className="card text-center py-8">
          <p className="text-ink-500 dark:text-parchment-400 mb-4">
            No timeline events yet.
          </p>
          <p className="text-sm text-ink-400 dark:text-parchment-500">
            Add in-game dates to sessions, NPCs, and locations to populate the timeline.
          </p>
        </div>
      )}

      {timeline && timeline.days.length > 0 && (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-parchment-200 dark:bg-ink-700" />

          {/* Days */}
          <div className="space-y-6">
            {timeline.days.map((day) => (
              <div key={day.day} className="relative pl-16">
                {/* Day marker */}
                <div className="absolute left-0 w-12 h-12 rounded-full bg-parchment-600 text-white flex items-center justify-center font-display font-bold text-sm">
                  {day.day}
                </div>

                {/* Day content */}
                <div className="card">
                  <h3 className="font-display font-semibold text-lg mb-3 text-parchment-700 dark:text-parchment-400">
                    {day.in_game_date}
                  </h3>
                  <div className="space-y-1">
                    {day.events.map((event, idx) => (
                      <EventItem key={idx} event={event} />
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

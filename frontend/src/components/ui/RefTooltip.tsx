import * as Tooltip from '@radix-ui/react-tooltip';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { getReferenceDetail } from '@services/api';

interface RefTooltipProps {
  type: string;
  slug: string;
  children: React.ReactNode;
}

export default function RefTooltip({ type, slug, children }: RefTooltipProps) {
  const [open, setOpen] = useState(false);

  const { data: reference, isLoading } = useQuery({
    queryKey: ['reference', type, slug],
    queryFn: () => getReferenceDetail(type, slug),
    enabled: open, // Only fetch when tooltip is open
    staleTime: 1000 * 60 * 10, // Cache for 10 minutes
  });

  return (
    <Tooltip.Provider delayDuration={300}>
      <Tooltip.Root open={open} onOpenChange={setOpen}>
        <Tooltip.Trigger asChild>{children}</Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            className="z-50 max-w-sm p-3 bg-white dark:bg-ink-800 rounded-lg shadow-lg border border-parchment-200 dark:border-ink-700"
            sideOffset={5}
          >
            {isLoading ? (
              <p className="text-sm text-ink-500">Loading...</p>
            ) : reference ? (
              <div>
                <h4 className="font-display font-semibold text-ink-900 dark:text-parchment-100">
                  {reference.name}
                </h4>
                {reference.source && (
                  <p className="text-xs text-ink-500 dark:text-parchment-400 mb-2">
                    {reference.source}
                  </p>
                )}
                {/* Show first 200 chars of content */}
                <p className="text-sm text-ink-700 dark:text-parchment-300 line-clamp-4">
                  {reference.content
                    .replace(/^#.+\n/, '') // Remove title
                    .replace(/\*\*[^*]+\*\*:\s*[^\n]+\n/g, '') // Remove metadata
                    .replace(/[#*_`]/g, '') // Remove markdown
                    .trim()
                    .slice(0, 200)}
                  ...
                </p>
              </div>
            ) : (
              <p className="text-sm text-ink-500">Not found</p>
            )}
            <Tooltip.Arrow className="fill-white dark:fill-ink-800" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}

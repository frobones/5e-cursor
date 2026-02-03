/**
 * Hook for real-time file change notifications via WebSocket.
 *
 * Connects to the backend WebSocket and invalidates React Query caches
 * when campaign files are created, modified, or deleted.
 */

import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface FileChangeMessage {
  type: 'file_change';
  event_type: 'created' | 'modified' | 'deleted';
  entity: string;
  slug: string;
}

interface ConnectionMessage {
  type: 'connected';
  message: string;
}

type WebSocketMessage = FileChangeMessage | ConnectionMessage | { type: 'pong' };

// Map entity types to React Query cache keys
const entityToQueryKeys: Record<string, string[][]> = {
  npcs: [['npcs'], ['npc']],
  locations: [['locations'], ['location']],
  sessions: [['sessions'], ['session']],
  encounters: [['encounters'], ['encounter']],
  characters: [['characters'], ['character'], ['party']],
  party: [['party']],
  campaign: [['campaign'], ['campaign-stats']],
};

export function useFileChanges(): void {
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    // Determine WebSocket URL based on current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[FileWatcher] Connected');
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          if (message.type === 'file_change') {
            console.log('[FileWatcher] File changed:', message);

            // Get query keys to invalidate
            const queryKeys = entityToQueryKeys[message.entity] || [];

            // Invalidate related queries
            for (const key of queryKeys) {
              queryClient.invalidateQueries({ queryKey: key });
            }

            // Also invalidate specific entity if slug is provided
            if (message.slug && message.entity) {
              // Invalidate the specific entity detail query
              queryClient.invalidateQueries({
                queryKey: [message.entity.replace(/s$/, ''), message.slug],
              });
            }

            // Always refresh campaign stats on any change
            queryClient.invalidateQueries({ queryKey: ['campaign-stats'] });
          } else if (message.type === 'connected') {
            console.log('[FileWatcher]', message.message);
          }
        } catch (e) {
          console.warn('[FileWatcher] Failed to parse message:', e);
        }
      };

      ws.onclose = (event) => {
        console.log('[FileWatcher] Disconnected:', event.code, event.reason);
        wsRef.current = null;

        // Reconnect with exponential backoff
        if (!event.wasClean) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectAttempts.current++;
          console.log(`[FileWatcher] Reconnecting in ${delay}ms...`);

          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, delay);
        }
      };

      ws.onerror = (error) => {
        console.warn('[FileWatcher] WebSocket error:', error);
      };
    } catch (e) {
      console.warn('[FileWatcher] Failed to connect:', e);
    }
  }, [queryClient]);

  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounted');
      }
    };
  }, [connect]);

  // Send periodic pings to keep connection alive
  useEffect(() => {
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 30000);

    return () => clearInterval(pingInterval);
  }, []);
}

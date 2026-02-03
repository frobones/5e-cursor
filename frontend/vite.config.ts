import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@services': path.resolve(__dirname, './src/services'),
      '@types': path.resolve(__dirname, './src/types'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        // Suppress benign EPIPE errors when WebSocket closes abruptly
        configure: (proxy) => {
          proxy.on('error', (err) => {
            // Ignore EPIPE errors (broken pipe when client disconnects)
            if ((err as NodeJS.ErrnoException).code !== 'EPIPE') {
              console.error('[ws proxy error]', err.message);
            }
          });
        },
      },
    },
  },
});

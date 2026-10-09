// LOCATION: frontend/vite.config.ts  (replaces your old vite_config.ts)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// API calls go straight to VITE_API_URL (see src/services/api.ts), so no dev proxy is needed.
export default defineConfig({
  base: '/',
  plugins: [react()],
  server: { port: 3000, strictPort: true },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['chart.js', 'react-chartjs-2'],
        },
      },
    },
  },
});
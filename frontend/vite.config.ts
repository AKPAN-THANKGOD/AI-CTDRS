import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    strictPort: true,
    
    // Proxy API requests to backend during development
    proxy: {
      // Proxy /api requests to your Render backend
      '/api': {
        target: 'https://ai-ctdrs-backend.onrender.com', // 🔧 Replace with YOUR Render URL
        changeOrigin: true,
        secure: true,
        // Remove this if you don't want to rewrite the path
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
      
      // Proxy WebSocket connections for real-time notifications
      '/ws': {
        target: 'wss://ai-ctdrs-backend.onrender.com', // 🔧 Replace with YOUR Render URL (wss:// for HTTPS)
        ws: true,
        changeOrigin: true,
        secure: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    // Optimize bundle size
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
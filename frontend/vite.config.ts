import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Vite automatically exposes env vars starting with VITE_ via import.meta.env.
// Configure envDir to read .env from the project root.
export default defineConfig({
  envDir: path.resolve(__dirname, '..'),
  server: {
    port: 3000,
    host: '0.0.0.0',
  },
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
});

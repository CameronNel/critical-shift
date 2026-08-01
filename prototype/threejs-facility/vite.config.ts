import { defineConfig } from 'vite';

// The prototype is inspected from a phone on the local network and from cloud
// preview URLs, so the dev server binds every interface by default.
export default defineConfig({
  base: './',
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    // Cloud dev environments proxy the port behind an arbitrary hostname.
    allowedHosts: true,
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
    allowedHosts: true,
  },
  build: {
    target: 'es2022',
    outDir: 'dist',
    sourcemap: true,
  },
});

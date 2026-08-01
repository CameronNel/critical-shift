import { defineConfig } from 'vite';

/**
 * Build variant for `tools/inline.mjs`: one JS chunk, no source map, so the
 * whole prototype can collapse into a single self-contained HTML file.
 */
export default defineConfig({
  base: './',
  build: {
    target: 'es2022',
    outDir: 'dist-inline',
    emptyOutDir: true,
    sourcemap: false,
    chunkSizeWarningLimit: 4000,
    rollupOptions: { output: { inlineDynamicImports: true } },
    rolldownOptions: { output: { codeSplitting: false } },
  },
});

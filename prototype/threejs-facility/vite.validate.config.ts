import { defineConfig } from 'vite';

/**
 * Bundles the headless facility validator for Node. Kept separate from the
 * app build so the browser bundle stays untouched.
 */
export default defineConfig({
  build: {
    ssr: 'src/tools/validateCli.ts',
    outDir: 'dist-tools',
    emptyOutDir: true,
    target: 'node20',
    minify: false,
    rollupOptions: { output: { entryFileNames: 'validate.mjs' } },
    rolldownOptions: { output: { entryFileNames: 'validate.mjs' } },
  },
});

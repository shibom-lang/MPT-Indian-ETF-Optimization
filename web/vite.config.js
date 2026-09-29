import { resolve } from 'path'
import { defineConfig } from 'vite'

// Multi-page app: Vite will bundle all three HTML files as separate entries.
// This ensures dashboard.html and compare.html are included in the production
// build output that Vercel serves.
const root = import.meta.dirname

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main:      resolve(root, 'index.html'),
        dashboard: resolve(root, 'dashboard.html'),
        compare:   resolve(root, 'compare.html'),
      },
    },
  },
})

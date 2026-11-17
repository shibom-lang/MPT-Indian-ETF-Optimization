import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import { defineConfig } from 'vite'

// Multi-page app: Vite will bundle all three HTML files as separate entries.
// This ensures dashboard.html and compare.html are included in the production
// build output that Vercel serves.
const __dirname = dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main:      resolve(__dirname, 'index.html'),
        dashboard: resolve(__dirname, 'dashboard.html'),
        compare:   resolve(__dirname, 'compare.html'),
      },
    },
  },
})

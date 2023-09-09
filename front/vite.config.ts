import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  base: './', // XXX: important pour servir depuis un path-prefix
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    target: 'esnext', // XXX: Because we use very new features
    outDir: '../api/src/our_celery_manager/app/static', // XXX: Because frontend is served by API
  }
})

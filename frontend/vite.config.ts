import { defineConfig } from 'vite';
import { devtools } from '@tanstack/devtools-vite';

import { tanstackStart } from '@tanstack/react-start/plugin/vite';

import viteReact from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

const config = defineConfig({
  resolve: { tsconfigPaths: true },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  plugins: [
    devtools(),
    // netlify(), disable this plugin until we start deploying
    tailwindcss(),
    tanstackStart(),
    viteReact(),
  ],
});

export default config;

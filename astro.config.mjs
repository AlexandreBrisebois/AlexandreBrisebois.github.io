import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  site: 'https://srvrlss.dev',
  integrations: [
    react(),
    mdx()
  ],
  output: 'static',
});

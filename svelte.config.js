import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),

  kit: {
    adapter: adapter({
      pages: 'dist',
      assets: 'dist',
      fallback: undefined,
      precompress: false,
      strict: true
    }),
    prerender: {
      handleHttpError: ({ status, path, referrer, referenceType }) => {
        if (path === '/favicon.png' || path === '/sharecard.jpg') {
          return;
        }
        throw new Error(`${status} ${path}`);
      }
    }
  }
};

export default config;

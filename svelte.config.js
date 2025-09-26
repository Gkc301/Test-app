import { mdsvex } from 'mdsvex';
import adapter from '@sveltejs/adapter-netlify';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Preprocessors: Svelte + mdsvex
	preprocess: [vitePreprocess(), mdsvex()],

	kit: {
		adapter: adapter(),   // 👈 now using Netlify adapter
	},

	extensions: ['.svelte', '.svx']
};

export default config;

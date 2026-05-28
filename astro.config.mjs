// @ts-check
import { defineConfig } from "astro/config";
import cloudflare from "@astrojs/cloudflare";
import sitemap from "@astrojs/sitemap";
import mdx from "@astrojs/mdx";
import tailwindcss from "@tailwindcss/vite";

// https://astro.build/config
export default defineConfig({
	site: "https://ancient-philosophia.org",
	output: "static",
	prefetch: {
		prefetchAll: false,
		defaultStrategy: "hover",
	},
	adapter: cloudflare({
		imageService: "passthrough",
	}),
	integrations: [
		sitemap({
			changefreq: "monthly",
			priority: 0.7,
			lastmod: new Date(),
		}),
		mdx(),
	],
	vite: {
		plugins: [tailwindcss()],
		build: {
			cssCodeSplit: true,
		},
	},
});

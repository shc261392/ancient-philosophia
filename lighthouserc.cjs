/** @type {import('@lhci/cli').LighthouseRcConfig} */
module.exports = {
	ci: {
		collect: {
			url: [
				"http://localhost:4322/",
				"http://localhost:4322/civilizations/",
				"http://localhost:4322/languages/",
				"http://localhost:4322/artifacts/",
				"http://localhost:4322/myths/",
			],
			numberOfRuns: 1,
			settings: {
				chromeFlags: "--no-sandbox --headless --disable-gpu",
				chromePath: process.env.CHROME_PATH || "/usr/bin/google-chrome",
			},
		},
		assert: {
			preset: "lighthouse:no-pwa",
			assertions: {
				"categories:performance": ["warn", { minScore: 0.9 }],
				"categories:accessibility": ["error", { minScore: 0.95 }],
				"categories:best-practices": ["warn", { minScore: 0.95 }],
				"categories:seo": ["warn", { minScore: 0.95 }],
				// Text compression / HTTP/2 push handled by Cloudflare Workers in production
				"uses-text-compression": "off",
				// CSS render-blocking is infrastructure-level — Cloudflare serves assets over HTTP/2 with
				// early hints in production; not meaningful in local preview
				"render-blocking-resources": "off",
				"render-blocking-insight": "off",
				"network-dependency-tree-insight": "off",
				// Document latency in local preview server is not representative of production CDN latency
				"document-latency-insight": "off",
				// DOM size on home page is inherent to listing all civilizations
				"dom-size": "off",
				"dom-size-insight": "off",
				// Images serve dual purpose (thumbnail + lightbox); full-resolution intentional
				"uses-responsive-images": "off",
				"modern-image-formats": "off",
				"image-delivery-insight": "off",
			},
		},
		upload: {
			target: "filesystem",
			outputDir: ".lighthouseci",
		},
	},
};

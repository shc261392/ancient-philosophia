# Aristeia & Philotimia — Copilot Instructions

## Project Overview
An open-source educational website for learning ancient history and languages, covering civilizations from Sumer to Rome. Built with Astro (v5+), Tailwind CSS v4, deployed to Cloudflare Workers/Pages.

## Tech Stack
- **Framework:** Astro 5+ (static-first, content collections with glob loaders)
- **Styling:** Tailwind CSS v4 (CSS-first config via `@theme inline` in global.css)
- **Deployment:** Cloudflare Workers/Pages (wrangler, `@astrojs/cloudflare` adapter)
- **Content:** MDX files in `src/content/` with Zod schemas in `src/content.config.ts`
- **Build:** `npm run build` → `dist/` → Cloudflare

## Architecture Decisions
- **Static HTML first** — All pages prerendered. Use `output: 'static'` with the CF adapter for future SSR opt-in
- **Dark mode only** — Ancient Greek color palette defined as CSS custom properties in `src/styles/global.css`
- **Content Collections** — Three collections: `civilizations`, `languages`, `resources` with typed schemas
- **SEO/GEO on every page** — `SEOHead.astro` component handles meta tags, Open Graph, Twitter cards, and JSON-LD structured data
- **Mobile-first responsive** — All components use Tailwind responsive utilities

## Color Palette (defined in global.css `@theme inline`)
- Backgrounds: `bg-primary` (#0f0f14), `bg-secondary` (#1a1a24), `bg-tertiary` (#24243a), `bg-card` (#1e1e2e)
- Text: `fg-primary` (#e8e0d4), `fg-secondary` (#b8b0a4), `fg-muted` (#7a7268)
- Accents: `terracotta` (#c1604e), `gold-leaf` (#c9a84c), `tyrian` (#7b2d5f), `aegean` (#2a6478), `bronze` (#6d7c3e), `marble` (#d4cfc6)

## File Structure
```
src/
  components/     # Astro components (Nav, Footer, Hero, Card, SEOHead)
  content/        # Content collections
    civilizations/ # 23 MDX files (sumer.mdx, akkad.mdx, etc.)
    languages/     # 6 MDX files (middle-egyptian.mdx, akkadian.mdx, etc.)
    resources/     # Learning resource entries (.md)
  layouts/        # BaseLayout.astro
  pages/          # Route pages
    civilizations/ # Index + [...slug].astro dynamic route
    languages/     # Index + [...slug].astro dynamic route
    mindmap/       # Learning mindmap
    resources/     # Resource directory
    roadmap/       # Product roadmap
  styles/         # global.css (Tailwind theme + custom styles)
```

## Content Guidelines
- **Tone:** Scholarly but accessible. Suitable for self-directed adult learners
- **Citations:** Prefer consensus academic sources. Always include a "Learning Resources" section
- **Accuracy:** Cross-reference multiple sources. Prefer peer-reviewed works and major digital projects (ORACC, Perseus, CDLI, etc.)
- **License:** Site code is GPL-3.0. External content retains its original license with attribution

## Authoritative Sources for Ancient History
- **Mesopotamia:** ORACC, CDLI, ETCSL, ePSD2; books by Van De Mieroop, Kuhrt, Foster, Kramer
- **Egypt:** TLA, Digital Egypt (UCL), UCLA Encyclopedia of Egyptology; books by Allen, Shaw, Kemp
- **Greece:** Perseus Digital Library, Logeion, Beazley Archive; books by Osborne, Cartledge, Chadwick
- **Rome:** LacusCurtius, Pleiades; books by Beard, Cornell, Goldsworthy
- **Hittites:** Hethitologie Portal, CHD; books by Bryce, van den Hout
- **General:** Livius.org, Pleiades gazetteer, ASOR

## Development Commands
```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run deploy   # Build + deploy to Cloudflare
```

## Code Style
- Use Astro components (.astro) for pages and layouts
- Use MDX for content with frontmatter schemas
- CSS custom properties via Tailwind v4 `@theme inline`
- Use `var(--color-*)` for all color references in component styles
- Keep components simple — prefer static HTML over client-side JS
- When JS is needed, use `<script>` tags in Astro components (island architecture)

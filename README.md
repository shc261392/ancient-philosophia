# Ancient Philosophia

An open-source educational website for learning ancient history and languages, covering civilizations from Sumer to Rome.

**Deployed at [ancient-philosophia.org](https://ancient-philosophia.org)**

## Overview

This site offers scholarly but accessible content for self-directed adult learners interested in the ancient world. It covers:

- **34 civilizations** — from Sumer (c. 4500 BCE) through the Roman Empire (27 BCE – 476 CE)
- **21 ancient languages** — from Middle Egyptian and Akkadian to Classical Latin and Koine Greek
- **20 myths & religions** — pantheons, epics, deities, and religious traditions across cultures
- **12 writing systems** — comparison of cuneiform, hieroglyphs, Linear scripts, alphabets
- **14 artifact collections** — museums and archaeological sites for exploration
- **23 learning resources** — curated databases and scholarly tools
- **Interactive mindmap** — guided study paths organized by region and difficulty
- **Product roadmap** — planned features including maps, quizzes, and community tools

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | [Astro](https://astro.build) 6+ (static-first, content collections with glob loaders) |
| Styling | [Tailwind CSS](https://tailwindcss.com) v4 (CSS-first config via `@theme inline`) |
| Content | MDX with Zod-validated schemas, 5 content collections |
| Deployment | [Cloudflare Workers](https://workers.cloudflare.com) via Wrangler |
| Secrets | [dotenvx](https://dotenvx.com) encrypted `.env.production` + GitHub Actions |

## Getting Started

**Requirements:** Node 24+, pnpm 10+, [GitHub CLI](https://cli.github.com) (for secrets only)

```bash
# Install dependencies
pnpm install

# Start dev server at localhost:4321
pnpm dev

# Build for production
pnpm build

# Preview production build locally
pnpm preview
```

## Deployment Setup

### Local Deployment (manual)

Deploy via dotenvx (decrypts `.env.production` and passes secrets to wrangler):

```bash
pnpm deploy
```

### CI/CD Deployment (GitHub Actions)

Set up the `DOTENV_PRIVATE_KEY_PRODUCTION` secret in your repository to enable automated deploys:

```bash
# Add the secret to GitHub (requires gh CLI and repo push access)
gh secret set DOTENV_PRIVATE_KEY_PRODUCTION < .env.keys
```

This command:
1. Reads the private key from `.env.keys` (created when you ran `pnpm encrypt`)
2. Adds it as a GitHub secret visible to all Actions in the repo
3. CI/CD pipeline decrypts `.env.production` at deploy time and passes `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` to Wrangler

**One-time setup (for repo maintainers):**

```bash
# 1. Copy and fill in credentials
cp .env.example .env.production
# Edit with real CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID

# 2. Encrypt in-place (creates .env.keys with the private key)
pnpm encrypt

# 3. Commit .env.production (remove from .gitignore first, it's safe — it's encrypted)
git add .env.production
git commit -m "ci(env): add encrypted .env.production"

# 4. Add the private key as a GitHub secret
gh secret set DOTENV_PRIVATE_KEY_PRODUCTION < .env.keys

# 5. .env.keys is on your local machine only — NEVER commit it
```

## Project Structure

```
src/
├── components/        # Astro components (Nav, Footer, SEOHead, ImageLightbox)
├── content/
│   ├── civilizations/ # 34 MDX entries (sumer.mdx through scythians.mdx)
│   ├── languages/     # 21 MDX entries (akkadian.mdx through vulgar-latin.mdx)
│   ├── myths/         # 20 MDX entries (pantheons, epics, deities, heroes)
│   ├── artifacts/     # 14 MD entries (museums and archaeological sites)
│   └── resources/     # 23 MD entries (learning resources)
├── layouts/           # BaseLayout.astro
├── pages/
│   ├── civilizations/ # Index + dynamic [...slug] routes
│   ├── languages/     # Index + dynamic [...slug] routes
│   ├── myths/         # Index + dynamic [...slug] routes with ToC
│   ├── artifacts/     # Image gallery with lightbox
│   ├── writing-systems/ # Comparison table and evolution
│   ├── mindmap/       # Learning mindmap & study paths
│   ├── faq/           # FAQ page (missing content, error reporting, etc.)
│   ├── resources/     # Resource directory
│   └── roadmap/       # Product roadmap
└── styles/            # global.css (Tailwind theme + custom styles)
```

## Design

Dark-only theme with an ancient Greek color palette (defined in `src/styles/global.css`):

- **Attic Red** `#8B3A2A` / `#B85442` — primary accent
- **Gold Leaf** `#c9a84c` — headings and highlights
- **Terracotta** `#c1604e` — decorative accent
- **Aegean Blue** `#2a6478` — links and interactive elements
- **Bronze** `#6d7c3e` — success states
- **Marble** `#d4cfc6` — borders and dividers
- **Dark backgrounds** — nested layers from `#0f0f14` (primary) to `#1e1e2e` (card)

All colors defined as CSS custom properties (`--color-*`) for easy theming.

## Content Standards

- **Tone**: Scholarly but accessible — for self-directed adult learners
- **Sources**: Peer-reviewed scholarship and major digital humanities projects
- **Scope**: Every article includes a "Learning Resources" section
- **Key references**: ORACC, CDLI, Perseus Digital Library, TLA, Logeion, Pleiades, Beazley Archive, ETCSL, ISAC (Oriental Institute)

## Contributing

Contributions are welcome! See the [Roadmap](/roadmap) for planned features and join us on [GitHub](https://github.com/shc261392/ancient-philosophia).

### How to contribute:

- **Content**: Write or improve civilization, language, or myth articles
- **Features**: Fix bugs, improve accessibility, or optimize performance
- **Resources**: Add new learning resources or update links
- **Reporting**: Found an error? See the [FAQ](/faq#report-error) for how to report it

## Support

For questions, corrections, or to report misleading information, please:

- **Visit the [FAQ](/faq)** for common questions
- **Open an issue** on [GitHub](https://github.com/shc261392/ancient-philosophia/issues)
- **Email** support@ancient-philosophia.org

## License

Site code is licensed under [GPL-3.0](LICENSE). External content retains its original license with proper attribution.

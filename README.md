# Aristeia & Philotimia

An open-source educational website for learning ancient history and languages, covering civilizations from Sumer to Rome.

> **ἀριστεία** (*aristeia*) — the moment of supreme excellence  
> **φιλοτιμία** (*philotimia*) — the love of honour through learning

## Overview

This site offers scholarly but accessible content for self-directed adult learners interested in the ancient world. It covers:

- **23 civilizations** — from Sumer (c. 4500 BCE) through the Roman Empire (27 BCE – 476 CE)
- **6 ancient languages** — Middle Egyptian, Akkadian, Sumerian, Hittite, Attic Greek, Classical Latin
- **16+ learning resources** — curated databases, textbooks, and online tools
- **Learning mindmap** — guided study paths organized by region and difficulty
- **Product roadmap** — planned features including interactive maps, quizzes, and community tools

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | [Astro](https://astro.build) 5+ (static-first, content collections) |
| Styling | [Tailwind CSS](https://tailwindcss.com) v4 (CSS-first config) |
| Content | MDX with Zod-validated schemas |
| Deployment | [Cloudflare Pages](https://pages.cloudflare.com) via Wrangler |

## Getting Started

**Requirements:** Node 24+, pnpm 10+

```bash
# Install dependencies
pnpm install

# Start dev server at localhost:4321
pnpm dev

# Build for production
pnpm build

# Preview production build locally
pnpm preview

# Deploy to Cloudflare Pages
pnpm deploy
```

## Project Structure

```
src/
├── components/        # Astro components (Nav, Footer, Hero, Card, SEOHead)
├── content/
│   ├── civilizations/ # 23 MDX files (sumer.mdx, akkad.mdx, etc.)
│   ├── languages/     # 6 MDX files (middle-egyptian.mdx, akkadian.mdx, etc.)
│   └── resources/     # 16 learning resource entries (.md)
├── layouts/           # BaseLayout.astro
├── pages/
│   ├── civilizations/ # Index + dynamic [slug] routes
│   ├── languages/     # Index + dynamic [slug] routes
│   ├── mindmap/       # Learning mindmap & study paths
│   ├── resources/     # Resource directory
│   └── roadmap/       # Product roadmap
└── styles/            # global.css (Tailwind theme + custom styles)
```

## Design

Dark-only theme with an ancient Greek color palette:

- **Terracotta** `#c1604e` — primary accent
- **Gold Leaf** `#c9a84c` — headings and highlights
- **Tyrian Purple** `#7b2d5f` — decorative accent
- **Aegean Blue** `#2a6478` — links and interactive elements
- **Bronze** `#6d7c3e` — success states
- **Marble** `#d4cfc6` — borders and dividers

## Content Guidelines

- Scholarly but accessible tone for self-directed adult learners
- Consensus academic sources preferred (peer-reviewed, major digital projects)
- Every content page includes a "Learning Resources" section
- Key references: ORACC, CDLI, Perseus Digital Library, TLA, Logeion, Pleiades

## Contributing

Contributions are welcome! See the [Roadmap](/src/pages/roadmap/index.astro) for planned features.

- Content corrections and additions
- New civilization or language entries
- Accessibility improvements
- Bug fixes and performance optimizations

## License

Site code is licensed under [GPL-3.0](LICENSE). External content retains its original license with proper attribution.

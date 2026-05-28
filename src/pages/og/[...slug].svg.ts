import type { APIRoute, GetStaticPaths } from 'astro';
import { getCollection } from 'astro:content';

const COLLECTIONS = ['civilizations', 'languages', 'myths', 'poems', 'artifacts'] as const;
type CollectionKey = (typeof COLLECTIONS)[number];

const COLLECTION_LABEL: Record<CollectionKey, string> = {
  civilizations: 'Civilization',
  languages: 'Language',
  myths: 'Myth & Deity',
  poems: 'Poem & Epic',
  artifacts: 'Museum & Site',
};

export const getStaticPaths: GetStaticPaths = async () => {
  const paths: { params: { slug: string }; props: { title: string; subtitle: string; label: string } }[] = [];
  for (const key of COLLECTIONS) {
    const entries = await getCollection(key as CollectionKey);
    for (const entry of entries) {
      const data = entry.data as Record<string, unknown>;
      const title = String(data.title ?? entry.id);
      const subtitle = String(
        data.dateRange ?? data.period ?? data.region ?? data.tradition ?? data.location ?? 'Ancient Philosophia'
      );
      paths.push({
        params: { slug: `${key}/${entry.id}` },
        props: { title, subtitle, label: COLLECTION_LABEL[key] },
      });
    }
  }
  return paths;
};

function escapeXml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function wrapTitle(title: string, maxCharsPerLine = 26, maxLines = 3): string[] {
  const words = title.split(/\s+/);
  const lines: string[] = [];
  let current = '';
  for (const word of words) {
    if ((current + ' ' + word).trim().length > maxCharsPerLine && current) {
      lines.push(current);
      current = word;
      if (lines.length === maxLines - 1) break;
    } else {
      current = (current ? current + ' ' : '') + word;
    }
  }
  if (current) lines.push(current);
  if (lines.length > maxLines) {
    const last = lines.slice(maxLines - 1).join(' ');
    lines.length = maxLines;
    lines[maxLines - 1] = last.length > maxCharsPerLine ? last.slice(0, maxCharsPerLine - 1) + '…' : last;
  }
  return lines;
}

export const GET: APIRoute = ({ props }) => {
  const { title, subtitle, label } = props as { title: string; subtitle: string; label: string };
  const lines = wrapTitle(title);
  const fontSize = lines.length >= 3 ? 70 : lines.length === 2 ? 84 : 96;
  const lineHeight = fontSize * 1.05;
  const startY = 320 - ((lines.length - 1) * lineHeight) / 2;

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" role="img" aria-label="${escapeXml(title)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0f0f14"/>
      <stop offset="55%" stop-color="#1a1a24"/>
      <stop offset="100%" stop-color="#24243a"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.85" cy="0.15" r="0.9">
      <stop offset="0%" stop-color="#c9a84c" stop-opacity="0.22"/>
      <stop offset="60%" stop-color="#c9a84c" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#glow)"/>
  <g stroke="#c9a84c" stroke-opacity="0.4" stroke-width="1.5" fill="none">
    <line x1="60" y1="80" x2="1140" y2="80"/>
    <line x1="60" y1="550" x2="1140" y2="550"/>
  </g>
  <text x="60" y="150" font-family="Georgia, 'Noto Serif', serif" font-size="28" fill="#c9a84c" letter-spacing="5">ANCIENT · PHILOSOPHIA</text>
  <text x="60" y="190" font-family="'Helvetica Neue', Arial, sans-serif" font-size="22" fill="#8fa052" letter-spacing="3">${escapeXml(label.toUpperCase())}</text>
  ${lines
    .map(
      (line, i) =>
        `<text x="60" y="${startY + i * lineHeight}" font-family="Georgia, 'Noto Serif', serif" font-size="${fontSize}" font-weight="700" fill="#e8e0d4">${escapeXml(line)}</text>`
    )
    .join('\n  ')}
  <text x="60" y="470" font-family="Georgia, 'Noto Serif', serif" font-size="30" fill="#b8b0a4">${escapeXml(subtitle)}</text>
  <text x="60" y="510" font-family="'Helvetica Neue', Arial, sans-serif" font-size="22" fill="#7a7268">ancient-philosophia.org</text>
</svg>`;

  return new Response(svg, {
    headers: {
      'Content-Type': 'image/svg+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  });
};

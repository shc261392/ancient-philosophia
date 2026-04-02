import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const civilizations = defineCollection({
  loader: glob({ base: './src/content/civilizations', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    period: z.string(),
    region: z.string(),
    dateRange: z.string(),
    image: z.string().optional(),
    tags: z.array(z.string()).default([]),
    sortOrder: z.number().default(0),
  }),
});

const languages = defineCollection({
  loader: glob({ base: './src/content/languages', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    family: z.string(),
    script: z.string(),
    period: z.string(),
    difficulty: z.enum(['beginner', 'intermediate', 'advanced']).default('intermediate'),
    tags: z.array(z.string()).default([]),
    sortOrder: z.number().default(0),
  }),
});

const resources = defineCollection({
  loader: glob({ base: './src/content/resources', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.enum(['book', 'website', 'course', 'tool', 'database', 'video']),
    url: z.string().url().optional(),
    free: z.boolean().default(true),
    topics: z.array(z.string()).default([]),
  }),
});

export const collections = { civilizations, languages, resources };

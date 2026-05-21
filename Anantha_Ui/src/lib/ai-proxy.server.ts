import { ALL_VERSES, getVerseOfDay, searchVerses, type Verse } from "./verses";

const TIMEOUT_MS = 10_000;

const FALLBACK_REPLIES = [
  "The Gita reminds us that peace is found not in changing the world, but in steadying the mind. Act with devotion, release the fruits, and let stillness become your foundation.",
  "Krishna teaches Arjuna that the self is eternal — untouched by sorrow, fire, or time. When you remember this, fear softens and clarity returns.",
  "Equanimity in success and failure is the heart of yoga. Begin small: notice when you grasp at outcomes, and gently return to the present action.",
];

function getServiceUrl(): string | null {
  const url = process.env.AI_SERVICE_URL;
  if (!url || url.trim().length === 0) return null;
  return url.replace(/\/+$/, "");
}

export async function proxy(
  pathname: string,
  init: RequestInit,
): Promise<Response | null> {
  const base = getServiceUrl();
  if (!base) return null;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(`${base}${pathname}`, { ...init, signal: controller.signal });
    return res;
  } catch (err) {
    console.error(`AI proxy ${pathname} failed:`, err);
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

export function mockSearch(query: string): { results: Verse[] } {
  return { results: searchVerses(query ?? "") };
}

export function mockChat(_prompt: string): { content: string; citations: Verse[] } {
  const pool = [...ALL_VERSES];
  const citations: Verse[] = [];
  for (let i = 0; i < 3 && pool.length; i++) {
    citations.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
  }
  return {
    content: FALLBACK_REPLIES[Math.floor(Math.random() * FALLBACK_REPLIES.length)],
    citations,
  };
}

export function mockDaily(): Verse {
  return getVerseOfDay();
}

export function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
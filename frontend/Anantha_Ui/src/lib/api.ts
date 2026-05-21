import type { Verse } from "./verses";
import { ALL_VERSES, getVerseOfDay, searchVerses } from "./verses";

export type ChatApiResponse = {
  content: string;
  citations: Verse[];
};

export type SearchApiResponse = {
  results: Verse[];
};

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path, { method: "GET" });
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

export async function searchApi(query: string): Promise<Verse[]> {
  try {
    const data = await postJson<SearchApiResponse | Verse[]>("/api/search", { query });
    if (Array.isArray(data)) return data;
    return data.results ?? [];
  } catch (err) {
    console.error("searchApi failed, falling back to local:", err);
    return searchVerses(query);
  }
}

export async function chatApi(
  prompt: string,
  context?: { verseId?: string },
): Promise<ChatApiResponse> {
  try {
    return await postJson<ChatApiResponse>("/api/chat", { prompt, context });
  } catch (err) {
    console.error("chatApi failed, falling back to local:", err);
    const pool = [...ALL_VERSES];
    const citations: Verse[] = [];
    for (let i = 0; i < 3 && pool.length; i++) {
      citations.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
    }
    return {
      content:
        "The Gita reminds us that peace is found not in changing the world, but in steadying the mind. Act with devotion, release the fruits, and let stillness become your foundation.",
      citations,
    };
  }
}

export async function getDailyVerse(): Promise<Verse> {
  try {
    return await getJson<Verse>("/api/daily");
  } catch (err) {
    console.error("getDailyVerse failed, falling back to local:", err);
    return getVerseOfDay();
  }
}
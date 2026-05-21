/**
 * Frontend API Client for Anantha Library.
 * 
 * This module provides functions to communicate with the Flask backend.
 * It follows a 'Graceful Degradation' pattern: if the backend API is
 * unavailable, it falls back to local data processing to ensure the
 * app remains functional.
 */
import type { Verse } from "./verses";
import { ALL_VERSES, getVerseOfDay, searchVerses } from "./verses";

export type ChatApiResponse = {
  content: string;
  citations: Verse[];
};

export type SearchApiResponse = {
  results: Verse[];
};

/**
 * Helper for making POST requests with JSON bodies.
 */
async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

/**
 * Helper for making GET requests.
 */
async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path, { method: "GET" });
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

/**
 * Searches for verses using the backend's semantic search.
 * Falls back to local keyword search if the backend is down.
 */
export async function searchApi(query: string): Promise<Verse[]> {
  try {
    const data = await postJson<SearchApiResponse | Verse[]>("/api/search", { query });
    if (Array.isArray(data)) return data;
    return data.results ?? [];
  } catch (err) {
    console.error("searchApi failed, falling back to local:", err);
    // Local fallback ensures user can still search even without a running backend
    return searchVerses(query);
  }
}

/**
 * Sends a prompt to the RAG chat endpoint.
 * On failure, it provides a thoughtful fallback response and random citations
 * to simulate the chat experience.
 */
export async function chatApi(
  prompt: string,
  context?: { verseId?: string },
): Promise<ChatApiResponse> {
  try {
    return await postJson<ChatApiResponse>("/api/chat", { prompt, context });
  } catch (err) {
    console.error("chatApi failed, falling back to local:", err);
    // Mocking the RAG response for offline mode
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

/**
 * Fetches the 'Verse of the Day' from the backend.
 * Falls back to a deterministic local selection based on the current date.
 */
export async function getDailyVerse(): Promise<Verse> {
  try {
    const data = await getJson<Verse | { verse: Verse }>("/api/daily");
    if ("verse" in data && typeof data.verse === "object") {
      return data.verse as Verse;
    }
    return data as Verse;
  } catch (err) {
    console.error("getDailyVerse failed, falling back to local:", err);
    return getVerseOfDay();
  }
}
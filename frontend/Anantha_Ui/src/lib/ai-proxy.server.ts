/**
 * Server-side AI Proxy
 * 
 * This module acts as a middleware between the frontend client and the Python backend.
 * Why use a proxy?
 * 1. Security: Hides the backend URL from the client browser.
 * 2. CORS Handling: Prevents Cross-Origin Resource Sharing issues during development.
 * 3. Timeout Control: Enforces strict timeouts (10s) to prevent hanging UI states if the LLM is slow.
 * 4. Offline Mocking: Provides fallback responses if the backend service URL is not configured.
 */
import { ALL_VERSES, getVerseOfDay, searchVerses, type Verse } from "./verses";

const TIMEOUT_MS = 10_000;

// Predefined thoughtful responses used when the backend is unreachable
const FALLBACK_REPLIES = [
  "The Gita reminds us that peace is found not in changing the world, but in steadying the mind. Act with devotion, release the fruits, and let stillness become your foundation.",
  "Krishna teaches Arjuna that the self is eternal — untouched by sorrow, fire, or time. When you remember this, fear softens and clarity returns.",
  "Equanimity in success and failure is the heart of yoga. Begin small: notice when you grasp at outcomes, and gently return to the present action.",
];

/**
 * Resolves the backend service URL from environment variables.
 * Supports both Node (process.env) and Vite (import.meta.env) contexts.
 */
function getServiceUrl(): string | null {
  const url = process.env.AI_SERVICE_URL || (import.meta as any).env?.VITE_AI_SERVICE_URL;
  console.log("[PROXY] getServiceUrl resolved to:", url);
  if (!url || url.trim().length === 0) return null;
  return url.replace(/\/+$/, "");
}

/**
 * Proxies a request to the configured backend URL.
 * Automatically aborts the request if it exceeds TIMEOUT_MS.
 */
export async function proxy(
  pathname: string,
  init: RequestInit,
): Promise<Response | null> {
  const base = getServiceUrl();
  if (!base) {
    console.log("[PROXY] No base URL, falling back to mock");
    return null;
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const target = `${base}${pathname}`;
    console.log(`[PROXY] Fetching: ${target}`);
    // Forward the request to the Python backend
    const res = await fetch(target, { ...init, signal: controller.signal });
    console.log(`[PROXY] Response from ${target}: ${res.status}`);
    return res;
  } catch (err) {
    console.error(`[PROXY] Failed ${pathname}:`, err);
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

// --- Mocking Functions for Offline/Fallback Mode ---

export function mockSearch(query: string): { results: Verse[] } {
  return { results: searchVerses(query ?? "") };
}

export function mockChat(_prompt: string): { content: string; citations: Verse[] } {
  // Select 3 random verses to act as 'citations' for the mock response
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

/**
 * Utility to wrap JSON data in a standard HTTP Response object.
 */
export function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
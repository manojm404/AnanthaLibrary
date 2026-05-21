/**
 * Verse Data Model and Local Utilities
 * 
 * This module defines the structure of a Bhagavad Gita verse and provides
 * local search and retrieval functions. These functions serve as a fallback
 * mechanism ensuring the app works entirely offline if necessary.
 */
import data from "@/data/verses.json";

export type Verse = {
  id: string;              // Unique identifier (e.g., "gita:1:1")
  chapter: number | string; // Chapter number
  verse: number | string;   // Verse number within the chapter
  sanskrit: string;        // Original Sanskrit text
  translation: string;     // English translation
  hindi?: string;          // Optional Hindi translation
  transliteration?: string;// Optional romanized Sanskrit
  text?: string;           // Combined text used primarily for backend indexing
};

// The complete, locally bundled dataset of all verses
export const ALL_VERSES: Verse[] = data as Verse[];

/**
 * Performs a basic, case-insensitive keyword search across the local dataset.
 * This is used when the semantic search backend (ChromaDB) is unreachable.
 * 
 * It checks translations, sanskrit, hindi, and chapter:verse references.
 */
export function searchVerses(query: string): Verse[] {
  const q = query.trim().toLowerCase();
  if (!q) return ALL_VERSES;
  return ALL_VERSES.filter((v) => {
    return (
      (v.translation || "").toLowerCase().includes(q) ||
      (v.sanskrit || "").toLowerCase().includes(q) ||
      (v.hindi || "").toLowerCase().includes(q) ||
      `${v.chapter}:${v.verse}`.includes(q) ||
      `${v.chapter}.${v.verse}`.includes(q) ||
      v.id.includes(q)
    );
  });
}

/**
 * Retrieves a pseudo-random verse based on the current date.
 * Ensures all users see the same 'Verse of the Day' on a given day.
 */
export function getVerseOfDay(): Verse {
  const day = Math.floor(Date.now() / 86_400_000); // Days since epoch
  return ALL_VERSES[day % ALL_VERSES.length];
}

/**
 * Utility to format the chapter and verse numbers into a readable reference (e.g., "2:47").
 */
export function getReference(v: Pick<Verse, "chapter" | "verse">) {
  return `${v.chapter}:${v.verse}`;
}
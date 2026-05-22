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
  chapter: number | string; // Chapter or Section identifier
  verse: number | string;   // Verse or Sentence identifier
  sanskrit: string;        // Original primary text (e.g., Sanskrit)
  translation: string;     // English translation
  hindi?: string;          // Optional Hindi translation
  transliteration?: string;// Optional transliteration
  text?: string;           // Combined text block
  audio_url?: string;      // URL to audio clip
  book_id?: string;        // ID of the book (e.g., "gita")
  book_title?: string;     // Title of the book
};

export type Book = {
  id: string;
  title: string;
};

// The complete, locally bundled dataset of all verses
export const ALL_VERSES: Verse[] = data as Verse[];

/**
 * Performs a basic, case-insensitive keyword search across the local dataset.
 * This is used when the semantic search backend (ChromaDB) is unreachable.
 */
export function searchVerses(query: string, book_id?: string): Verse[] {
  const q = query.trim().toLowerCase();
  
  // Filter by book if specified
  const pool = book_id 
    ? ALL_VERSES.filter(v => v.book_id === book_id)
    : ALL_VERSES;

  if (!q) return pool;
  
  return pool.filter((v) => {
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
 * Retrieves a pseudo-random verse based on the current date and active book.
 */
export function getVerseOfDay(book_id?: string): Verse {
  const day = Math.floor(Date.now() / 86_400_000); 
  const pool = book_id 
    ? ALL_VERSES.filter(v => v.book_id === book_id)
    : ALL_VERSES;
    
  if (pool.length === 0) return ALL_VERSES[day % ALL_VERSES.length];
  return pool[day % pool.length];
}

/**
 * Utility to format the chapter and verse numbers into a readable reference (e.g., "2:47").
 */
export function getReference(v: Pick<Verse, "chapter" | "verse">) {
  return `${v.chapter}:${v.verse}`;
}
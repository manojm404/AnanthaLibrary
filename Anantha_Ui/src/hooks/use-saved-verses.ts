import { useCallback, useEffect, useState } from "react";
import { storage, type SavedVerse } from "@/lib/storage";
import type { Verse } from "@/lib/verses";

export function useSavedVerses() {
  const [verses, setVerses] = useState<SavedVerse[]>([]);

  useEffect(() => {
    setVerses(storage.getSavedVerses());
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.key === storage.KEYS.saved) {
        setVerses(storage.getSavedVerses());
      }
    };
    window.addEventListener("anantha-storage", handler);
    return () => window.removeEventListener("anantha-storage", handler);
  }, []);

  const isSaved = useCallback(
    (id: string) => verses.some((v) => v.id === id),
    [verses],
  );

  const toggle = useCallback((verse: Verse) => {
    const current = storage.getSavedVerses();
    const exists = current.some((v) => v.id === verse.id);
    const next = exists
      ? current.filter((v) => v.id !== verse.id)
      : [
          {
            id: verse.id,
            chapter: verse.chapter,
            verse: verse.verse,
            sanskrit: verse.sanskrit,
            translation: verse.translation,
            savedAt: new Date().toISOString(),
          },
          ...current,
        ];
    storage.setSavedVerses(next);
    setVerses(next);
    return !exists;
  }, []);

  const remove = useCallback((id: string) => {
    const next = storage.getSavedVerses().filter((v) => v.id !== id);
    storage.setSavedVerses(next);
    setVerses(next);
  }, []);

  return { verses, isSaved, toggle, remove };
}
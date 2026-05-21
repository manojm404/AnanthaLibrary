import data from "@/data/verses.json";

export type Verse = {
  id: string;
  chapter: number;
  verse: number;
  sanskrit: string;
  translation: string;
};

export const ALL_VERSES: Verse[] = data as Verse[];

export function searchVerses(query: string): Verse[] {
  const q = query.trim().toLowerCase();
  if (!q) return ALL_VERSES;
  return ALL_VERSES.filter((v) => {
    return (
      v.translation.toLowerCase().includes(q) ||
      v.sanskrit.includes(query) ||
      `${v.chapter}:${v.verse}`.includes(q) ||
      `${v.chapter}.${v.verse}`.includes(q) ||
      v.id.includes(q)
    );
  });
}

export function getVerseOfDay(): Verse {
  const day = Math.floor(Date.now() / 86_400_000);
  return ALL_VERSES[day % ALL_VERSES.length];
}

export function getReference(v: Pick<Verse, "chapter" | "verse">) {
  return `${v.chapter}:${v.verse}`;
}
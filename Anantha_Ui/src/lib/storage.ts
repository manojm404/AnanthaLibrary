export type SavedVerse = {
  id: string;
  chapter: number;
  verse: number;
  sanskrit: string;
  translation: string;
  savedAt: string;
};

const KEYS = {
  saved: "anantha_saved_verses",
  journal: "anantha_journal_entries",
  streak: "anantha_streak",
  streakDate: "anantha_streak_last_date",
  theme: "anantha_theme",
} as const;

const isBrowser = () => typeof window !== "undefined";

function read<T>(key: string, fallback: T): T {
  if (!isBrowser()) return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function write<T>(key: string, value: T) {
  if (!isBrowser()) return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
    window.dispatchEvent(new CustomEvent("anantha-storage", { detail: { key } }));
  } catch {
    // ignore quota
  }
}

export const storage = {
  KEYS,
  getSavedVerses: () => read<SavedVerse[]>(KEYS.saved, []),
  setSavedVerses: (v: SavedVerse[]) => write(KEYS.saved, v),
  getJournal: () => read<Record<string, string>>(KEYS.journal, {}),
  setJournal: (v: Record<string, string>) => write(KEYS.journal, v),
  getStreak: () => read<number>(KEYS.streak, 0),
  setStreak: (v: number) => write(KEYS.streak, v),
  getStreakDate: () => read<string | null>(KEYS.streakDate, null),
  setStreakDate: (v: string) => write(KEYS.streakDate, v),
  getTheme: () => read<"dark" | "light" | null>(KEYS.theme, null),
  setTheme: (v: "dark" | "light") => write(KEYS.theme, v),
};
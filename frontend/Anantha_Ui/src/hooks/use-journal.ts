import { useEffect, useRef, useState } from "react";
import { storage } from "@/lib/storage";

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

export function useJournal() {
  const key = todayKey();
  const [text, setText] = useState("");
  const initialized = useRef(false);

  useEffect(() => {
    const all = storage.getJournal();
    setText(all[key] ?? "");
    initialized.current = true;
  }, [key]);

  useEffect(() => {
    if (!initialized.current) return;
    const id = setTimeout(() => {
      const all = storage.getJournal();
      storage.setJournal({ ...all, [key]: text });
    }, 400);
    return () => clearTimeout(id);
  }, [text, key]);

  return { text, setText, dateKey: key };
}

export function useStreak() {
  const [streak, setStreak] = useState(0);
  const [appliedToday, setAppliedToday] = useState(false);

  useEffect(() => {
    setStreak(storage.getStreak());
    setAppliedToday(storage.getStreakDate() === todayKey());
  }, []);

  const apply = () => {
    const today = todayKey();
    const last = storage.getStreakDate();
    if (last === today) return;
    const yesterday = new Date(Date.now() - 86_400_000).toISOString().slice(0, 10);
    const current = storage.getStreak();
    const next = last === yesterday ? current + 1 : 1;
    storage.setStreak(next);
    storage.setStreakDate(today);
    setStreak(next);
    setAppliedToday(true);
  };

  return { streak, appliedToday, apply };
}
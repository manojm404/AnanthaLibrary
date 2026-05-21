import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Flame, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { getVerseOfDay, getReference, type Verse } from "@/lib/verses";
import { getDailyVerse } from "@/lib/api";
import { useJournal, useStreak } from "@/hooks/use-journal";
import { SaveHeartButton } from "@/components/SaveHeartButton";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/wisdom")({
  head: () => ({
    meta: [
      { title: "Today's Wisdom — Anantha" },
      { name: "description", content: "A verse, a reflection, and a practice for today." },
    ],
  }),
  component: WisdomPage,
});

function WisdomPage() {
  const [verse, setVerse] = useState<Verse>(() => getVerseOfDay());
  useEffect(() => {
    getDailyVerse().then(setVerse).catch(() => {});
  }, []);
  const { text, setText } = useJournal();
  const { streak, appliedToday, apply } = useStreak();
  const dateLabel = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="mx-auto max-w-3xl px-4 md:px-8 py-10 space-y-6">
      <section className="glass rounded-2xl p-6 md:p-8 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Today</p>
          <h1
            style={{ fontFamily: "var(--font-display)" }}
            className="mt-1 text-2xl md:text-3xl font-semibold"
          >
            {dateLabel}
          </h1>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1.5 text-sm text-primary">
          <Flame className="h-4 w-4" />
          <span className="font-semibold">{streak}</span>
          <span className="text-xs text-primary/80">day streak</span>
        </div>
      </section>

      <section className="glass rounded-2xl p-6 md:p-8 space-y-4">
        <div className="flex items-center justify-between">
          <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-medium text-primary">
            Ch {getReference(verse)}
          </span>
          <SaveHeartButton verse={verse} />
        </div>
        <p className="sanskrit text-lg leading-loose">{verse.sanskrit}</p>
        <p className="text-foreground/90 leading-relaxed">{verse.translation}</p>
      </section>

      <section className="glass rounded-2xl p-6 md:p-8 space-y-3">
        <h2 style={{ fontFamily: "var(--font-display)" }} className="text-xl font-semibold">
          Reflection
        </h2>
        <p className="text-muted-foreground leading-relaxed">
          Where in your life today are you holding onto an outcome? Notice the grasp without
          judgment, and let the act itself be enough.
        </p>
      </section>

      <section className="glass rounded-2xl p-6 md:p-8 space-y-3">
        <h2 style={{ fontFamily: "var(--font-display)" }} className="text-xl font-semibold">
          Practice
        </h2>
        <p className="text-muted-foreground leading-relaxed">
          Before your next task, pause for three breaths. Offer the work — not its result —
          as your contribution.
        </p>
      </section>

      <section className="glass rounded-2xl p-6 md:p-8 space-y-3">
        <h2 style={{ fontFamily: "var(--font-display)" }} className="text-xl font-semibold">
          Journal
        </h2>
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="What did this verse stir in you today?"
          aria-label="Journal entry"
          className="min-h-[140px] rounded-xl bg-background/40"
        />
        <p className="text-xs text-muted-foreground">Saved automatically.</p>
      </section>

      <Button
        size="lg"
        onClick={apply}
        disabled={appliedToday}
        className={cn(
          "w-full rounded-xl h-12 text-base shadow-[0_0_24px_-6px_var(--primary)]",
          appliedToday
            ? "bg-[var(--success)] text-[var(--success-foreground)] hover:bg-[var(--success)]"
            : "bg-primary text-primary-foreground hover:bg-primary/90",
        )}
      >
        {appliedToday ? (
          <>
            <Check className="h-4 w-4 mr-2" />
            Applied today — see you tomorrow
          </>
        ) : (
          "I applied this today"
        )}
      </Button>
    </div>
  );
}
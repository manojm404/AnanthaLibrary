import { useEffect, useState } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { ArrowRight, BookOpen, Search as SearchIcon, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { VerseCard } from "@/components/VerseCard";
import { getVerseOfDay, type Verse } from "@/lib/verses";
import { getDailyVerse } from "@/lib/api";

export const Route = createFileRoute("/app")({
  head: () => ({
    meta: [
      { title: "Home — Anantha Library" },
      { name: "description", content: "Your daily companion to the Bhagavad Gita." },
    ],
  }),
  component: AppHome,
});

function AppHome() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [verse, setVerse] = useState<Verse>(() => getVerseOfDay());

  useEffect(() => {
    getDailyVerse().then(setVerse).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-5xl px-4 md:px-8 py-10 md:py-16 space-y-16">
      <section className="text-center space-y-6 pt-6 md:pt-12">
        <p className="inline-flex items-center gap-2 rounded-full glass px-3 py-1 text-xs text-muted-foreground">
          <Sparkles className="h-3 w-3 text-primary" />
          {t("home.hero_pill")}
        </p>
        <h1
          style={{ fontFamily: "var(--font-display)" }}
          className="text-4xl md:text-6xl font-semibold tracking-tight leading-[1.05]"
        >
          {t("home.hero_title")} <br className="hidden md:block" />
          <span className="text-gradient-amber">{t("home.hero_title_accent")}</span>
        </h1>
        <p className="mx-auto max-w-xl text-muted-foreground leading-relaxed">
          {t("home.hero_subtitle")}
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            navigate({ to: "/search", search: { q } });
          }}
          className="mx-auto mt-8 max-w-xl"
        >
          <div className="relative glass rounded-2xl p-1.5 flex items-center gap-2 focus-within:ring-2 focus-within:ring-primary/40 transition">
            <SearchIcon className="ml-3 h-5 w-5 text-muted-foreground" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder={t("home.search_placeholder")}
              aria-label={t("home.search_placeholder")}
              className="border-0 bg-transparent focus-visible:ring-0 shadow-none text-base h-12"
            />
            <Button
              type="submit"
              size="sm"
              className="rounded-xl h-10 bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {t("home.search_button")}
              <ArrowRight className="ml-1.5 h-4 w-4" />
            </Button>
          </div>
        </form>
      </section>

      <section aria-labelledby="vod">
        <div className="flex items-end justify-between mb-4">
          <h2
            id="vod"
            style={{ fontFamily: "var(--font-display)" }}
            className="text-2xl font-semibold"
          >
            {t("home.verse_of_day")}
          </h2>
          <Link to="/wisdom" className="text-sm text-primary hover:underline">
            {t("home.todays_wisdom")}
          </Link>
        </div>
        <VerseCard verse={verse} truncate={false} />
      </section>

      <section aria-labelledby="how" className="space-y-6">
        <h2
          id="how"
          style={{ fontFamily: "var(--font-display)" }}
          className="text-2xl font-semibold text-center"
        >
          {t("home.how_title")}
        </h2>
        <ol className="grid gap-4 md:grid-cols-3">
          {[
            { icon: SearchIcon, title: t("home.step_search_title"), body: t("home.step_search_body") },
            { icon: BookOpen, title: t("home.step_save_title"), body: t("home.step_save_body") },
            { icon: Sparkles, title: t("home.step_reflect_title"), body: t("home.step_reflect_body") },
          ].map((step, i) => (
            <li
              key={i}
              className="glass rounded-2xl p-6 space-y-3 hover:scale-[1.02] transition-transform"
            >
              <div className="flex items-center gap-3">
                <span className="grid place-items-center h-8 w-8 rounded-full bg-primary/15 text-primary text-sm font-semibold">
                  {i + 1}
                </span>
                <step.icon className="h-4 w-4 text-primary" />
              </div>
              <h3 style={{ fontFamily: "var(--font-display)" }} className="text-lg font-semibold">
                {step.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
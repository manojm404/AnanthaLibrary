import { createFileRoute, Link } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { ArrowRight, BookOpen, MessageCircle, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { Logo } from "@/components/Logo";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Anantha Library — Spiritual Companion" },
      {
        name: "description",
        content:
          "Search, save, and reflect on the Bhagavad Gita. A quiet, modern companion for daily wisdom.",
      },
    ],
  }),
  component: Landing,
});

function Landing() {
  const { t } = useTranslation();

  const features = [
    {
      icon: Search,
      title: t("landing.feature_search_title", "Search the Gita"),
      body: t(
        "landing.feature_search_body",
        "Find verses by theme, keyword, or chapter in seconds.",
      ),
    },
    {
      icon: MessageCircle,
      title: t("landing.feature_chat_title", "Chat with Anantha"),
      body: t(
        "landing.feature_chat_body",
        "Ask questions and receive grounded, contemplative answers.",
      ),
    },
    {
      icon: BookOpen,
      title: t("landing.feature_save_title", "Save & Reflect"),
      body: t(
        "landing.feature_save_body",
        "Bookmark verses, journal insights, and build a daily practice.",
      ),
    },
  ];

  return (
    <div className="min-h-dvh aurora-bg">
      <header className="flex items-center justify-between px-6 md:px-10 h-16">
        <Logo />
        <LanguageSwitcher />
      </header>

      <main className="mx-auto max-w-5xl px-4 md:px-8 py-12 md:py-20">
        <section className="text-center space-y-6">
          <p className="inline-flex items-center gap-2 rounded-full glass px-3 py-1 text-xs text-muted-foreground">
            <Sparkles className="h-3 w-3 text-primary" />
            {t("landing.pill", "Bhagavad Gita, reimagined")}
          </p>
          <h1
            style={{ fontFamily: "var(--font-display)" }}
            className="text-5xl md:text-7xl font-semibold tracking-tight leading-[1.05]"
          >
            {t("landing.title", "Anantha Library")}
          </h1>
          <p className="mx-auto max-w-xl text-lg text-muted-foreground leading-relaxed">
            {t(
              "landing.subtitle",
              "A quiet, modern companion for daily reflection on timeless wisdom.",
            )}
          </p>
          <div className="pt-4">
            <Button
              asChild
              size="lg"
              className="rounded-xl bg-primary text-primary-foreground hover:bg-primary/90"
            >
              <Link to="/app">
                {t("landing.cta", "Enter Library")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </section>

        <section className="mt-20 grid gap-4 md:grid-cols-3">
          {features.map((f, i) => (
            <div
              key={i}
              className="glass rounded-2xl p-6 space-y-3 hover:scale-[1.02] transition-transform"
            >
              <f.icon className="h-5 w-5 text-primary" />
              <h3
                style={{ fontFamily: "var(--font-display)" }}
                className="text-lg font-semibold"
              >
                {f.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.body}</p>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}
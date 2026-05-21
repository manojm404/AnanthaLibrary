import { createFileRoute, Link } from "@tanstack/react-router";
import { BookHeart } from "lucide-react";
import { VerseCard } from "@/components/VerseCard";
import { useSavedVerses } from "@/hooks/use-saved-verses";

export const Route = createFileRoute("/library")({
  head: () => ({
    meta: [
      { title: "Library — Anantha" },
      { name: "description", content: "Your saved verses from the Bhagavad Gita." },
    ],
  }),
  component: LibraryPage,
});

function LibraryPage() {
  const { verses, remove } = useSavedVerses();

  return (
    <div className="mx-auto max-w-6xl px-4 md:px-8 py-10 space-y-6">
      <header className="space-y-2">
        <h1 style={{ fontFamily: "var(--font-display)" }} className="text-3xl md:text-4xl font-semibold">
          Your Library
        </h1>
        <p className="text-muted-foreground text-sm">
          {verses.length} saved {verses.length === 1 ? "verse" : "verses"}
        </p>
      </header>

      {verses.length === 0 ? (
        <div className="glass rounded-2xl p-12 text-center space-y-4">
          <BookHeart className="mx-auto h-10 w-10 text-primary opacity-70" />
          <p className="text-muted-foreground">
            Your library is empty. Save verses that move you from{" "}
            <Link to="/search" className="text-primary hover:underline">Search</Link>.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {verses.map((v) => (
            <VerseCard
              key={v.id}
              verse={v}
              showSave={false}
              onRemove={() => remove(v.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
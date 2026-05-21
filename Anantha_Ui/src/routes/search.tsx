import { useEffect, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { zodValidator, fallback } from "@tanstack/zod-adapter";
import { z } from "zod";
import { Search as SearchIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { VerseCard } from "@/components/VerseCard";
import { searchApi } from "@/lib/api";
import type { Verse } from "@/lib/verses";

const searchSchema = z.object({
  q: fallback(z.string(), "").default(""),
});

export const Route = createFileRoute("/search")({
  validateSearch: zodValidator(searchSchema),
  head: () => ({
    meta: [
      { title: "Search — Anantha Library" },
      { name: "description", content: "Search verses of the Bhagavad Gita by theme or reference." },
    ],
  }),
  component: SearchPage,
});

function SearchPage() {
  const { q } = Route.useSearch();
  const navigate = useNavigate({ from: "/search" });
  const [query, setQuery] = useState(q);
  const [results, setResults] = useState<Verse[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    searchApi(q).then((r) => {
      if (!cancelled) {
        setResults(r);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [q]);

  return (
    <div className="mx-auto max-w-6xl px-4 md:px-8 py-6 md:py-10 space-y-6">
      <div className="sticky top-14 md:top-0 z-20 -mx-4 md:-mx-8 px-4 md:px-8 py-3 glass border-b">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            navigate({ search: { q: query } });
          }}
          className="relative"
        >
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search verses, themes, references…"
            aria-label="Search verses"
            className="pl-9 h-11 rounded-xl"
            autoFocus
          />
        </form>
      </div>

      <p className="text-sm text-muted-foreground">
        {loading ? "Searching…" : `${results.length} ${results.length === 1 ? "verse" : "verses"}`}
        {q && !loading && <> matching "<span className="text-foreground">{q}</span>"</>}
      </p>

      {!loading && results.length === 0 ? (
        <div className="glass rounded-2xl p-10 text-center text-muted-foreground">
          No verses found. Try a different theme or feeling.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((v) => (
            <VerseCard key={v.id} verse={v} />
          ))}
        </div>
      )}
    </div>
  );
}
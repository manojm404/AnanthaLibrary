# Anantha Library — Spiritual Companion

UI-only MVP on TanStack Start (this project's stack — Next.js can't run here). All features from the brief map 1:1; the only adaptations are framework-level (file-based routes in `src/routes/*`, `@tanstack/react-router` links, custom `ThemeProvider` instead of `next-themes`, Tailwind v4 tokens in `src/styles.css`).

## Pages (`src/routes/`)

1. `index.tsx` → `/` — Hero, large search bar (submits to `/search?q=…`), Verse of the Day card, 3-step "How it works"
2. `search.tsx` → `/search` — Sticky search, results grid (2 cols mobile / 3 desktop), each card: Ch:Verse, truncated Sanskrit + translation, heart (save), "Ask Anantha" → chat modal pre-populated with verse context. Reads `?q=` via `Route.useSearch` with Zod schema; filters mock verses client-side.
3. `chat.tsx` → `/chat` — Full-height message list, sticky bottom input, "Anantha is meditating…" typing indicator, each AI message has Sources button → citations drawer. Mock streamed responses with fake citations.
4. `library.tsx` → `/library` — Grid of saved verses from `localStorage`, each with Remove. Empty state.
5. `wisdom.tsx` → `/wisdom` — Date hero, verse card, Reflection, Practice, Journal textarea (debounced save to `localStorage`), "I applied this today" button increments streak.

## Global chrome

- `src/routes/__root.tsx` — wraps everything in `ThemeProvider` + `QueryClientProvider`, renders responsive layout: desktop collapsible left sidebar, mobile header + bottom nav, `<main>` with `<Outlet />` and page-transition wrapper.
- `src/components/AppSidebar.tsx` — shadcn sidebar variant: logo, nav items (Home/Search/Chat/Library/Wisdom), theme toggle at bottom, collapsible to icon strip.
- `src/components/MobileHeader.tsx` — logo + theme toggle.
- `src/components/BottomNav.tsx` — fixed bottom bar with 5 icons, active state via `Link` `activeProps`, hidden on `md:` and up.
- `src/components/ThemeToggle.tsx` — sun/moon, toggles `class="dark"` on `<html>`, persists to `localStorage` (`anantha_theme`).
- `src/components/PageTransition.tsx` — fade + slide wrapper using CSS keyframes (respects `prefers-reduced-motion`).

## Modals & drawers

- `src/components/ChatModal.tsx` — shadcn `Dialog`, smaller chat surface, accepts `verseContext` prop, reuses chat message components.
- `src/components/CitationsDrawer.tsx` — shadcn `Sheet` (right), expandable Sanskrit per cited verse.
- `src/components/VerseCard.tsx` — shared card used in Search, Library, Wisdom, and as citation row.
- `src/components/SaveHeartButton.tsx` — pop animation on save (scale keyframe), emerald flash on confirm, syncs to `localStorage`.

## Mock data + utilities

- `src/data/verses.json` — 15 Bhagavad Gita verses `{ id, chapter, verse, sanskrit, translation }`.
- `src/lib/storage.ts` — typed get/set helpers for `anantha_saved_verses`, `anantha_journal_entries`, `anantha_streak`, `anantha_theme`. SSR-safe (guards `typeof window`).
- `src/lib/search.ts` — client-side text matcher across sanskrit + translation + reference.
- `src/lib/mock-chat.ts` — generates fake assistant replies + 2–3 citations sampled from `verses.json`, with artificial delay for typing indicator.
- `src/hooks/use-saved-verses.ts`, `src/hooks/use-journal.ts`, `src/hooks/use-streak.ts` — small state hooks wrapping storage.

## Design system (`src/styles.css`)

Replace existing tokens with the brief's palette, expressed in `oklch` for both light and dark, plus extra semantic tokens for glass surfaces.

Dark (default):
- `--background` ≈ `#0B0E14`, `--foreground` ≈ `#E8EDF2`, `--muted-foreground` ≈ `#8A95A5`
- `--primary` = Golden Amber `#D4AF37`, `--success` = Emerald `#10B981`
- `--glass-bg` = `rgba(18,22,30,0.7)`, `--glass-border` = `rgba(255,255,255,0.1)`, `--glass-blur: 12px`

Light:
- `--background` ≈ `#F9F7F4`, `--foreground` ≈ `#1E293B`, `--primary` = `#B8860B`

Add a `.glass` utility class (background + backdrop-blur + border) and keyframes: `fade-in`, `slide-up`, `pop`, `pulse-soft`, all gated by `@media (prefers-reduced-motion: reduce)`.

Fonts: load Playfair Display, Inter, Noto Serif Devanagari via `<link>` in `__root.tsx` `head()`. Register as `--font-display`, `--font-sans`, `--font-devanagari` in the `@theme` block; apply Devanagari class to `.sanskrit` spans.

## shadcn components used

Button, Card, Input, Textarea, Dialog, Sheet (drawer), Tabs, Skeleton, Sonner (toast), Sidebar, Tooltip. Add any missing via the standard component path under `src/components/ui/`.

## Accessibility

- One `<main>` per page inside `__root.tsx` outlet wrapper.
- `aria-label` on every icon-only button (theme toggle, heart, nav icons, sources).
- Focus-visible ring tokens via Tailwind `ring-ring`.
- Color contrast verified against brief palette (amber on dark bg + foreground combos meet AA).
- Keyboard: chat input submits on Enter, Shift+Enter newline; modal/drawer use Radix focus trap.

## Routing details

- Add `defaultPreload: "intent"` to router for snappy nav.
- `search.tsx` declares Zod `validateSearch` for `{ q?: string }`.
- Every route sets its own `head()` with title + description + og tags (no og:image at root).

## Out of scope (per brief)

No real backend, no auth, no Lovable Cloud. Chat + search are mock; localStorage is the only persistence. Easy to swap to server functions later.

## File checklist

```text
src/
  routes/
    __root.tsx            (rewrite: providers, layout, fonts, nav)
    index.tsx             (rewrite: real home)
    search.tsx            (new)
    chat.tsx              (new)
    library.tsx           (new)
    wisdom.tsx            (new)
  components/
    AppSidebar.tsx
    MobileHeader.tsx
    BottomNav.tsx
    ThemeToggle.tsx
    ThemeProvider.tsx
    PageTransition.tsx
    VerseCard.tsx
    SaveHeartButton.tsx
    ChatModal.tsx
    ChatSurface.tsx       (shared by /chat + ChatModal)
    CitationsDrawer.tsx
    VerseOfDay.tsx
    HowItWorks.tsx
  data/verses.json
  lib/storage.ts
  lib/search.ts
  lib/mock-chat.ts
  hooks/use-saved-verses.ts
  hooks/use-journal.ts
  hooks/use-streak.ts
  styles.css              (rewrite tokens + utilities + keyframes)
```

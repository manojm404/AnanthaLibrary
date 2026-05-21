import { Link } from "@tanstack/react-router";

export function Logo({ collapsed = false }: { collapsed?: boolean }) {
  return (
    <Link
      to="/"
      className="flex items-center gap-2 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md"
      aria-label="Anantha Library home"
    >
      <span
        aria-hidden
        className="relative grid place-items-center h-9 w-9 rounded-full bg-gradient-to-br from-primary to-primary/60 text-primary-foreground shadow-[0_0_24px_-4px_var(--primary)] transition-transform group-hover:scale-105"
      >
        <span className="text-base font-bold leading-none" style={{ fontFamily: "var(--font-display)" }}>अ</span>
      </span>
      {!collapsed && (
        <span className="flex flex-col leading-tight">
          <span className="text-base font-semibold tracking-tight" style={{ fontFamily: "var(--font-display)" }}>Anantha</span>
          <span className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
            Library
          </span>
        </span>
      )}
    </Link>
  );
}
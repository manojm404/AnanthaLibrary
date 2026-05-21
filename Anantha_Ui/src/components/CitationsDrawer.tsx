import { useState } from "react";
import { ChevronDown } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { Verse } from "@/lib/verses";
import { getReference } from "@/lib/verses";
import { cn } from "@/lib/utils";

export function CitationsDrawer({
  open,
  onOpenChange,
  citations,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  citations: Verse[];
}) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader>
          <SheetTitle style={{ fontFamily: "var(--font-display)" }}>Cited Verses</SheetTitle>
          <SheetDescription>Sources Anantha drew from for this response.</SheetDescription>
        </SheetHeader>
        <ul className="mt-6 space-y-3 px-4 pb-6">
          {citations.map((v) => (
            <CitationItem key={v.id} verse={v} />
          ))}
        </ul>
      </SheetContent>
    </Sheet>
  );
}

function CitationItem({ verse }: { verse: Verse }) {
  const [open, setOpen] = useState(false);
  return (
    <li className="rounded-xl border bg-card/40 overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="w-full text-left p-4 flex items-start gap-3 hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <span className="shrink-0 inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-medium text-primary">
          {getReference(verse)}
        </span>
        <span className="flex-1 text-sm text-foreground/90 line-clamp-2">{verse.translation}</span>
        <ChevronDown
          className={cn(
            "h-4 w-4 mt-1 text-muted-foreground transition-transform shrink-0",
            open && "rotate-180",
          )}
        />
      </button>
      {open && (
        <div className="px-4 pb-4 -mt-1 space-y-2 animate-anantha-fade-in">
          <p className="sanskrit text-sm leading-loose text-foreground">{verse.sanskrit}</p>
          <p className="text-sm text-muted-foreground leading-relaxed">{verse.translation}</p>
        </div>
      )}
    </li>
  );
}
import { useState } from "react";
import { Sparkles, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Verse } from "@/lib/verses";
import { getReference } from "@/lib/verses";
import { SaveHeartButton } from "./SaveHeartButton";
import { ChatModal } from "./ChatModal";

type Props = {
  verse: Verse;
  truncate?: boolean;
  showAsk?: boolean;
  showSave?: boolean;
  onRemove?: () => void;
  className?: string;
};

export function VerseCard({
  verse,
  truncate = true,
  showAsk = true,
  showSave = true,
  onRemove,
  className,
}: Props) {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <article
      className={cn(
        "glass rounded-2xl p-5 flex flex-col gap-3 transition-transform duration-200 hover:scale-[1.02] hover:border-primary/30",
        className,
      )}
    >
      <header className="flex items-start justify-between gap-2">
        <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-medium text-primary tracking-wide">
          Ch {getReference(verse)}
        </span>
        <div className="flex items-center -mr-2">
          {showSave && <SaveHeartButton verse={verse} />}
          {onRemove && (
            <Button variant="ghost" size="icon" aria-label="Remove from library" onClick={onRemove}>
              <Trash2 className="h-[1.05rem] w-[1.05rem] text-muted-foreground" />
            </Button>
          )}
        </div>
      </header>

      <p className={cn("sanskrit text-[15px] text-foreground/90", truncate && "line-clamp-2")}>
        {verse.sanskrit}
      </p>

      <p
        className={cn(
          "text-sm text-muted-foreground leading-relaxed",
          truncate && "line-clamp-3",
        )}
      >
        {verse.translation}
      </p>

      {showAsk && (
        <div className="pt-1 mt-auto">
          <Button
            variant="ghost"
            size="sm"
            className="text-primary hover:bg-primary/10 -ml-2"
            onClick={() => setChatOpen(true)}
          >
            <Sparkles className="h-3.5 w-3.5 mr-1.5" />
            Ask Anantha
          </Button>
          <ChatModal open={chatOpen} onOpenChange={setChatOpen} verseContext={verse} />
        </div>
      )}
    </article>
  );
}
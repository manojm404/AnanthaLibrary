import { useState } from "react";
import { Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useSavedVerses } from "@/hooks/use-saved-verses";
import type { Verse } from "@/lib/verses";
import { toast } from "sonner";

export function SaveHeartButton({ verse, className }: { verse: Verse; className?: string }) {
  const { isSaved, toggle } = useSavedVerses();
  const saved = isSaved(verse.id);
  const [popping, setPopping] = useState(false);

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={saved ? "Remove from library" : "Save to library"}
      aria-pressed={saved}
      className={cn("relative", className)}
      onClick={() => {
        const added = toggle(verse);
        setPopping(true);
        setTimeout(() => setPopping(false), 450);
        toast.success(added ? "Saved to your library" : "Removed from library", { duration: 1600 });
      }}
    >
      <Heart
        className={cn(
          "h-[1.05rem] w-[1.05rem] transition-colors",
          saved
            ? "text-[oklch(0.72_0.17_162)] fill-[oklch(0.72_0.17_162)]"
            : "text-muted-foreground",
          popping && "animate-anantha-pop",
        )}
      />
    </Button>
  );
}
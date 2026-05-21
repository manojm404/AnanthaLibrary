import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ChatSurface } from "./ChatSurface";
import type { Verse } from "@/lib/verses";
import { getReference } from "@/lib/verses";

export function ChatModal({
  open,
  onOpenChange,
  verseContext,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  verseContext?: Verse;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl p-0 gap-0 overflow-hidden glass-strong">
        <DialogHeader className="px-5 py-4 border-b">
          <DialogTitle style={{ fontFamily: "var(--font-display)" }} className="text-lg">
            Ask Anantha{verseContext ? ` · ${getReference(verseContext)}` : ""}
          </DialogTitle>
          <DialogDescription>A guided reflection on the wisdom of the Gita.</DialogDescription>
        </DialogHeader>
        <ChatSurface verseContext={verseContext} variant="modal" />
      </DialogContent>
    </Dialog>
  );
}
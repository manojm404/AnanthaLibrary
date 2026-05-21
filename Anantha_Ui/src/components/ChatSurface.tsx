import { useEffect, useRef, useState } from "react";
import { ArrowUp, BookOpen, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { makeId, type ChatMessage } from "@/lib/mock-chat";
import { chatApi } from "@/lib/api";
import type { Verse } from "@/lib/verses";
import { getReference } from "@/lib/verses";
import { CitationsDrawer } from "./CitationsDrawer";

function makeSeed(verseContext?: Verse): ChatMessage[] {
  if (verseContext) {
    return [
      {
        id: makeId(),
        role: "assistant",
        content: `Let's reflect together on Chapter ${getReference(verseContext)}. What would you like to ask about this verse?`,
        createdAt: Date.now(),
        citations: [verseContext],
      },
    ];
  }
  return [
    {
      id: makeId(),
      role: "assistant",
      content:
        "Namaste. I am Anantha — your companion to the Bhagavad Gita. Ask me about a verse, a feeling you're working through, or a question life has placed before you.",
      createdAt: Date.now(),
    },
  ];
}

export function ChatSurface({
  verseContext,
  variant = "page",
}: {
  verseContext?: Verse;
  variant?: "page" | "modal";
}) {
  const [messages, setMessages] = useState<ChatMessage[]>(() => makeSeed(verseContext));
  const [input, setInput] = useState(
    verseContext ? `Help me understand the meaning of ${getReference(verseContext)}.` : "",
  );
  const [typing, setTyping] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeCitations, setActiveCitations] = useState<Verse[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  async function send() {
    const text = input.trim();
    if (!text || typing) return;
    const userMsg: ChatMessage = {
      id: makeId(),
      role: "user",
      content: text,
      createdAt: Date.now(),
    };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setTyping(true);
    try {
      const { content, citations } = await chatApi(text, {
        verseId: verseContext?.id,
      });
      setMessages((m) => [
        ...m,
        { id: makeId(), role: "assistant", content, citations, createdAt: Date.now() },
      ]);
    } finally {
      setTyping(false);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }

  function openCitations(c: Verse[]) {
    setActiveCitations(c);
    setDrawerOpen(true);
  }

  return (
    <div
      className={cn(
        "flex flex-col",
        variant === "page"
          ? "h-[calc(100dvh-9rem)] md:h-[calc(100dvh-2rem)]"
          : "h-[70dvh] max-h-[640px]",
      )}
    >
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 md:px-6 py-6 space-y-4">
        {messages.map((m) => (
          <Message key={m.id} message={m} onOpenCitations={openCitations} />
        ))}
        {typing && <TypingIndicator />}
      </div>

      <div className="border-t bg-background/60 backdrop-blur p-3 md:p-4">
        <div className="relative flex items-end gap-2 max-w-3xl mx-auto">
          <Textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Ask Anantha…"
            aria-label="Message Anantha"
            rows={1}
            className="min-h-[48px] max-h-40 resize-none rounded-2xl glass pr-12"
          />
          <Button
            type="button"
            size="icon"
            onClick={send}
            disabled={!input.trim() || typing}
            aria-label="Send message"
            className="absolute right-2 bottom-2 h-9 w-9 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_-4px_var(--primary)]"
          >
            <ArrowUp className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <CitationsDrawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        citations={activeCitations}
      />
    </div>
  );
}

function Message({
  message,
  onOpenCitations,
}: {
  message: ChatMessage;
  onOpenCitations: (c: Verse[]) => void;
}) {
  const isUser = message.role === "user";
  return (
    <div
      className={cn(
        "flex gap-3 animate-anantha-slide-up",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && (
        <div
          aria-hidden
          className="shrink-0 h-8 w-8 rounded-full grid place-items-center bg-gradient-to-br from-primary to-primary/50 text-primary-foreground shadow-[0_0_18px_-4px_var(--primary)]"
        >
          <Sparkles className="h-4 w-4" />
        </div>
      )}
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
          isUser ? "bg-primary text-primary-foreground rounded-br-md" : "glass rounded-bl-md",
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!isUser && message.citations && message.citations.length > 0 && (
          <button
            type="button"
            onClick={() => onOpenCitations(message.citations!)}
            className="mt-3 inline-flex items-center gap-1.5 text-[12px] text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
          >
            <BookOpen className="h-3.5 w-3.5" />
            Sources · {message.citations.length}
          </button>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 animate-anantha-fade-in">
      <div
        aria-hidden
        className="shrink-0 h-8 w-8 rounded-full grid place-items-center bg-gradient-to-br from-primary to-primary/50 text-primary-foreground"
      >
        <Sparkles className="h-4 w-4 animate-anantha-pulse-soft" />
      </div>
      <div className="glass rounded-2xl rounded-bl-md px-4 py-3 flex items-center gap-2 text-sm text-muted-foreground">
        <span>Anantha is meditating</span>
        <span className="inline-flex gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-primary animate-anantha-pulse-soft" />
          <span
            className="h-1.5 w-1.5 rounded-full bg-primary animate-anantha-pulse-soft"
            style={{ animationDelay: "0.2s" }}
          />
          <span
            className="h-1.5 w-1.5 rounded-full bg-primary animate-anantha-pulse-soft"
            style={{ animationDelay: "0.4s" }}
          />
        </span>
      </div>
    </div>
  );
}
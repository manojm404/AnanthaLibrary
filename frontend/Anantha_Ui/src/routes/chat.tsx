import { createFileRoute } from "@tanstack/react-router";
import { ChatSurface } from "@/components/ChatSurface";

export const Route = createFileRoute("/chat")({
  head: () => ({
    meta: [
      { title: "Chat with Anantha — Anantha Library" },
      { name: "description", content: "Converse with Anantha about the Bhagavad Gita." },
    ],
  }),
  component: ChatPage,
});

function ChatPage() {
  return (
    <div className="mx-auto max-w-3xl h-full">
      <ChatSurface />
    </div>
  );
}
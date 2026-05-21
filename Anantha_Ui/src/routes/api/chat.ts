import { createFileRoute } from "@tanstack/react-router";
import { jsonResponse, mockChat, proxy } from "@/lib/ai-proxy.server";

export const Route = createFileRoute("/api/chat")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        let body: unknown = {};
        try {
          body = await request.json();
        } catch {
          body = {};
        }
        const prompt =
          typeof (body as { prompt?: unknown })?.prompt === "string"
            ? ((body as { prompt: string }).prompt)
            : "";

        const res = await proxy("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (res && res.ok) {
          const data = await res.text();
          return new Response(data, {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }
        return jsonResponse(mockChat(prompt));
      },
    },
  },
});
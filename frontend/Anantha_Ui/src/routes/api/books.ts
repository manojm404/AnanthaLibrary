import { createFileRoute } from "@tanstack/react-router";
import { jsonResponse, proxy } from "@/lib/ai-proxy.server";

export const Route = createFileRoute("/api/books")({
  server: {
    handlers: {
      GET: async () => {
        const res = await proxy("/books", { method: "GET" });
        if (res && res.ok) {
          const data = await res.text();
          return new Response(data, {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }
        // Fallback to default book list if backend is unreachable
        return jsonResponse({
          books: [{ id: "gita", title: "Bhagavad Gita" }]
        });
      },
    },
  },
});

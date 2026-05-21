import { createFileRoute } from "@tanstack/react-router";
import { jsonResponse, mockSearch, proxy } from "@/lib/ai-proxy.server";

export const Route = createFileRoute("/api/search")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        let body: unknown = {};
        try {
          body = await request.json();
        } catch {
          body = {};
        }
        const query =
          typeof (body as { query?: unknown })?.query === "string"
            ? ((body as { query: string }).query)
            : "";

        const res = await proxy("/search", {
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
        return jsonResponse(mockSearch(query));
      },
    },
  },
});
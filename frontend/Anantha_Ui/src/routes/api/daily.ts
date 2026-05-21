import { createFileRoute } from "@tanstack/react-router";
import { jsonResponse, mockDaily, proxy } from "@/lib/ai-proxy.server";

export const Route = createFileRoute("/api/daily")({
  server: {
    handlers: {
      GET: async () => {
        const res = await proxy("/daily", { method: "GET" });
        if (res && res.ok) {
          const data = await res.text();
          return new Response(data, {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }
        return jsonResponse(mockDaily());
      },
    },
  },
});
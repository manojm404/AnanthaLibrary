import { useRouterState } from "@tanstack/react-router";

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <div key={pathname} className="animate-anantha-fade-in">
      {children}
    </div>
  );
}
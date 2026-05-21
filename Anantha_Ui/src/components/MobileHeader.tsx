import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";

export function MobileHeader() {
  return (
    <header className="md:hidden sticky top-0 z-30 glass border-b">
      <div className="flex h-14 items-center justify-between px-4">
        <Logo />
        <ThemeToggle />
      </div>
    </header>
  );
}
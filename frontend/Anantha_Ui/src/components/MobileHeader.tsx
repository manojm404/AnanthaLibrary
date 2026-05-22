import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";
import { BookSelector } from "./BookSelector";

export function MobileHeader() {
  return (
    <header className="md:hidden sticky top-0 z-30 glass border-b">
      <div className="flex h-14 items-center justify-between px-4 gap-2">
        <Logo />
        <div className="flex-1 flex justify-center max-w-[160px]">
          <BookSelector />
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
}
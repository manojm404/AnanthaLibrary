import type { LucideIcon } from "lucide-react";
import { BookHeart, Home, MessageCircle, Search, Sun } from "lucide-react";

export type NavItem = {
  to: "/" | "/search" | "/chat" | "/library" | "/wisdom";
  label: string;
  icon: LucideIcon;
  exact?: boolean;
};

export const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Home", icon: Home, exact: true },
  { to: "/search", label: "Search", icon: Search },
  { to: "/chat", label: "Chat", icon: MessageCircle },
  { to: "/library", label: "Library", icon: BookHeart },
  { to: "/wisdom", label: "Wisdom", icon: Sun },
];
import { Globe } from "lucide-react";
import { useTranslation } from "react-i18next";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { LANGUAGES, LANGUAGE_STORAGE_KEY, type SupportedLanguage } from "@/i18n";
import { cn } from "@/lib/utils";

type Props = {
  collapsed?: boolean;
  className?: string;
};

export function LanguageSwitcher({ collapsed, className }: Props) {
  const { i18n, t } = useTranslation();
  const current = (i18n.resolvedLanguage ?? "en") as SupportedLanguage;

  function change(lng: SupportedLanguage) {
    i18n.changeLanguage(lng);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(LANGUAGE_STORAGE_KEY, lng);
        document.documentElement.setAttribute("lang", lng);
      } catch {
        /* ignore */
      }
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size={collapsed ? "icon" : "sm"}
          aria-label={t("common.language")}
          className={cn("gap-2", className)}
        >
          <Globe className="h-4 w-4" />
          {!collapsed && (
            <span className="text-xs font-medium">
              {LANGUAGES.find((l) => l.code === current)?.native ?? "English"}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="min-w-[160px]">
        {LANGUAGES.map((l) => (
          <DropdownMenuItem
            key={l.code}
            onSelect={() => change(l.code)}
            className={cn(
              "flex items-center justify-between gap-3 cursor-pointer",
              current === l.code && "text-primary",
            )}
          >
            <span>{l.native}</span>
            <span className="text-[11px] text-muted-foreground">{l.label}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
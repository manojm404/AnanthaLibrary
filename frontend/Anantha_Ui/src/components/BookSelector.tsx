import React from "react";
import { useLibrary } from "@/hooks/use-library";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { BookOpen } from "lucide-react";

export function BookSelector() {
  const { activeBookId, setActiveBookId, availableBooks, isLoadingBooks } = useLibrary();

  if (isLoadingBooks && availableBooks.length <= 1) {
    return (
      <div className="h-9 w-40 animate-pulse bg-muted rounded-md" />
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Select value={activeBookId} onValueChange={setActiveBookId}>
        <SelectTrigger className="w-[180px] h-9 glass border-none text-sm font-medium">
          <BookOpen className="w-4 h-4 mr-2 text-primary" />
          <SelectValue placeholder="Select Text" />
        </SelectTrigger>
        <SelectContent className="glass">
          {availableBooks.map((book) => (
            <SelectItem key={book.id} value={book.id} className="text-sm cursor-pointer">
              {book.title}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

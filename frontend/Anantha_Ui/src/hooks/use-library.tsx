import React, { createContext, useContext, useState, useEffect } from "react";
import { Book } from "@/lib/verses";
import { getBooks } from "@/lib/api";

type LibraryContextType = {
  activeBookId: string;
  setActiveBookId: (id: string) => void;
  availableBooks: Book[];
  isLoadingBooks: boolean;
};

const LibraryContext = createContext<LibraryContextType | undefined>(undefined);

export function LibraryProvider({ children }: { children: React.ReactNode }) {
  const [activeBookId, setActiveBookId] = useState("gita");
  const [availableBooks, setAvailableBooks] = useState<Book[]>([
    { id: "gita", title: "Bhagavad Gita" }
  ]);
  const [isLoadingBooks, setIsLoadingBooks] = useState(true);

  useEffect(() => {
    getBooks().then((books) => {
      if (books && books.length > 0) {
        setAvailableBooks(books);
        // Default to first book if gita is not found in the list
        if (!books.find(b => b.id === "gita")) {
          setActiveBookId(books[0].id);
        }
      }
      setIsLoadingBooks(false);
    });
  }, []);

  return (
    <LibraryContext.Provider value={{ activeBookId, setActiveBookId, availableBooks, isLoadingBooks }}>
      {children}
    </LibraryContext.Provider>
  );
}

export function useLibrary() {
  const context = useContext(LibraryContext);
  if (context === undefined) {
    throw new Error("useLibrary must be used within a LibraryProvider");
  }
  return context;
}

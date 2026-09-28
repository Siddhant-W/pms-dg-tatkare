import { useCallback, useState } from 'react';

const STORAGE_KEY = 'presento.recentTeacherSearches';
const MAX_ITEMS = 5;

function read(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function write(items: string[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch {
    // Best-effort only - private browsing or a full quota shouldn't break search.
  }
}

export function useRecentSearches() {
  const [recent, setRecent] = useState<string[]>(read);

  const addRecent = useCallback((term: string) => {
    const trimmed = term.trim();
    if (!trimmed) return;
    setRecent((prev) => {
      const next = [trimmed, ...prev.filter((t) => t.toLowerCase() !== trimmed.toLowerCase())].slice(0, MAX_ITEMS);
      write(next);
      return next;
    });
  }, []);

  const clearRecent = useCallback(() => {
    setRecent([]);
    write([]);
  }, []);

  const removeRecent = useCallback((term: string) => {
    setRecent((prev) => {
      const next = prev.filter((t) => t !== term);
      write(next);
      return next;
    });
  }, []);

  return { recent, addRecent, clearRecent, removeRecent };
}

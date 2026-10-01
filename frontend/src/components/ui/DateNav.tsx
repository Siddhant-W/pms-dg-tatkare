import { ChevronLeft, ChevronRight } from 'lucide-react';
import { addDays, formatShortDate, todayISO } from '../../lib/dates';
import { IconButton } from './IconButton';
import { Button } from './Button';

/** Previous / next day with a "Today" shortcut and a native date picker. */
export function DateNav({ value, onChange }: { value: string; onChange: (iso: string) => void }) {
  const isToday = value === todayISO();
  return (
    <div className="flex items-center gap-1.5">
      <IconButton aria-label="Previous day" variant="subtle" onClick={() => onChange(addDays(value, -1))}>
        <ChevronLeft size={18} />
      </IconButton>
      <label className="relative flex h-11 min-w-[9.5rem] cursor-pointer items-center justify-center rounded-lg border border-border bg-surface-elevated px-3 text-sm font-semibold text-text-primary transition-colors hover:border-accent focus-within:ring-2 focus-within:ring-accent/40">
        <span aria-hidden>{formatShortDate(value)}</span>
        <span className="sr-only">Choose date, currently {formatShortDate(value)}</span>
        <input
          type="date"
          value={value}
          onChange={(e) => e.target.value && onChange(e.target.value)}
          className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
          aria-label="Choose date"
        />
      </label>
      <IconButton aria-label="Next day" variant="subtle" onClick={() => onChange(addDays(value, 1))}>
        <ChevronRight size={18} />
      </IconButton>
      {!isToday && (
        <Button size="sm" variant="ghost" onClick={() => onChange(todayISO())}>
          Today
        </Button>
      )}
    </div>
  );
}

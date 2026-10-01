import { cn } from '../../lib/utils';

export interface FilterChipsProps {
  options: { label: string; value: string; count?: number }[];
  value: string;
  onChange: (val: string) => void;
  label?: string;
  className?: string;
}

/** Single-choice filter. A radiogroup so keyboard and screen-reader users get arrow-key semantics. */
export function FilterChips({ options, value, onChange, label, className }: FilterChipsProps) {
  return (
    <div role="radiogroup" aria-label={label} className={cn('no-scrollbar -mx-4 flex gap-2 overflow-x-auto px-4 py-1 sm:mx-0 sm:px-0', className)}>
      {options.map((opt) => {
        const selected = value === opt.value;
        return (
          <button
            key={opt.value}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onChange(opt.value)}
            className={cn(
              'flex min-h-[40px] shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-4 text-sm font-semibold transition-all active:scale-95',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg',
              selected
                ? 'border-primary bg-primary text-white shadow-sm'
                : 'border-border bg-surface-elevated text-text-secondary hover:border-accent hover:text-text-primary'
            )}
          >
            {opt.label}
            {opt.count !== undefined && (
              <span
                className={cn(
                  'rounded-full px-1.5 text-xs font-bold tabular-nums',
                  selected ? 'bg-white/20 text-white' : 'bg-surface text-text-muted'
                )}
              >
                {opt.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

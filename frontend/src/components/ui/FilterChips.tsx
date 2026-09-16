import { cn } from '../../lib/utils';

export interface FilterChipsProps {
  options: { label: string; value: string }[];
  value: string;
  onChange: (val: string) => void;
}

export function FilterChips({ options, value, onChange }: FilterChipsProps) {
  return (
    <div className="flex overflow-x-auto gap-2 py-2 no-scrollbar">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={cn(
            'whitespace-nowrap px-4 h-9 min-h-[44px] rounded-full text-sm font-medium transition-all active:scale-95',
            value === opt.value
              ? 'bg-primary text-white shadow-sm'
              : 'bg-surface text-text-secondary hover:bg-border-subtle'
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

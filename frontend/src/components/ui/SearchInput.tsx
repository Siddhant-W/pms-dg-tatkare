import React from 'react';
import { Search, X } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  onClear?: () => void;
}

export function SearchInput({ className, value, onClear, onChange, ...props }: SearchInputProps) {
  return (
    <div className="relative flex items-center">
      <Search size={17} className="pointer-events-none absolute left-3.5 text-text-muted" aria-hidden />
      <input
        type="search"
        value={value}
        onChange={onChange}
        aria-label={props['aria-label'] ?? props.placeholder ?? 'Search'}
        className={cn(
          'h-11 min-h-[44px] w-full rounded-lg border border-border bg-surface-elevated pl-10 pr-10 text-sm text-text-primary placeholder:text-text-muted',
          'transition-shadow focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 [&::-webkit-search-cancel-button]:hidden',
          className
        )}
        {...props}
      />
      {value && onClear && (
        <button
          type="button"
          onClick={onClear}
          aria-label="Clear search"
          className="absolute right-1 flex h-11 min-w-[44px] items-center justify-center text-text-muted hover:text-text-primary"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}

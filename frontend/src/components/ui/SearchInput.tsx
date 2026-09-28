import React from 'react';
import { Search, X } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  onClear?: () => void;
}

export function SearchInput({ className, value, onClear, onChange, ...props }: SearchInputProps) {
  return (
    <div className="relative flex items-center">
      <Search size={17} className="absolute left-3.5 text-text-muted pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={onChange}
        className={cn(
          'w-full pl-10 pr-10 py-2 h-11 min-h-[44px] rounded-lg border border-border bg-surface-elevated text-text-primary transition-shadow focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent',
          className
        )}
        {...props}
      />
      {value && onClear && (
        <button
          type="button"
          onClick={onClear}
          aria-label="Clear search"
          className="absolute right-2 p-1 text-text-muted hover:text-text-primary min-h-[44px] min-w-[44px] flex items-center justify-center"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}

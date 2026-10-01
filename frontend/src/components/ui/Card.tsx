import React from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
  /** `accent` adds a gold hairline along the top edge - used sparingly for the one card that matters on a page. */
  variant?: 'flat' | 'raised' | 'accent';
  interactive?: boolean;
}

export function Card({ className, padding = 'md', variant = 'raised', interactive, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'relative bg-surface-elevated rounded-xl border border-border/80 overflow-hidden transition-all duration-200',
        variant === 'raised' && 'shadow-sm',
        variant === 'accent' && 'shadow-sm before:absolute before:inset-x-0 before:top-0 before:h-[2px] before:bg-accent',
        interactive && 'cursor-pointer hover:shadow-md hover:-translate-y-px active:translate-y-0 active:scale-[0.995]',
        {
          'p-0': padding === 'none',
          'p-3': padding === 'sm',
          'p-4': padding === 'md',
          'p-6': padding === 'lg',
        },
        className
      )}
      {...props}
    />
  );
}

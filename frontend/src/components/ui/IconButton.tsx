import React from 'react';
import { cn } from '../../lib/utils';

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Required: icon-only buttons have no visible text for screen readers. */
  'aria-label': string;
  variant?: 'ghost' | 'primary' | 'subtle';
  size?: 'sm' | 'md';
}

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant = 'ghost', size = 'md', type = 'button', ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      className={cn(
        'inline-flex shrink-0 items-center justify-center rounded-full transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent',
        'disabled:opacity-50 disabled:pointer-events-none',
        variant === 'ghost' && 'text-text-primary hover:bg-surface active:bg-border-subtle',
        variant === 'subtle' && 'text-text-secondary bg-surface hover:bg-border-subtle',
        variant === 'primary' && 'bg-primary text-white hover:bg-primary-hover',
        size === 'sm' ? 'h-9 w-9' : 'h-11 w-11 min-h-[44px] min-w-[44px]',
        className
      )}
      {...props}
    />
  )
);
IconButton.displayName = 'IconButton';

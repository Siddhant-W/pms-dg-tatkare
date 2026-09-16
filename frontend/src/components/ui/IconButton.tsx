import React from 'react';
import { cn } from '../../lib/utils';
import { ButtonProps } from './Button';

export const IconButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'ghost', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center rounded-full transition-colors focus-visible:outline-none disabled:opacity-50 disabled:pointer-events-none',
          {
            'bg-primary text-white hover:bg-primary-hover': variant === 'primary',
            'bg-transparent text-text-primary hover:bg-surface': variant === 'ghost',
            'bg-error text-white hover:bg-error/90': variant === 'destructive',
            'w-9 h-9': size === 'sm',
            'w-11 h-11 min-h-[44px] min-w-[44px]': size === 'md',
            'w-14 h-14': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {isLoading ? <span className="border-2 border-t-transparent border-current rounded-full w-4 h-4 animate-spin"></span> : children}
      </button>
    );
  }
);
IconButton.displayName = 'IconButton';

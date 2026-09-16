import React from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-150 ease-out active:scale-[0.97] focus-visible:outline-none disabled:opacity-50 disabled:pointer-events-none disabled:active:scale-100',
          {
            'bg-primary text-white shadow-sm hover:bg-primary-hover hover:shadow-md': variant === 'primary',
            'bg-transparent text-text-primary hover:bg-surface active:bg-border-subtle': variant === 'ghost',
            'bg-error text-white shadow-sm hover:bg-error/90 hover:shadow-md': variant === 'destructive',
            'h-9 px-3 text-sm': size === 'sm',
            'h-11 px-4 min-h-[44px] text-base': size === 'md',
            'h-14 px-6 text-lg': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {isLoading ? <span className="mr-2 border-2 border-t-transparent border-white rounded-full w-4 h-4 animate-spin"></span> : null}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';

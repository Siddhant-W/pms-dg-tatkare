import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'accent' | 'secondary' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
}

const VARIANTS: Record<NonNullable<ButtonProps['variant']>, string> = {
  primary: 'bg-primary text-white shadow-sm hover:bg-primary-hover hover:shadow-md',
  // Gold is a fill with navy content on top - never white on gold (contrast).
  accent: 'bg-accent text-accent-fg shadow-sm hover:brightness-95 hover:shadow-md',
  secondary: 'bg-surface-elevated text-text-primary border border-border hover:border-accent hover:bg-accent-bg',
  ghost: 'bg-transparent text-text-primary hover:bg-surface active:bg-border-subtle',
  destructive: 'bg-error text-white shadow-sm hover:brightness-110 hover:shadow-md',
};

const SIZES: Record<NonNullable<ButtonProps['size']>, string> = {
  sm: 'h-9 px-3 text-sm gap-1.5',
  md: 'h-11 px-4 text-sm gap-2 min-h-[44px]',
  lg: 'h-12 px-6 text-base gap-2.5 min-h-[48px]',
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, leftIcon, children, disabled, type = 'button', ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-semibold tracking-tight transition-all duration-150 ease-out',
        'active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg',
        'disabled:opacity-50 disabled:pointer-events-none disabled:active:scale-100',
        VARIANTS[variant],
        SIZES[size],
        className
      )}
      {...props}
    >
      {isLoading ? <Loader2 size={16} className="animate-spin" aria-hidden /> : leftIcon}
      {children}
    </button>
  )
);
Button.displayName = 'Button';

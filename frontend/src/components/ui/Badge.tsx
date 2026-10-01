import React from 'react';
import { cn } from '../../lib/utils';

const TONES = {
  neutral: 'bg-surface border-border text-text-secondary',
  gold: 'bg-accent-bg border-accent/40 text-accent-fg',
  navy: 'bg-primary/10 border-primary/20 text-primary',
  success: 'bg-success-bg border-success/20 text-success',
  danger: 'bg-error-bg border-error/20 text-error',
} as const;

export function Badge({ children, tone = 'neutral', className }: { children: React.ReactNode; tone?: keyof typeof TONES; className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-1 whitespace-nowrap rounded-full border px-2 py-0.5 text-xs font-bold', TONES[tone], className)}>
      {children}
    </span>
  );
}

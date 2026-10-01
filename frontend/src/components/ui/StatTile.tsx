import React from 'react';
import { cn } from '../../lib/utils';
import { Card } from './Card';
import { Skeleton } from './Skeleton';
import { AnimatedCounter } from '../../features/dashboard/AnimatedCounter';

const TONES = {
  neutral: { value: 'text-text-primary', chip: 'bg-primary/10 text-primary' },
  success: { value: 'text-success', chip: 'bg-success-bg text-success' },
  danger: { value: 'text-error', chip: 'bg-error-bg text-error' },
  gold: { value: 'text-text-primary', chip: 'bg-accent-bg text-accent-fg' },
} as const;

/** One headline number with an icon chip - the dashboard/analytics building block. */
export function StatTile({
  label,
  value,
  hint,
  icon,
  tone = 'neutral',
  loading,
  onClick,
}: {
  label: string;
  value: number;
  hint?: string;
  icon: React.ReactNode;
  tone?: keyof typeof TONES;
  loading?: boolean;
  onClick?: () => void;
}) {
  const styles = TONES[tone];
  const body = loading ? (
    <div className="space-y-3">
      <Skeleton className="h-8 w-8 rounded-full" />
      <Skeleton className="h-8 w-14" />
      <Skeleton className="h-3 w-20" />
    </div>
  ) : (
    <div className="flex flex-col gap-2">
      <span className={cn('flex h-9 w-9 items-center justify-center rounded-full', styles.chip)} aria-hidden>
        {icon}
      </span>
      <span className={cn('font-heading text-4xl font-bold leading-none tabular-nums', styles.value)}>
        <AnimatedCounter value={value} />
      </span>
      <span className="text-sm font-semibold text-text-secondary">{label}</span>
      {hint && <span className="-mt-1 text-xs text-text-muted">{hint}</span>}
    </div>
  );

  return (
    <Card padding="md" interactive={!!onClick} onClick={onClick} role={onClick ? 'button' : undefined} tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), onClick()) : undefined}>
      {body}
    </Card>
  );
}

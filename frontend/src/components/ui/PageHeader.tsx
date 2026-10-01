import React from 'react';
import { cn } from '../../lib/utils';

/** Page title block: small eyebrow, Cinzel title, gold rule, optional actions. */
export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  className,
}: {
  eyebrow?: string;
  title: string;
  description?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}) {
  return (
    <header className={cn('flex flex-wrap items-end justify-between gap-x-4 gap-y-3', className)}>
      <div className="min-w-0">
        {eyebrow && <p className="mb-1 text-[11px] font-bold uppercase tracking-[0.14em] text-accent-ink">{eyebrow}</p>}
        <h1 className="text-2xl font-bold leading-tight text-text-primary sm:text-3xl">{title}</h1>
        <span className="gold-rule mt-2.5" aria-hidden />
        {description && <p className="mt-2.5 text-sm text-text-secondary">{description}</p>}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </header>
  );
}

export function SectionHeader({
  title,
  count,
  action,
  className,
}: {
  title: string;
  count?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('mb-3 flex items-center justify-between gap-3', className)}>
      <h2 className="flex items-center gap-2 text-lg font-bold text-text-primary">
        {title}
        {count !== undefined && (
          <span className="rounded-full bg-accent-bg px-2 py-0.5 font-sans text-xs font-bold tabular-nums tracking-normal text-accent-fg">
            {count}
          </span>
        )}
      </h2>
      {action}
    </div>
  );
}

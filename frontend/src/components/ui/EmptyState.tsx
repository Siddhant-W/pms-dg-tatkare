import React from 'react';
import { cn } from '../../lib/utils';

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('flex flex-col items-center justify-center px-4 py-12 text-center', className)}>
      {icon && (
        <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-accent-bg text-accent-fg" aria-hidden>
          {icon}
        </span>
      )}
      <h3 className="mb-1 text-lg font-bold text-text-primary">{title}</h3>
      {description && <p className="max-w-xs text-sm text-text-secondary">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

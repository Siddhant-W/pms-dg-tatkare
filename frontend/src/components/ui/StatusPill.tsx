import { Check, X, Clock, Circle, Ban } from 'lucide-react';
import { cn } from '../../lib/utils';

const LABELS: Record<string, string> = {
  PRESENT: 'Present',
  ABSENT: 'Absent',
  NOT_MARKED: 'Not Marked',
  PENDING: 'Pending',
  ASSIGNED: 'Assigned',
  UNRESOLVED: 'Unresolved',
  CANCELLED: 'Cancelled',
};

/** Status is always icon + label, never colour alone (design.md accessibility). */
export function StatusPill({ status, className }: { status: string; className?: string }) {
  let colorClass = 'bg-not-marked-bg text-not-marked';
  let Icon = Circle;

  switch (status) {
    case 'PRESENT':
    case 'ASSIGNED':
      colorClass = 'bg-present-bg text-present';
      Icon = Check;
      break;
    case 'ABSENT':
    case 'UNRESOLVED':
      colorClass = 'bg-absent-bg text-absent';
      Icon = X;
      break;
    case 'PENDING':
      colorClass = 'bg-pending-bg text-pending';
      Icon = Clock;
      break;
    case 'CANCELLED':
      colorClass = 'bg-not-marked-bg text-not-marked';
      Icon = Ban;
      break;
  }

  return (
    <span className={cn('inline-flex items-center gap-1 whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-bold', colorClass, className)}>
      <Icon size={12} strokeWidth={3} aria-hidden />
      {LABELS[status] ?? status}
    </span>
  );
}

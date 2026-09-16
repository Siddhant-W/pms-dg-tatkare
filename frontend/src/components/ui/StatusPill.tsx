import { Check, X, Clock, Circle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { AttendanceStatus, ProxyStatus } from '../../types';

const LABELS: Record<string, string> = {
  PRESENT: 'Present',
  ABSENT: 'Absent',
  NOT_MARKED: 'Not Marked',
  PENDING: 'Pending',
  ASSIGNED: 'Assigned',
  UNRESOLVED: 'Unresolved',
};

export function StatusPill({ status }: { status: AttendanceStatus | ProxyStatus | string }) {
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
  }

  return (
    <span className={cn('inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold', colorClass)}>
      <Icon size={12} strokeWidth={3} />
      {LABELS[status] ?? status}
    </span>
  );
}

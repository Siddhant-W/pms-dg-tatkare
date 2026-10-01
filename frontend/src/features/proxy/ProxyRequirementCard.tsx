import { UserRound, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { StatusPill } from '../../components/ui/StatusPill';
import { Button } from '../../components/ui/Button';
import { cn } from '../../lib/utils';
import { ProxyRequirement } from '../../types';

// Left-edge accent by pipeline state, matching the period-row treatment from
// the Administrative Calm design system (design.md #3/#6).
const ACCENT: Record<string, string> = {
  PENDING: 'border-l-pending',
  ASSIGNED: 'border-l-assigned',
  UNRESOLVED: 'border-l-unresolved',
};

export function ProxyRequirementCard({ requirement }: { requirement: ProxyRequirement }) {
  const navigate = useNavigate();
  return (
    <Card className={cn('flex flex-col gap-3 border-l-4', ACCENT[requirement.status])}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-2.5">
          <span className="mt-0.5 inline-flex h-6 min-w-[1.75rem] shrink-0 items-center justify-center rounded-md bg-surface px-1.5 text-xs font-bold tabular-nums text-text-secondary">
            P{requirement.period_number}
          </span>
          <div className="min-w-0">
            <p className="font-bold leading-snug">
              {requirement.class_name}
              {requirement.subject ? ` · ${requirement.subject}` : ''}
            </p>
            <p className="mt-0.5 flex items-start gap-1.5 text-sm text-text-secondary">
              <UserRound size={14} className="mt-0.5 shrink-0" aria-hidden />
              <span className="min-w-0">{requirement.absent_teacher_name} <span className="text-text-muted">(absent)</span></span>
            </p>
          </div>
        </div>
        <StatusPill status={requirement.status} />
      </div>
      {requirement.status === 'PENDING' && (
        <Button size="sm" onClick={() => navigate(`/proxy/${requirement.id}/candidates`)}>
          Find a proxy
        </Button>
      )}
      {requirement.assigned_proxy_teacher_name && (
        <p className="flex items-center gap-1.5 text-sm font-medium text-success">
          <CheckCircle2 size={15} aria-hidden />
          Covered by {requirement.assigned_proxy_teacher_name}
        </p>
      )}
    </Card>
  );
}

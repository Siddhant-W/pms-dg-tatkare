import { UserRound, CheckCircle2 } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { ProxyRequirement } from '../../types';
import { StatusPill } from '../../components/ui/StatusPill';
import { Button } from '../../components/ui/Button';
import { useNavigate } from 'react-router-dom';
import { cn } from '../../lib/utils';

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
      <div className="flex justify-between items-start gap-3">
        <div className="min-w-0 flex items-start gap-2.5">
          <span className="shrink-0 mt-0.5 inline-flex items-center justify-center h-6 min-w-[1.75rem] px-1.5 rounded-md bg-surface text-xs font-bold tabular-nums text-text-secondary">
            P{requirement.period_number}
          </span>
          <div className="min-w-0">
            <div className="font-bold truncate">
              {requirement.class_name}
              {requirement.subject ? ` · ${requirement.subject}` : ''}
            </div>
            <div className="flex items-center gap-1.5 text-sm text-text-secondary mt-0.5">
              <UserRound size={14} className="shrink-0" />
              <span className="truncate">{requirement.absent_teacher_name}</span>
            </div>
          </div>
        </div>
        <StatusPill status={requirement.status} />
      </div>
      {requirement.status === 'PENDING' && (
        <Button size="sm" onClick={() => navigate(`/proxy/${requirement.id}/candidates`)}>
          Assign Proxy
        </Button>
      )}
      {requirement.assigned_proxy_teacher_name && (
        <div className="flex items-center gap-1.5 text-sm text-success">
          <CheckCircle2 size={15} />
          Assigned to {requirement.assigned_proxy_teacher_name}
        </div>
      )}
    </Card>
  );
}

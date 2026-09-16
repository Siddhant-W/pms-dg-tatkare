import { UserRound, CheckCircle2 } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { ProxyRequirement } from '../../types';
import { StatusPill } from '../../components/ui/StatusPill';
import { Button } from '../../components/ui/Button';
import { useNavigate } from 'react-router-dom';

export function ProxyRequirementCard({ requirement }: { requirement: ProxyRequirement }) {
  const navigate = useNavigate();
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex justify-between items-start gap-3">
        <div className="min-w-0">
          <div className="font-bold truncate">Period {requirement.period_number} · {requirement.class_name}</div>
          <div className="flex items-center gap-1.5 text-sm text-text-secondary mt-0.5">
            <UserRound size={14} className="shrink-0" />
            <span className="truncate">{requirement.absent_teacher_name}</span>
          </div>
          {requirement.subject && <div className="text-sm text-text-secondary mt-0.5">{requirement.subject}</div>}
        </div>
        <StatusPill status={requirement.status} />
      </div>
      {requirement.status === 'PENDING' && (
        <Button size="sm" onClick={() => navigate(`/proxy/${requirement.id}/candidates`)}>
          Assign
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

import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { ClipboardCheck, UserRoundCheck, PartyPopper } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { MetricCard } from './MetricCard';
import { ProxyRequirementCard } from '../proxy/ProxyRequirementCard';
import { attendanceService } from '../../services/attendanceService';
import { proxyService } from '../../services/proxyService';
import { ProxyRequirement } from '../../types';

function todayISO() {
  return new Date().toISOString().split('T')[0];
}

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

export function DashboardPage() {
  const navigate = useNavigate();
  const today = todayISO();
  const displayDate = new Date().toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['attendance-summary', today],
    queryFn: () => attendanceService.getAttendanceSummary(today),
  });

  const { data: requirements = [], isLoading: requirementsLoading } = useQuery<ProxyRequirement[]>({
    queryKey: ['proxy-requirements', today],
    queryFn: () => proxyService.getProxyRequirements(today),
  });

  const isLoading = summaryLoading || requirementsLoading;

  const pending = requirements.filter((r) => r.status === 'PENDING');
  const assigned = requirements.filter((r) => r.status === 'ASSIGNED');
  const unresolved = requirements.filter((r) => r.status === 'UNRESOLVED');

  const attendanceNotStarted = !!summary && summary.present === 0 && summary.absent === 0;

  return (
    <div className="p-4 space-y-6">
      <header className="animate-fade-in">
        <h1 className="text-2xl font-bold tracking-tight">{greeting()}, Mrs. Vaishali</h1>
        <p className="text-text-secondary">{displayDate}</p>
      </header>

      {isLoading ? (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} padding="md" className="flex flex-col items-center gap-2">
                <Skeleton className="h-8 w-10" />
                <Skeleton className="h-3 w-16" />
              </Card>
            ))}
          </div>
          <div className="space-y-3">
            {Array.from({ length: 2 }).map((_, i) => (
              <Card key={i} className="space-y-3">
                <Skeleton className="h-4 w-40" />
                <Skeleton className="h-3 w-28" />
                <Skeleton className="h-9 w-full rounded-md" />
              </Card>
            ))}
          </div>
        </div>
      ) : attendanceNotStarted ? (
        <Card padding="lg" className="flex flex-col items-center text-center gap-3 animate-slide-up">
          <span className="flex items-center justify-center w-14 h-14 rounded-full bg-primary/10">
            <ClipboardCheck size={26} className="text-primary" />
          </span>
          <div>
            <h2 className="font-semibold">Attendance not marked yet</h2>
            <p className="text-sm text-text-secondary mt-1">Mark today's attendance to see proxy requirements.</p>
          </div>
          <Button onClick={() => navigate('/attendance')}>Mark Attendance</Button>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 animate-slide-up">
            <MetricCard type="absent" value={summary?.absent ?? 0} label="Absent" />
            <MetricCard type="proxy" value={pending.length} label="Proxy Needed" />
            <MetricCard type="assigned" value={assigned.length} label="Assigned" />
            <MetricCard type="unresolved" value={unresolved.length} label="Unresolved" />
          </div>

          <Button className="w-full gap-2" variant="ghost" onClick={() => navigate('/attendance')}>
            <UserRoundCheck size={18} /> Mark Attendance
          </Button>

          <section>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold">Needs Attention</h2>
            </div>
            <div className="space-y-3">
              {pending.length === 0 && (
                <div className="flex flex-col items-center gap-2 text-center py-8 text-text-secondary text-sm">
                  <PartyPopper size={22} className="text-success" />
                  All clear — no pending proxy requirements today.
                </div>
              )}
              {pending.map((req) => (
                <ProxyRequirementCard key={req.id} requirement={req} />
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

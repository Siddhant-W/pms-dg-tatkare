import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { UserX, Clock, CheckCircle2, TriangleAlert, PartyPopper, ArrowRight, ClipboardCheck } from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader, SectionHeader } from '../../components/ui/PageHeader';
import { StatTile } from '../../components/ui/StatTile';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { ErrorState } from '../../components/ui/ErrorState';
import { Skeleton } from '../../components/ui/Skeleton';
import { ProxyRequirementCard } from '../proxy/ProxyRequirementCard';
import { attendanceService } from '../../services/attendanceService';
import { proxyService } from '../../services/proxyService';
import { useAuth } from '../auth/useAuth';
import { formatLongDate, todayISO } from '../../lib/dates';

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

export function DashboardPage() {
  const navigate = useNavigate();
  const user = useAuth((s) => s.user);
  const today = todayISO();
  const name = (user?.full_name || user?.username || 'Supervisor').split(' ').slice(0, 2).join(' ');

  const summary = useQuery({
    queryKey: ['attendance-summary', today],
    queryFn: () => attendanceService.getAttendanceSummary(today),
  });
  const requirementsQuery = useQuery({
    queryKey: ['proxy-requirements', today],
    queryFn: () => proxyService.getProxyRequirements(today),
  });

  const requirements = requirementsQuery.data ?? [];
  const pending = requirements.filter((r) => r.status === 'PENDING');
  const assigned = requirements.filter((r) => r.status === 'ASSIGNED');
  const unresolved = requirements.filter((r) => r.status === 'UNRESOLVED');
  const loading = summary.isLoading || requirementsQuery.isLoading;
  const failed = summary.error || requirementsQuery.error;
  const absent = summary.data?.absent ?? 0;

  return (
    <Page>
      <PageHeader eyebrow={formatLongDate(today)} title={`${greeting()}, ${name}`} />

      {failed ? (
        <ErrorState onRetry={() => { void summary.refetch(); void requirementsQuery.refetch(); }} />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatTile label="Absent today" value={absent} icon={<UserX size={18} />} tone="danger" loading={loading} onClick={() => navigate('/attendance')} />
            <StatTile label="Need a proxy" value={pending.length} icon={<Clock size={18} />} tone="gold" loading={loading} />
            <StatTile label="Covered" value={assigned.length} icon={<CheckCircle2 size={18} />} tone="success" loading={loading} onClick={() => navigate('/proxies')} />
            <StatTile label="Unresolved" value={unresolved.length} icon={<TriangleAlert size={18} />} tone="neutral" loading={loading} />
          </div>

          {!loading && absent === 0 && (
            <Card variant="accent" className="flex items-center gap-4">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-success-bg text-success" aria-hidden><PartyPopper size={22} /></span>
              <div className="min-w-0 flex-1">
                <p className="font-bold">Everyone is present</p>
                <p className="text-sm text-text-secondary">Teachers count as present until you mark them absent.</p>
              </div>
              <Button variant="secondary" size="sm" leftIcon={<ClipboardCheck size={15} />} onClick={() => navigate('/attendance')}>
                Attendance
              </Button>
            </Card>
          )}

          <section>
            <SectionHeader title="Needs attention" count={loading ? undefined : pending.length} />
            {loading ? (
              <div className="grid gap-3 md:grid-cols-2">
                {[0, 1].map((i) => (
                  <Card key={i} className="space-y-3"><Skeleton className="h-4 w-40" /><Skeleton className="h-3 w-28" /><Skeleton className="h-9 w-full rounded-lg" /></Card>
                ))}
              </div>
            ) : pending.length === 0 ? (
              <Card variant="flat" className="py-8 text-center text-sm text-text-secondary">
                {absent === 0 ? 'Nothing to arrange today.' : 'All clear. No periods are waiting for a proxy.'}
              </Card>
            ) : (
              <div className="grid gap-3 md:grid-cols-2">
                {pending.map((r) => <ProxyRequirementCard key={r.id} requirement={r} />)}
              </div>
            )}
          </section>

          {assigned.length > 0 && (
            <section>
              <SectionHeader
                title="Covered today"
                count={assigned.length}
                action={<Button variant="ghost" size="sm" onClick={() => navigate('/proxies')}>View all <ArrowRight size={14} aria-hidden /></Button>}
              />
              <ul className="space-y-2">
                {assigned.map((r) => (
                  <li key={r.id} className="flex items-center justify-between gap-3 rounded-lg border border-border/80 bg-surface-elevated px-3 py-2.5">
                    <span className="flex min-w-0 items-center gap-2 text-sm">
                      <CheckCircle2 size={16} className="shrink-0 text-success" aria-hidden />
                      <span className="truncate"><span className="font-semibold tabular-nums">P{r.period_number}</span> · {r.class_name}</span>
                    </span>
                    <span className="max-w-[45%] shrink-0 truncate text-xs text-text-secondary">{r.assigned_proxy_teacher_name}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </Page>
  );
}

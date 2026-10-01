import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Timer, ShieldCheck, UserX, Clock, CheckCircle2, TriangleAlert } from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader, SectionHeader } from '../../components/ui/PageHeader';
import { DateNav } from '../../components/ui/DateNav';
import { StatTile } from '../../components/ui/StatTile';
import { Card } from '../../components/ui/Card';
import { ErrorState } from '../../components/ui/ErrorState';
import { Skeleton } from '../../components/ui/Skeleton';
import { MiniBarChart } from './MiniBarChart';
import { analyticsService } from '../../services/analyticsService';
import { todayISO } from '../../lib/dates';
import { DailyStats } from '../../types';

function formatDuration(seconds: number | null) {
  if (seconds === null || seconds === undefined) return '—';
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
}

export function AnalyticsPage() {
  const [date, setDate] = useState(todayISO());
  const { data: stats, isLoading, error, refetch } = useQuery<DailyStats>({
    queryKey: ['analytics', date],
    queryFn: () => analyticsService.getDailyStats(date),
  });

  return (
    <Page>
      <PageHeader eyebrow="Insights" title="Analytics" actions={<DateNav value={date} onChange={setDate} />} />

      {error ? (
        <ErrorState onRetry={() => refetch()} />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatTile label="Absent" value={stats?.absent_count ?? 0} icon={<UserX size={18} />} tone="danger" loading={isLoading} />
            <StatTile label="Proxies needed" value={stats?.requirements_count ?? 0} icon={<Clock size={18} />} tone="gold" loading={isLoading} />
            <StatTile label="Assigned" value={stats?.assigned_count ?? 0} icon={<CheckCircle2 size={18} />} tone="success" loading={isLoading} />
            <StatTile label="Unresolved" value={stats?.unresolved_count ?? 0} icon={<TriangleAlert size={18} />} loading={isLoading} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Card className="flex flex-col items-center gap-1 text-center">
              <Timer size={18} className="text-primary" aria-hidden />
              {isLoading ? <Skeleton className="h-8 w-16" /> : <span className="font-heading text-2xl font-bold tabular-nums">{formatDuration(stats?.avg_assignment_time_seconds ?? null)}</span>}
              <span className="text-sm text-text-secondary">Avg. assignment time</span>
            </Card>
            <Card className="flex flex-col items-center gap-1 text-center">
              <ShieldCheck size={18} className="text-accent-ink" aria-hidden />
              {isLoading ? <Skeleton className="h-8 w-10" /> : <span className="font-heading text-2xl font-bold tabular-nums">{stats?.collision_attempts ?? 0}</span>}
              <span className="text-sm text-text-secondary">Double-bookings prevented</span>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <section>
              <SectionHeader title="Proxy load" />
              <Card>{isLoading ? <Skeleton className="h-24 w-full" /> : <MiniBarChart items={stats?.proxy_load_distribution ?? []} emptyLabel="No proxies assigned on this day." />}</Card>
            </section>
            <section>
              <SectionHeader title="Most often absent" />
              <Card>{isLoading ? <Skeleton className="h-24 w-full" /> : <MiniBarChart items={stats?.most_frequently_absent_teachers ?? []} emptyLabel="No absence history yet." />}</Card>
            </section>
            <section className="lg:col-span-2">
              <SectionHeader title="Most often a proxy" />
              <Card>{isLoading ? <Skeleton className="h-24 w-full" /> : <MiniBarChart items={stats?.most_frequently_assigned_teachers ?? []} emptyLabel="No assignment history yet." />}</Card>
            </section>
          </div>
        </div>
      )}
    </Page>
  );
}

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Timer, ShieldCheck } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import { Skeleton } from '../../components/ui/Skeleton';
import { MetricCard } from '../dashboard/MetricCard';
import { MiniBarChart } from './MiniBarChart';
import { analyticsService } from '../../services/analyticsService';
import { DailyStats } from '../../types';

function todayISO() {
  return new Date().toISOString().split('T')[0];
}

function formatDuration(seconds: number | null) {
  if (seconds === null || seconds === undefined) return '—';
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
}

export function AnalyticsPage() {
  const [date, setDate] = useState(todayISO());

  const { data: stats, isLoading } = useQuery<DailyStats>({
    queryKey: ['analytics', date],
    queryFn: () => analyticsService.getDailyStats(date),
  });

  return (
    <div className="p-4 space-y-6 animate-fade-in">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="h-10 min-h-[44px] px-3 rounded-lg border border-border bg-bg text-text-primary text-sm"
        />
      </header>

      {isLoading && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} padding="md" className="flex flex-col items-center gap-2">
                <Skeleton className="h-7 w-10" />
                <Skeleton className="h-3 w-16" />
              </Card>
            ))}
          </div>
          <Card className="space-y-3">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-2 w-full rounded-full" />
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-2 w-full rounded-full" />
          </Card>
        </div>
      )}

      {stats && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <MetricCard type="absent" value={stats.absent_count} label="Absent" />
            <MetricCard type="proxy" value={stats.requirements_count} label="Proxies Needed" />
            <MetricCard type="assigned" value={stats.assigned_count} label="Assigned" />
            <MetricCard type="unresolved" value={stats.unresolved_count} label="Unresolved" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Card padding="md" className="flex flex-col items-center gap-1">
              <Timer size={18} className="text-primary mb-1" />
              <span className="text-2xl font-bold tabular-nums">{formatDuration(stats.avg_assignment_time_seconds)}</span>
              <span className="text-sm text-text-secondary text-center">Avg. Assignment Time</span>
            </Card>
            <Card padding="md" className="flex flex-col items-center gap-1">
              <ShieldCheck size={18} className="text-warning mb-1" />
              <span className="text-2xl font-bold tabular-nums text-warning">{stats.collision_attempts}</span>
              <span className="text-sm text-text-secondary text-center">Collisions Prevented</span>
            </Card>
          </div>

          <section>
            <h2 className="text-lg font-bold mb-3">Today's Proxy Load</h2>
            <Card>
              <MiniBarChart items={stats.proxy_load_distribution} emptyLabel="No proxies assigned yet today." />
            </Card>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-3">Most Frequently Absent</h2>
            <Card>
              <MiniBarChart items={stats.most_frequently_absent_teachers} emptyLabel="No absence history yet." />
            </Card>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-3">Most Frequently Assigned as Proxy</h2>
            <Card>
              <MiniBarChart items={stats.most_frequently_assigned_teachers} emptyLabel="No assignment history yet." />
            </Card>
          </section>
        </>
      )}
    </div>
  );
}

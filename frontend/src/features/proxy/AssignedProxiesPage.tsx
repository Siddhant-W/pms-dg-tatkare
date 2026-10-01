import { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { ArrowRight, HandHelping, SearchX, Clock, Ban } from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader } from '../../components/ui/PageHeader';
import { DateNav } from '../../components/ui/DateNav';
import { FilterChips } from '../../components/ui/FilterChips';
import { SearchInput } from '../../components/ui/SearchInput';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Avatar } from '../../components/ui/Avatar';
import { StatusPill } from '../../components/ui/StatusPill';
import { ConfirmDialog } from '../../components/ui/Modal';
import { EmptyState } from '../../components/ui/EmptyState';
import { ErrorState } from '../../components/ui/ErrorState';
import { ListSkeleton } from '../../components/ui/Skeleton';
import { proxyService } from '../../services/proxyService';
import { parseApiError } from '../../lib/errors';
import { formatTime, todayISO } from '../../lib/dates';
import { cn } from '../../lib/utils';
import { ProxyAssignmentDetail } from '../../types';

function lessonLabel(a: ProxyAssignmentDetail) {
  return [a.class_name, a.subject].filter(Boolean).join(' · ') || 'Free period';
}

export function AssignedProxiesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [date, setDate] = useState(todayISO());
  const [filter, setFilter] = useState<'ASSIGNED' | 'CANCELLED' | 'ALL'>('ASSIGNED');
  const [search, setSearch] = useState('');
  const [toCancel, setToCancel] = useState<ProxyAssignmentDetail | null>(null);

  // One fetch for every status; the chips filter client-side so their counts are always right.
  const { data: rows = [], isLoading, error, refetch } = useQuery({
    queryKey: ['proxy-assignments', date],
    queryFn: () => proxyService.getAssignments(date, 'ALL'),
  });
  const { data: requirements = [] } = useQuery({
    queryKey: ['proxy-requirements', date],
    queryFn: () => proxyService.getProxyRequirements(date),
  });
  const pending = requirements.filter((r) => r.status === 'PENDING');

  const cancel = useMutation({
    mutationFn: (a: ProxyAssignmentDetail) => proxyService.cancelAssignment(a.id),
    onSuccess: (_d, a) => {
      toast.success('Assignment cancelled', { description: `${a.proxy_teacher_name} no longer covers period ${a.period_number}.` });
      setToCancel(null);
    },
    onError: (err) => toast.error('Could not cancel', { description: parseApiError(err).message }),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['proxy-assignments'] });
      queryClient.invalidateQueries({ queryKey: ['proxy-requirements'] });
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
    },
  });

  const counts = useMemo(
    () => ({
      ASSIGNED: rows.filter((r) => r.status === 'ASSIGNED').length,
      CANCELLED: rows.filter((r) => r.status === 'CANCELLED').length,
      ALL: rows.length,
    }),
    [rows]
  );

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    return rows.filter((r) => {
      if (filter !== 'ALL' && r.status !== filter) return false;
      if (!q) return true;
      return [r.proxy_teacher_name, r.absent_teacher_name, r.class_name, r.subject].some((v) => v?.toLowerCase().includes(q));
    });
  }, [rows, filter, search]);

  const isFiltered = !!search || filter !== 'ALL';

  return (
    <Page>
      <PageHeader
        eyebrow="Cover for absent teachers"
        title="Assigned Proxies"
        description="Who is covering which period, and for whom."
        actions={<DateNav value={date} onChange={setDate} />}
      />

      {pending.length > 0 && (
        <Card variant="accent" className="flex flex-wrap items-center justify-between gap-3">
          <p className="flex items-center gap-2 text-sm font-semibold">
            <Clock size={18} className="text-pending" aria-hidden />
            {pending.length} period{pending.length === 1 ? ' still needs' : 's still need'} a proxy
          </p>
          <Button size="sm" onClick={() => navigate('/')}>Assign now</Button>
        </Card>
      )}

      <div className="space-y-3">
        <SearchInput placeholder="Search teacher, class or subject" value={search} onChange={(e) => setSearch(e.target.value)} onClear={() => setSearch('')} />
        <FilterChips
          label="Filter by status"
          value={filter}
          onChange={(v) => setFilter(v as typeof filter)}
          options={[
            { label: 'Assigned', value: 'ASSIGNED', count: counts.ASSIGNED },
            { label: 'Cancelled', value: 'CANCELLED', count: counts.CANCELLED },
            { label: 'All', value: 'ALL', count: counts.ALL },
          ]}
        />
      </div>

      <section aria-label="Proxy assignments">
        {isLoading ? (
          <ListSkeleton rows={4} />
        ) : error ? (
          <ErrorState title="Couldn't load assignments" onRetry={() => refetch()} />
        ) : visible.length === 0 ? (
          <EmptyState
            icon={isFiltered ? <SearchX size={26} /> : <HandHelping size={26} />}
            title={isFiltered ? 'Nothing matches' : 'No proxies assigned'}
            description={isFiltered ? 'Try a different search or status.' : 'When a teacher is absent and a proxy is assigned, it shows up here.'}
            action={isFiltered ? <Button variant="secondary" onClick={() => { setSearch(''); setFilter('ALL'); }}>Clear filters</Button> : undefined}
          />
        ) : (
          <>
            {/* Phones: one card per assignment. */}
            <ul className="space-y-3 md:hidden">
              {visible.map((a) => (
                <li key={a.id}>
                  <AssignmentCard a={a} onCancel={() => setToCancel(a)} />
                </li>
              ))}
            </ul>

            {/* Tablet and up: a real table, easier to scan down the page. */}
            <Card padding="none" className="hidden md:block">
              <table className="w-full text-left text-sm">
                <caption className="sr-only">Proxy assignments for the selected date</caption>
                <thead className="border-b border-border bg-surface text-xs font-bold uppercase tracking-wide text-text-secondary">
                  <tr>
                    <th scope="col" className="px-4 py-3">Period</th>
                    <th scope="col" className="px-4 py-3">Class &amp; subject</th>
                    <th scope="col" className="px-4 py-3">Absent teacher</th>
                    <th scope="col" className="px-4 py-3">Proxy teacher</th>
                    <th scope="col" className="px-4 py-3">Status</th>
                    <th scope="col" className="px-4 py-3"><span className="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {visible.map((a) => (
                    <tr key={a.id} className={cn(a.status === 'CANCELLED' && 'text-text-muted')}>
                      <td className="px-4 py-3 font-bold tabular-nums">P{a.period_number}</td>
                      <td className="px-4 py-3">{lessonLabel(a)}</td>
                      <td className="px-4 py-3">{a.absent_teacher_name}</td>
                      <td className="px-4 py-3 font-semibold">{a.proxy_teacher_name}</td>
                      <td className="px-4 py-3"><StatusPill status={a.status} /></td>
                      <td className="px-4 py-3 text-right">
                        {a.status === 'ASSIGNED' && (
                          <Button size="sm" variant="ghost" onClick={() => setToCancel(a)} aria-label={`Cancel proxy for period ${a.period_number}, ${a.class_name ?? ''}`}>
                            Cancel
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          </>
        )}
      </section>

      <ConfirmDialog
        isOpen={!!toCancel}
        onClose={() => setToCancel(null)}
        onConfirm={() => toCancel && cancel.mutate(toCancel)}
        isPending={cancel.isPending}
        tone="destructive"
        title="Cancel this proxy?"
        description={toCancel ? `${toCancel.proxy_teacher_name} will no longer cover period ${toCancel.period_number} (${lessonLabel(toCancel)}). The period goes back to needing a proxy.` : undefined}
        confirmLabel="Cancel proxy"
        cancelLabel="Keep it"
      />
    </Page>
  );
}

function AssignmentCard({ a, onCancel }: { a: ProxyAssignmentDetail; onCancel: () => void }) {
  const cancelled = a.status === 'CANCELLED';
  return (
    <Card className={cn('space-y-3 border-l-4', cancelled ? 'border-l-not-marked opacity-80' : 'border-l-assigned')}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="inline-flex h-7 min-w-[2rem] shrink-0 items-center justify-center rounded-md bg-primary px-1.5 text-xs font-bold tabular-nums text-white">
            P{a.period_number}
          </span>
          <p className="font-bold leading-snug">{lessonLabel(a)}</p>
        </div>
        <StatusPill status={a.status} />
      </div>

      <div className="flex flex-col gap-2 rounded-lg bg-surface p-2.5 sm:flex-row sm:items-center">
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <Avatar name={a.absent_teacher_name ?? '?'} size="sm" />
          <div className="min-w-0">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-text-muted">Absent</p>
            <p className="text-sm font-semibold leading-snug">{a.absent_teacher_name}</p>
          </div>
        </div>
        <ArrowRight size={16} className="shrink-0 self-center text-text-muted max-sm:rotate-90" aria-hidden />
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <Avatar name={a.proxy_teacher_name ?? '?'} size="sm" />
          <div className="min-w-0">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-text-muted">Proxy</p>
            <p className="text-sm font-semibold leading-snug">{a.proxy_teacher_name}</p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between gap-2">
        <p className="text-xs text-text-muted">
          {cancelled && a.cancelled_at ? (
            <span className="inline-flex items-center gap-1"><Ban size={12} aria-hidden /> Cancelled {formatTime(a.cancelled_at)}</span>
          ) : (
            <>Assigned {formatTime(a.assigned_at)}{a.assigned_by_name ? ` by ${a.assigned_by_name}` : ''}</>
          )}
        </p>
        {!cancelled && (
          <Button size="sm" variant="ghost" onClick={onCancel} className="text-error hover:bg-error-bg">
            Cancel
          </Button>
        )}
      </div>
    </Card>
  );
}

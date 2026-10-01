import { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { UserCheck, UserX, Users, RotateCcw, SearchX } from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader } from '../../components/ui/PageHeader';
import { SearchInput } from '../../components/ui/SearchInput';
import { FilterChips } from '../../components/ui/FilterChips';
import { Avatar } from '../../components/ui/Avatar';
import { Card } from '../../components/ui/Card';
import { Switch } from '../../components/ui/Switch';
import { Button } from '../../components/ui/Button';
import { ConfirmDialog } from '../../components/ui/Modal';
import { EmptyState } from '../../components/ui/EmptyState';
import { ErrorState } from '../../components/ui/ErrorState';
import { ListSkeleton } from '../../components/ui/Skeleton';
import { Badge } from '../../components/ui/Badge';
import { attendanceService } from '../../services/attendanceService';
import { proxyService } from '../../services/proxyService';
import { parseApiError } from '../../lib/errors';
import { formatLongDate, todayISO } from '../../lib/dates';
import { cn } from '../../lib/utils';
import { TeacherWithAttendance } from '../../types';

const isAbsent = (t: TeacherWithAttendance) => t.attendance_status === 'ABSENT';

export function AttendancePage() {
  const today = todayISO();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('ALL');
  const [pendingIds, setPendingIds] = useState<Set<string>>(new Set());
  const [confirmReset, setConfirmReset] = useState(false);

  const teachersKey = ['teachers', today];

  const { data: teachers = [], isLoading, error, refetch } = useQuery({
    queryKey: teachersKey,
    queryFn: () => attendanceService.getTeachersWithAttendance(today),
  });

  // Needed only to tell the supervisor what "Mark all present" will undo.
  const { data: requirements = [] } = useQuery({
    queryKey: ['proxy-requirements', today],
    queryFn: () => proxyService.getProxyRequirements(today),
  });

  // Anything derived from attendance goes stale when it changes.
  const refreshDependents = () => {
    queryClient.invalidateQueries({ queryKey: ['attendance-summary'] });
    queryClient.invalidateQueries({ queryKey: ['proxy-requirements'] });
    queryClient.invalidateQueries({ queryKey: ['proxy-assignments'] });
    queryClient.invalidateQueries({ queryKey: ['candidates'] });
  };

  const setStatus = (id: string, absent: boolean) =>
    queryClient.setQueryData<TeacherWithAttendance[]>(teachersKey, (old) =>
      old?.map((t) => (t.id === id ? { ...t, attendance_status: absent ? 'ABSENT' : 'PRESENT' } : t))
    );

  const toggle = useMutation({
    mutationFn: ({ teacher, absent }: { teacher: TeacherWithAttendance; absent: boolean }) =>
      attendanceService.markAttendance(teacher.id, today, absent ? 'ABSENT' : 'PRESENT'),
    onMutate: ({ teacher, absent }) => {
      setPendingIds((s) => new Set(s).add(teacher.id));
      setStatus(teacher.id, absent); // optimistic: the switch moves immediately
    },
    onSuccess: (_d, { teacher, absent }) => {
      toast.success(absent ? `${teacher.name} marked absent` : `${teacher.name} is present again`);
    },
    onError: (err, { teacher, absent }) => {
      setStatus(teacher.id, !absent); // roll back
      toast.error(`Could not update ${teacher.name}`, { description: parseApiError(err).message });
    },
    onSettled: (_d, _e, { teacher }) => {
      setPendingIds((s) => {
        const next = new Set(s);
        next.delete(teacher.id);
        return next;
      });
      refreshDependents();
      queryClient.invalidateQueries({ queryKey: teachersKey });
    },
  });

  const resetAll = useMutation({
    mutationFn: () => attendanceService.resetAll(today),
    onSuccess: (result) => {
      queryClient.setQueryData<TeacherWithAttendance[]>(teachersKey, (old) =>
        old?.map((t) => ({ ...t, attendance_status: 'PRESENT' }))
      );
      setConfirmReset(false);
      toast.success('Everyone is marked present', {
        description: result.cleared_absences
          ? `${result.cleared_absences} absence${result.cleared_absences === 1 ? '' : 's'} cleared.`
          : undefined,
      });
    },
    onError: (err) => toast.error('Could not reset attendance', { description: parseApiError(err).message }),
    onSettled: () => {
      refreshDependents();
      queryClient.invalidateQueries({ queryKey: teachersKey });
    },
  });

  const absentCount = teachers.filter(isAbsent).length;
  const presentCount = teachers.length - absentCount;
  const assignedToday = requirements.filter((r) => r.status === 'ASSIGNED').length;

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return teachers.filter((t) => {
      if (q && !t.name.toLowerCase().includes(q)) return false;
      if (filter === 'ABSENT') return isAbsent(t);
      if (filter === 'PRESENT') return !isAbsent(t);
      return true;
    });
  }, [teachers, search, filter]);

  const filters = [
    { label: 'All', value: 'ALL', count: teachers.length },
    { label: 'Present', value: 'PRESENT', count: presentCount },
    { label: 'Absent', value: 'ABSENT', count: absentCount },
  ];

  return (
    <>
    <Page>
      <PageHeader
        eyebrow={formatLongDate(today)}
        title="Attendance"
        description="Everyone starts the day present. Switch on only the teachers who are absent."
      />

      <div className="grid grid-cols-3 gap-2 sm:gap-3">
        <SummaryCell icon={<Users size={16} />} label="Teachers" value={teachers.length} loading={isLoading} />
        <SummaryCell icon={<UserCheck size={16} />} label="Present" value={presentCount} tone="success" loading={isLoading} />
        <SummaryCell icon={<UserX size={16} />} label="Absent" value={absentCount} tone="danger" loading={isLoading} />
      </div>

      <div className="space-y-3">
        <SearchInput placeholder="Search teachers" value={search} onChange={(e) => setSearch(e.target.value)} onClear={() => setSearch('')} />
        <FilterChips label="Filter by status" options={filters} value={filter} onChange={setFilter} />
      </div>

      <section aria-label="Teachers">
        {isLoading ? (
          <ListSkeleton rows={7} />
        ) : error ? (
          <ErrorState title="Couldn't load teachers" onRetry={() => refetch()} />
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={<SearchX size={26} />}
            title={teachers.length === 0 ? 'No teachers yet' : 'No teachers match'}
            description={teachers.length === 0 ? 'An admin can add teachers from Timetable settings.' : 'Try a different name or filter.'}
            action={
              (search || filter !== 'ALL') && (
                <Button variant="secondary" onClick={() => { setSearch(''); setFilter('ALL'); }}>
                  Clear filters
                </Button>
              )
            }
          />
        ) : (
          <ul className="space-y-2">
            {filtered.map((t) => {
              const absent = isAbsent(t);
              return (
                <li key={t.id}>
                  <Card
                    padding="sm"
                    className={cn('flex items-center gap-3 border-l-4 transition-colors', absent ? 'border-l-error bg-error-bg/40' : 'border-l-transparent')}
                  >
                    <Avatar name={t.name} />
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-semibold">{t.name}</p>
                      <p className="truncate text-xs text-text-secondary">
                        {t.class_name ? `Class teacher · ${t.class_name}` : 'Subject teacher'}
                      </p>
                    </div>
                    <span className={cn('text-xs font-bold', absent ? 'text-error' : 'text-text-muted')}>{absent ? 'Absent' : 'Present'}</span>
                    <Switch
                      tone="danger"
                      checked={absent}
                      disabled={pendingIds.has(t.id)}
                      label={`Mark ${t.name} absent`}
                      onCheckedChange={(next) => toggle.mutate({ teacher: t, absent: next })}
                    />
                  </Card>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <ConfirmDialog
        isOpen={confirmReset}
        onClose={() => setConfirmReset(false)}
        onConfirm={() => resetAll.mutate()}
        isPending={resetAll.isPending}
        title="Mark everyone present?"
        description="This clears every absence recorded for today."
        confirmLabel="Mark all present"
        tone="destructive"
      >
        <ul className="space-y-1.5 rounded-lg bg-surface p-3 text-sm">
          <li className="flex justify-between"><span>Absences cleared</span><Badge tone="danger">{absentCount}</Badge></li>
          <li className="flex justify-between"><span>Proxy assignments cancelled</span><Badge tone="gold">{assignedToday}</Badge></li>
        </ul>
        <p className="text-xs text-text-muted">Pending proxy requirements for today are removed as well.</p>
      </ConfirmDialog>
    </Page>
    {/* Outside <Page>: sticky needs the tall <main> as its container, not a per-section wrapper. */}
      {absentCount > 0 && (
        <div className="sticky bottom-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom)+0.75rem)] z-30 px-4 pb-1 lg:bottom-4">
          <div className="flex items-center justify-between gap-3 rounded-xl border border-border bg-surface-elevated p-3 shadow-lg">
            <p className="text-sm font-semibold">
              <span className="tabular-nums text-error">{absentCount}</span> absent today
            </p>
            <Button size="sm" variant="secondary" leftIcon={<RotateCcw size={15} />} onClick={() => setConfirmReset(true)}>
              Mark all present
            </Button>
          </div>
        </div>
      )}

    </>
  );
}

function SummaryCell({ icon, label, value, tone, loading }: { icon: React.ReactNode; label: string; value: number; tone?: 'success' | 'danger'; loading?: boolean }) {
  return (
    <Card padding="sm" className="text-center">
      <span className={cn('mx-auto mb-1 flex h-7 w-7 items-center justify-center rounded-full', tone === 'success' ? 'bg-success-bg text-success' : tone === 'danger' ? 'bg-error-bg text-error' : 'bg-primary/10 text-primary')} aria-hidden>
        {icon}
      </span>
      <p className="font-heading text-2xl font-bold tabular-nums">{loading ? '–' : value}</p>
      <p className="text-xs font-semibold text-text-secondary">{label}</p>
    </Card>
  );
}

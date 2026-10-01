import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Coffee, RefreshCw, Settings2, SearchX } from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader } from '../../components/ui/PageHeader';
import { FilterChips } from '../../components/ui/FilterChips';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { SearchInput } from '../../components/ui/SearchInput';
import { Avatar } from '../../components/ui/Avatar';
import { EmptyState } from '../../components/ui/EmptyState';
import { ErrorState } from '../../components/ui/ErrorState';
import { ListSkeleton, Skeleton } from '../../components/ui/Skeleton';
import { teacherService } from '../../services/teacherService';
import { timetableService } from '../../services/timetableService';
import { useAuth } from '../auth/useAuth';
import { todayISO, weekdayOf } from '../../lib/dates';
import { cn } from '../../lib/utils';
import { TimetableEntry, Weekday } from '../../types';
import { DAYS, PERIODS, trimTime } from './shared';

/** Read-only timetable for everyone. Admins get a shortcut to the editor. */
export function TimetablePage() {
  const isAdmin = useAuth((s) => s.user?.role === 'ADMIN');
  const [day, setDay] = useState<Weekday>(weekdayOf(todayISO()) ?? 'MONDAY');
  const [search, setSearch] = useState('');
  const [teacherId, setTeacherId] = useState<string | null>(null);

  const teachersQuery = useQuery({
    queryKey: ['teachers', todayISO()],
    queryFn: () => teacherService.getTeachers(todayISO()),
  });
  const teachers = useMemo(() => teachersQuery.data ?? [], [teachersQuery.data]);
  const teacher = teachers.find((t) => t.id === teacherId) ?? null;

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return q ? teachers.filter((t) => t.name.toLowerCase().includes(q)) : teachers;
  }, [teachers, search]);

  const entriesQuery = useQuery<TimetableEntry[]>({
    queryKey: ['timetable', day, teacherId],
    queryFn: () => timetableService.getTimetable(day, teacherId!),
    enabled: !!teacherId,
  });
  const byPeriod = useMemo(() => new Map((entriesQuery.data ?? []).map((e) => [e.period_number, e])), [entriesQuery.data]);

  return (
    <Page>
      <PageHeader
        eyebrow="Weekly schedule"
        title="Timetable"
        description={teacher ? undefined : 'Pick a teacher to see their day.'}
        actions={
          isAdmin && (
            <Link to="/timetable/settings">
              <Button variant="secondary" size="sm" leftIcon={<Settings2 size={15} />}>Edit timetable</Button>
            </Link>
          )
        }
      />

      <FilterChips label="Day" options={DAYS} value={day} onChange={(v) => setDay(v as Weekday)} />

      {!teacher ? (
        <div className="space-y-3">
          <SearchInput placeholder="Search teachers" value={search} onChange={(e) => setSearch(e.target.value)} onClear={() => setSearch('')} />
          {teachersQuery.isLoading ? (
            <ListSkeleton rows={6} />
          ) : teachersQuery.error ? (
            <ErrorState title="Couldn't load teachers" onRetry={() => teachersQuery.refetch()} />
          ) : filtered.length === 0 ? (
            <EmptyState icon={<SearchX size={26} />} title="No teachers found" description="Try a different name." />
          ) : (
            <ul className="grid gap-2 md:grid-cols-2">
              {filtered.map((t) => (
                <li key={t.id}>
                  <button type="button" onClick={() => setTeacherId(t.id)} className="block w-full text-left">
                    <Card padding="sm" interactive className="flex items-center gap-3">
                      <Avatar name={t.name} />
                      <div className="min-w-0">
                        <p className="truncate font-semibold">{t.name}</p>
                        {t.class_name && <p className="truncate text-xs text-text-secondary">Class teacher · {t.class_name}</p>}
                      </div>
                    </Card>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-2">
            <div className="flex min-w-0 items-center gap-3">
              <Avatar name={teacher.name} />
              <div className="min-w-0">
                <p className="truncate font-bold">{teacher.name}</p>
                {teacher.class_name && <p className="truncate text-xs text-text-secondary">Class teacher · {teacher.class_name}</p>}
              </div>
            </div>
            <Button variant="ghost" size="sm" leftIcon={<RefreshCw size={14} />} onClick={() => setTeacherId(null)}>Change</Button>
          </div>

          {entriesQuery.isLoading ? (
            <div className="space-y-2">{PERIODS.map((p) => <Skeleton key={p} className="h-16 w-full rounded-xl" />)}</div>
          ) : entriesQuery.error ? (
            <ErrorState title="Couldn't load the timetable" onRetry={() => entriesQuery.refetch()} />
          ) : (
            <ol className="space-y-2.5">
              {PERIODS.map((p) => {
                const entry = byPeriod.get(p);
                const free = !entry || entry.is_free || entry.is_recess;
                return (
                  <li key={p}>
                    <Card padding="sm" className={cn('flex items-center gap-4', free && 'border-dashed bg-surface shadow-none')}>
                      <span className={cn('flex h-11 w-11 shrink-0 items-center justify-center rounded-lg text-base font-bold', free ? 'bg-border-subtle text-text-muted' : 'bg-primary/10 text-primary')}>{p}</span>
                      {free ? (
                        <p className="flex-1 font-medium text-text-muted">{entry?.is_recess ? 'Recess' : 'Free'}</p>
                      ) : (
                        <div className="min-w-0 flex-1">
                          <p className="truncate font-bold">{entry.subject ?? 'Untitled'}</p>
                          {entry.class_name && <p className="truncate text-sm text-text-secondary">{entry.class_name}</p>}
                        </div>
                      )}
                      {entry?.time_start && <span className="shrink-0 text-xs tabular-nums text-text-muted">{trimTime(entry.time_start)}–{trimTime(entry.time_end)}</span>}
                    </Card>
                    {p === 5 && (
                      <div className="flex items-center gap-3 py-3" aria-hidden>
                        <div className="h-px flex-1 bg-border" />
                        <span className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-text-muted"><Coffee size={13} /> Recess · 2:30 – 3:00 PM</span>
                        <div className="h-px flex-1 bg-border" />
                      </div>
                    )}
                  </li>
                );
              })}
            </ol>
          )}
        </div>
      )}
    </Page>
  );
}

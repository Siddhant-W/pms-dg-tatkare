import { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import { ArrowLeft, Coffee, Pencil, Plus, UserRoundX, UserRoundCheck } from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader } from '../../components/ui/PageHeader';
import { FilterChips } from '../../components/ui/FilterChips';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Select, Field } from '../../components/ui/Field';
import { Avatar } from '../../components/ui/Avatar';
import { Badge } from '../../components/ui/Badge';
import { SearchInput } from '../../components/ui/SearchInput';
import { ConfirmDialog } from '../../components/ui/Modal';
import { EmptyState } from '../../components/ui/EmptyState';
import { ErrorState } from '../../components/ui/ErrorState';
import { ListSkeleton, Skeleton } from '../../components/ui/Skeleton';
import { teacherService } from '../../services/teacherService';
import { timetableService } from '../../services/timetableService';
import { parseApiError } from '../../lib/errors';
import { todayISO, weekdayOf } from '../../lib/dates';
import { cn } from '../../lib/utils';
import { Teacher, TimetableEntry, Weekday } from '../../types';
import { DAYS, PERIODS, trimTime } from './shared';
import { PeriodEditor, EditorTarget } from './PeriodEditor';
import { TeacherEditor } from './TeacherEditor';

type Tab = 'periods' | 'teachers';

/** Admin-only (guarded in the router and enforced again by the API). */
export function TimetableSettingsPage() {
  const [tab, setTab] = useState<Tab>('periods');
  const [teacherId, setTeacherId] = useState<string>('');
  const [day, setDay] = useState<Weekday>(weekdayOf(todayISO()) ?? 'MONDAY');
  const [editor, setEditor] = useState<EditorTarget | null>(null);
  const [toClear, setToClear] = useState<TimetableEntry | null>(null);
  const queryClient = useQueryClient();

  // Inactive teachers are included so the Teachers tab can reactivate them.
  const teachersQuery = useQuery({
    queryKey: ['teachers', 'all', todayISO()],
    queryFn: () => teacherService.getTeachers(todayISO(), true),
  });
  const allTeachers = useMemo(() => teachersQuery.data ?? [], [teachersQuery.data]);
  const activeTeachers = useMemo(() => allTeachers.filter((t) => t.active), [allTeachers]);
  const selectedId = teacherId || activeTeachers[0]?.id || '';

  const entriesQuery = useQuery<TimetableEntry[]>({
    queryKey: ['timetable', day, selectedId],
    queryFn: () => timetableService.getTimetable(day, selectedId),
    enabled: !!selectedId && tab === 'periods',
  });
  const byPeriod = useMemo(() => new Map((entriesQuery.data ?? []).map((e) => [e.period_number, e])), [entriesQuery.data]);

  const clear = useMutation({
    mutationFn: (entry: TimetableEntry) => timetableService.clearEntry(entry.id),
    onSuccess: () => {
      toast.success('Period cleared');
      setToClear(null);
      setEditor(null);
    },
    onError: (err) => toast.error("Couldn't clear this period", { description: parseApiError(err).message }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ['timetable'] }),
  });

  return (
    <Page>
      <div>
        <Link to="/timetable" className="mb-3 inline-flex items-center gap-1.5 text-sm font-semibold text-text-secondary hover:text-text-primary">
          <ArrowLeft size={15} aria-hidden /> Back to timetable
        </Link>
        <PageHeader
          eyebrow="Admin"
          title="Timetable settings"
          description="Assign teachers, classes and subjects to periods. Conflicts are checked before anything is saved."
        />
      </div>

      <div role="tablist" aria-label="Settings" className="grid grid-cols-2 gap-1 rounded-xl bg-surface p-1 sm:inline-grid sm:min-w-[20rem]">
        {([['periods', 'Periods'], ['teachers', 'Teachers']] as [Tab, string][]).map(([key, label]) => (
          <button
            key={key}
            role="tab"
            id={`tab-${key}`}
            aria-selected={tab === key}
            aria-controls={`panel-${key}`}
            onClick={() => setTab(key)}
            className={cn('h-10 rounded-lg text-sm font-semibold transition-colors', tab === key ? 'bg-surface-elevated text-text-primary shadow-sm' : 'text-text-secondary hover:text-text-primary')}
          >
            {label}
          </button>
        ))}
      </div>

      {teachersQuery.isLoading ? (
        <ListSkeleton rows={5} />
      ) : teachersQuery.error ? (
        <ErrorState title="Couldn't load teachers" onRetry={() => teachersQuery.refetch()} />
      ) : tab === 'periods' ? (
        <section id="panel-periods" role="tabpanel" aria-labelledby="tab-periods" className="space-y-4">
          {activeTeachers.length === 0 ? (
            <EmptyState icon={<Plus size={26} />} title="Add a teacher first" description="Periods belong to a teacher." action={<Button onClick={() => setTab('teachers')}>Go to teachers</Button>} />
          ) : (
            <>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                <Field label="Teacher" className="sm:w-80">
                  {(p) => (
                    <Select {...p} value={selectedId} onChange={(e) => setTeacherId(e.target.value)}>
                      {activeTeachers.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                    </Select>
                  )}
                </Field>
                <FilterChips label="Day" options={DAYS} value={day} onChange={(v) => setDay(v as Weekday)} />
              </div>

              {entriesQuery.isLoading ? (
                <div className="space-y-2">{PERIODS.map((p) => <Skeleton key={p} className="h-16 w-full rounded-xl" />)}</div>
              ) : entriesQuery.error ? (
                <ErrorState title="Couldn't load this timetable" onRetry={() => entriesQuery.refetch()} />
              ) : (
                <ol className="grid gap-2.5 lg:grid-cols-2">
                  {PERIODS.map((p) => {
                    const entry = byPeriod.get(p);
                    const lesson = entry && !entry.is_free && !entry.is_recess;
                    return (
                      <li key={p}>
                        <button
                          type="button"
                          className="block w-full text-left"
                          onClick={() => setEditor({ teacherId: selectedId, weekday: day, period: p, entry })}
                          aria-label={`Period ${p}: ${lesson ? `${entry.subject}, ${entry.class_name}` : entry?.is_recess ? 'recess' : 'free'}. Edit`}
                        >
                          <Card padding="sm" interactive className={cn('flex items-center gap-4', !lesson && 'border-dashed bg-surface shadow-none')}>
                            <span className={cn('flex h-11 w-11 shrink-0 items-center justify-center rounded-lg font-bold', lesson ? 'bg-primary/10 text-primary' : 'bg-border-subtle text-text-muted')}>{p}</span>
                            <div className="min-w-0 flex-1">
                              {lesson ? (
                                <>
                                  <p className="truncate font-bold">{entry.subject}</p>
                                  <p className="truncate text-sm text-text-secondary">{entry.class_name}{entry.time_start ? ` · ${trimTime(entry.time_start)}–${trimTime(entry.time_end)}` : ''}</p>
                                </>
                              ) : (
                                <p className="flex items-center gap-1.5 font-medium text-text-muted">
                                  {entry?.is_recess ? <><Coffee size={14} aria-hidden /> Recess</> : 'Free · tap to assign'}
                                </p>
                              )}
                            </div>
                            {lesson ? <Pencil size={15} className="shrink-0 text-text-muted" aria-hidden /> : <Plus size={16} className="shrink-0 text-text-muted" aria-hidden />}
                          </Card>
                        </button>
                      </li>
                    );
                  })}
                </ol>
              )}
            </>
          )}
        </section>
      ) : (
        <TeachersPanel teachers={allTeachers} />
      )}

      <PeriodEditor target={editor} teachers={activeTeachers} onClose={() => setEditor(null)} onRequestClear={setToClear} />

      <ConfirmDialog
        isOpen={!!toClear}
        onClose={() => setToClear(null)}
        onConfirm={() => toClear && clear.mutate(toClear)}
        isPending={clear.isPending}
        tone="destructive"
        title="Clear this period?"
        description={toClear ? `${toClear.subject ?? 'This lesson'} · ${toClear.class_name ?? ''} becomes a free period for this teacher.` : undefined}
        confirmLabel="Clear period"
      />
    </Page>
  );
}

function TeachersPanel({ teachers }: { teachers: Teacher[] }) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState<Teacher | null>(null);
  const [adding, setAdding] = useState(false);
  const [toggle, setToggle] = useState<Teacher | null>(null);

  const setActive = useMutation({
    mutationFn: (t: Teacher) => teacherService.updateTeacher(t.id, { active: !t.active }),
    onSuccess: (_d, t) => {
      toast.success(t.active ? `${t.name} deactivated` : `${t.name} reactivated`);
      setToggle(null);
    },
    onError: (err) => toast.error("Couldn't update the teacher", { description: parseApiError(err).message }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ['teachers'] }),
  });

  const q = search.trim().toLowerCase();
  const shown = q ? teachers.filter((t) => t.name.toLowerCase().includes(q)) : teachers;

  return (
    <section id="panel-teachers" role="tabpanel" aria-labelledby="tab-teachers" className="space-y-3">
      <div className="flex items-center gap-2">
        <div className="min-w-0 flex-1"><SearchInput placeholder="Search teachers" value={search} onChange={(e) => setSearch(e.target.value)} onClear={() => setSearch('')} /></div>
        <Button leftIcon={<Plus size={16} />} onClick={() => setAdding(true)}>Add</Button>
      </div>

      {shown.length === 0 ? (
        <EmptyState title="No teachers found" description={q ? 'Try a different name.' : 'Add the first teacher to get started.'} />
      ) : (
        <ul className="grid gap-2 md:grid-cols-2">
          {shown.map((t) => (
            <li key={t.id}>
              <Card padding="sm" className={cn('flex items-center gap-3', !t.active && 'opacity-70')}>
                <Avatar name={t.name} />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-semibold">{t.name}</p>
                  <p className="flex flex-wrap items-center gap-1.5 text-xs text-text-secondary">
                    {t.class_name ? `Class teacher · ${t.class_name}` : 'Subject teacher'}
                    {!t.active && <Badge>Inactive</Badge>}
                  </p>
                </div>
                <Button size="sm" variant="ghost" aria-label={`Edit ${t.name}`} onClick={() => setEditing(t)}><Pencil size={15} /></Button>
                <Button size="sm" variant="ghost" aria-label={t.active ? `Deactivate ${t.name}` : `Reactivate ${t.name}`} onClick={() => (t.active ? setToggle(t) : setActive.mutate(t))}>
                  {t.active ? <UserRoundX size={16} /> : <UserRoundCheck size={16} />}
                </Button>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <TeacherEditor isOpen={adding || !!editing} teacher={editing} onClose={() => { setAdding(false); setEditing(null); }} />
      <ConfirmDialog
        isOpen={!!toggle}
        onClose={() => setToggle(null)}
        onConfirm={() => toggle && setActive.mutate(toggle)}
        isPending={setActive.isPending}
        tone="destructive"
        title="Deactivate this teacher?"
        description={toggle ? `${toggle.name} won't appear in attendance or be offered as a proxy. Their timetable is kept, and you can reactivate them anytime.` : undefined}
        confirmLabel="Deactivate"
      />
    </section>
  );
}

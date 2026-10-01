import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  UserRound, ClipboardList, CheckCircle2, Undo2, TriangleAlert, History as HistoryIcon, X, RotateCcw, UserPlus, CalendarCog, ChevronDown, type LucideIcon,
} from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader } from '../../components/ui/PageHeader';
import { DateNav } from '../../components/ui/DateNav';
import { EmptyState } from '../../components/ui/EmptyState';
import { ErrorState } from '../../components/ui/ErrorState';
import { Card } from '../../components/ui/Card';
import { SearchInput } from '../../components/ui/SearchInput';
import { Button } from '../../components/ui/Button';
import { ListSkeleton } from '../../components/ui/Skeleton';
import { historyService } from '../../services/historyService';
import { teacherService } from '../../services/teacherService';
import { formatTime, todayISO } from '../../lib/dates';
import { cn } from '../../lib/utils';
import { AuditEvent } from '../../types';

interface EventStyle { Icon: LucideIcon; bg: string; text: string }
const NEUTRAL: EventStyle = { Icon: HistoryIcon, bg: 'bg-surface', text: 'text-text-muted' };
const EVENT_CONFIG: Record<string, EventStyle> = {
  ATTENDANCE_MARKED: { Icon: UserRound, bg: 'bg-primary/10', text: 'text-primary' },
  ATTENDANCE_RESET: { Icon: RotateCcw, bg: 'bg-primary/10', text: 'text-primary' },
  ATTENDANCE_RESET_ALL: { Icon: RotateCcw, bg: 'bg-primary/10', text: 'text-primary' },
  REQUIREMENT_CREATED: { Icon: ClipboardList, bg: 'bg-warning-bg', text: 'text-warning' },
  ASSIGNMENT_CREATED: { Icon: CheckCircle2, bg: 'bg-success-bg', text: 'text-success' },
  ASSIGNMENT_CANCELLED: { Icon: Undo2, bg: 'bg-not-marked-bg', text: 'text-not-marked' },
  ASSIGNMENT_COLLISION_PREVENTED: { Icon: TriangleAlert, bg: 'bg-error-bg', text: 'text-error' },
  TEACHER_CREATED: { Icon: UserPlus, bg: 'bg-accent-bg', text: 'text-accent-fg' },
  TEACHER_UPDATED: { Icon: UserPlus, bg: 'bg-accent-bg', text: 'text-accent-fg' },
  TIMETABLE_ENTRY_UPDATED: { Icon: CalendarCog, bg: 'bg-accent-bg', text: 'text-accent-fg' },
  TIMETABLE_ENTRY_MOVED: { Icon: CalendarCog, bg: 'bg-accent-bg', text: 'text-accent-fg' },
  TIMETABLE_ENTRY_CLEARED: { Icon: CalendarCog, bg: 'bg-accent-bg', text: 'text-accent-fg' },
};

export function HistoryPage() {
  const [date, setDate] = useState(todayISO());
  const [teacherSearch, setTeacherSearch] = useState('');
  const [teacherId, setTeacherId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: teachers = [] } = useQuery({
    queryKey: ['teachers', todayISO()],
    queryFn: () => teacherService.getTeachers(todayISO()),
  });
  const selectedTeacher = teachers.find((t) => t.id === teacherId) ?? null;
  const suggestions = useMemo(() => {
    const q = teacherSearch.trim().toLowerCase();
    return q ? teachers.filter((t) => t.name.toLowerCase().includes(q)).slice(0, 6) : [];
  }, [teachers, teacherSearch]);

  const { data: events = [], isLoading, error, refetch } = useQuery<AuditEvent[]>({
    queryKey: ['history', date, teacherId],
    queryFn: () => historyService.getHistory(date, teacherId ?? undefined),
  });

  return (
    <Page>
      <PageHeader eyebrow="Audit trail" title="History" description="Every change, with who made it and when." actions={<DateNav value={date} onChange={setDate} />} />

      {selectedTeacher ? (
        <div className="flex items-center justify-between rounded-lg border border-accent/30 bg-accent-bg px-3">
          <span className="text-sm font-semibold text-accent-fg">Showing {selectedTeacher.name}</span>
          <Button size="sm" variant="ghost" leftIcon={<X size={14} />} onClick={() => setTeacherId(null)}>Clear</Button>
        </div>
      ) : (
        <div className="relative">
          <SearchInput placeholder="Filter by teacher" value={teacherSearch} onChange={(e) => setTeacherSearch(e.target.value)} onClear={() => setTeacherSearch('')} />
          {suggestions.length > 0 && (
            <ul className="absolute z-20 mt-1 w-full overflow-hidden rounded-xl border border-border bg-surface-elevated shadow-lg animate-fade-in">
              {suggestions.map((t) => (
                <li key={t.id}>
                  <button type="button" className="min-h-[44px] w-full px-4 text-left text-sm hover:bg-surface" onClick={() => { setTeacherId(t.id); setTeacherSearch(''); }}>
                    {t.name}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <section aria-label="Events">
        {isLoading ? (
          <ListSkeleton rows={5} />
        ) : error ? (
          <ErrorState title="Couldn't load history" onRetry={() => refetch()} />
        ) : events.length === 0 ? (
          <EmptyState icon={<HistoryIcon size={26} />} title="Nothing recorded" description="No activity for this day yet." />
        ) : (
          <ol className="space-y-2">
            {events.map((event) => {
              const open = expandedId === event.id;
              const { Icon, bg, text } = EVENT_CONFIG[event.event_type] ?? NEUTRAL;
              return (
                <li key={event.id}>
                  <Card padding="none">
                    <button type="button" aria-expanded={open} onClick={() => setExpandedId(open ? null : event.id)} className="flex w-full items-start gap-3 p-3 text-left">
                      <span className={cn('flex h-8 w-8 shrink-0 items-center justify-center rounded-full', bg)} aria-hidden><Icon size={15} className={text} /></span>
                      <span className="min-w-0 flex-1">
                        <span className="block text-sm font-medium">{event.summary}</span>
                        <span className="mt-0.5 block text-xs text-text-secondary">{formatTime(event.created_at)}{event.actor_name && ` · ${event.actor_name}`}</span>
                      </span>
                      <ChevronDown size={16} className={cn('mt-1 shrink-0 text-text-muted transition-transform', open && 'rotate-180')} aria-hidden />
                    </button>
                    {open && (
                      <pre className="mx-3 mb-3 overflow-x-auto rounded-lg bg-surface p-2 text-xs text-text-muted">{JSON.stringify(event.metadata, null, 2)}</pre>
                    )}
                  </Card>
                </li>
              );
            })}
          </ol>
        )}
      </section>
    </Page>
  );
}

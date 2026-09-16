import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { UserRound, ClipboardList, CheckCircle2, Undo2, TriangleAlert, History as HistoryIcon, X } from 'lucide-react';
import { EmptyState } from '../../components/ui/EmptyState';
import { Card } from '../../components/ui/Card';
import { SearchInput } from '../../components/ui/SearchInput';
import { Skeleton } from '../../components/ui/Skeleton';
import { historyService } from '../../services/historyService';
import { teacherService } from '../../services/teacherService';
import { AuditEvent } from '../../types';

function todayISO() {
  return new Date().toISOString().split('T')[0];
}

const EVENT_CONFIG: Record<string, { Icon: typeof UserRound; bg: string; text: string }> = {
  ATTENDANCE_MARKED: { Icon: UserRound, bg: 'bg-primary/10', text: 'text-primary' },
  REQUIREMENT_CREATED: { Icon: ClipboardList, bg: 'bg-warning-bg', text: 'text-warning' },
  ASSIGNMENT_CREATED: { Icon: CheckCircle2, bg: 'bg-success-bg', text: 'text-success' },
  ASSIGNMENT_CANCELLED: { Icon: Undo2, bg: 'bg-not-marked-bg', text: 'text-not-marked' },
  ASSIGNMENT_COLLISION_PREVENTED: { Icon: TriangleAlert, bg: 'bg-error-bg', text: 'text-error' },
};

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

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
  const filteredTeachers = useMemo(() => {
    if (!teacherSearch) return [];
    const q = teacherSearch.toLowerCase();
    return teachers.filter((t) => t.name.toLowerCase().includes(q)).slice(0, 6);
  }, [teachers, teacherSearch]);

  const { data: events = [], isLoading, error } = useQuery<AuditEvent[]>({
    queryKey: ['history', date, teacherId],
    queryFn: () => historyService.getHistory(date, teacherId ?? undefined),
  });

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold tracking-tight">History &amp; Audit</h1>

      <div className="space-y-3">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="w-full h-11 min-h-[44px] px-3 rounded-lg border border-border bg-surface-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
        />

        {selectedTeacher ? (
          <div className="flex items-center justify-between px-3 py-2.5 rounded-lg bg-primary/10 border border-primary/20">
            <span className="text-sm font-medium text-primary">Filtered by: {selectedTeacher.name}</span>
            <button
              className="flex items-center gap-1 text-primary text-sm font-medium min-h-[44px]"
              onClick={() => {
                setTeacherId(null);
                setTeacherSearch('');
              }}
            >
              <X size={14} /> Clear
            </button>
          </div>
        ) : (
          <div className="relative">
            <SearchInput
              placeholder="Filter by teacher..."
              value={teacherSearch}
              onChange={(e) => setTeacherSearch(e.target.value)}
              onClear={() => setTeacherSearch('')}
            />
            {filteredTeachers.length > 0 && (
              <div className="absolute z-10 mt-1 w-full bg-surface-elevated border border-border rounded-xl shadow-lg overflow-hidden animate-fade-in">
                {filteredTeachers.map((t) => (
                  <div
                    key={t.id}
                    className="px-3 py-2.5 text-sm cursor-pointer hover:bg-surface active:bg-surface transition-colors"
                    onClick={() => {
                      setTeacherId(t.id);
                      setTeacherSearch('');
                    }}
                  >
                    {t.name}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} padding="sm" className="flex items-start gap-3">
              <Skeleton className="w-8 h-8 rounded-full shrink-0" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-3 w-24" />
              </div>
            </Card>
          ))}
        </div>
      )}
      {error && <div className="text-center py-8 text-error">Failed to load history. Please try again.</div>}

      {!isLoading && !error && events.length === 0 && (
        <div className="py-4">
          <EmptyState icon="🕒" title="No history found" description="No activity recorded for this date." />
        </div>
      )}

      <div className="space-y-2">
        {events.map((event, i) => {
          const isExpanded = expandedId === event.id;
          const config = EVENT_CONFIG[event.event_type] ?? { Icon: HistoryIcon, bg: 'bg-surface', text: 'text-text-muted' };
          const { Icon, bg, text } = config;
          return (
            <Card
              key={event.id}
              padding="sm"
              style={{ animationDelay: `${Math.min(i, 8) * 30}ms` }}
              className="cursor-pointer active:bg-surface transition-colors animate-fade-in"
              onClick={() => setExpandedId(isExpanded ? null : event.id)}
            >
              <div className="flex items-start gap-3">
                <span className={`flex items-center justify-center w-8 h-8 rounded-full shrink-0 ${bg}`}>
                  <Icon size={15} className={text} />
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium">{event.summary}</div>
                  <div className="text-xs text-text-secondary mt-0.5">
                    {formatTime(event.created_at)}
                    {event.actor_name && ` · ${event.actor_name}`}
                  </div>
                  {isExpanded && (
                    <pre className="text-xs text-text-muted mt-2 bg-surface rounded-lg p-2 overflow-x-auto">
                      {JSON.stringify(event.metadata, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

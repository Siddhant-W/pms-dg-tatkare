import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Coffee, RefreshCw } from 'lucide-react';
import { FilterChips } from '../../components/ui/FilterChips';
import { Card } from '../../components/ui/Card';
import { SearchInput } from '../../components/ui/SearchInput';
import { Avatar } from '../../components/ui/Avatar';
import { Skeleton } from '../../components/ui/Skeleton';
import { teacherService } from '../../services/teacherService';
import { timetableService } from '../../services/timetableService';
import { Weekday, TimetableEntry } from '../../types';

const DAYS: { label: string; value: Weekday }[] = [
  { label: 'Mon', value: 'MONDAY' },
  { label: 'Tue', value: 'TUESDAY' },
  { label: 'Wed', value: 'WEDNESDAY' },
  { label: 'Thu', value: 'THURSDAY' },
  { label: 'Fri', value: 'FRIDAY' },
  { label: 'Sat', value: 'SATURDAY' },
];

function todayISO() {
  return new Date().toISOString().split('T')[0];
}

function todayWeekday(): Weekday {
  const idx = new Date().getDay(); // 0=Sun ... 6=Sat
  const map: Weekday[] = ['SUNDAY' as Weekday, 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
  const day = map[idx];
  return DAYS.some((d) => d.value === day) ? day : 'MONDAY';
}

export function TimetablePage() {
  const [day, setDay] = useState<Weekday>(todayWeekday());
  const [teacherSearch, setTeacherSearch] = useState('');
  const [selectedTeacherId, setSelectedTeacherId] = useState<string | null>(null);

  const { data: teachers = [] } = useQuery({
    queryKey: ['teachers', todayISO()],
    queryFn: () => teacherService.getTeachers(todayISO()),
  });

  const selectedTeacher = teachers.find((t) => t.id === selectedTeacherId) ?? null;

  const filteredTeachers = useMemo(() => {
    if (!teacherSearch) return teachers;
    const q = teacherSearch.toLowerCase();
    return teachers.filter((t) => t.name.toLowerCase().includes(q));
  }, [teachers, teacherSearch]);

  const { data: entries = [], isLoading: entriesLoading } = useQuery<TimetableEntry[]>({
    queryKey: ['timetable', day, selectedTeacherId],
    queryFn: () => timetableService.getTimetable(day, selectedTeacherId!),
    enabled: !!selectedTeacherId,
  });

  const entryByPeriod = useMemo(() => {
    const map = new Map<number, TimetableEntry>();
    for (const e of entries) map.set(e.period_number, e);
    return map;
  }, [entries]);

  return (
    <div className="p-4 space-y-4">
      <FilterChips options={DAYS} value={day} onChange={(v) => setDay(v as Weekday)} />

      {!selectedTeacher ? (
        <div className="space-y-3">
          <SearchInput
            placeholder="Search teacher..."
            value={teacherSearch}
            onChange={(e) => setTeacherSearch(e.target.value)}
            onClear={() => setTeacherSearch('')}
          />
          <div className="space-y-2">
            {filteredTeachers.map((t, i) => (
              <div
                key={t.id}
                onClick={() => setSelectedTeacherId(t.id)}
                style={{ animationDelay: `${Math.min(i, 8) * 30}ms` }}
                className="flex items-center gap-3 p-3 bg-surface-elevated rounded-xl border border-border/80 shadow-sm cursor-pointer active:scale-[0.99] active:bg-surface transition-all animate-fade-in"
              >
                <Avatar name={t.name} />
                <div>
                  <div className="font-semibold">{t.name}</div>
                  {t.class_name && <div className="text-xs text-text-secondary">Class Teacher: {t.class_name}</div>}
                </div>
              </div>
            ))}
            {filteredTeachers.length === 0 && (
              <div className="text-center py-8 text-text-secondary text-sm">No teachers found.</div>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Avatar name={selectedTeacher.name} />
              <div>
                <div className="font-bold">{selectedTeacher.name}</div>
                {selectedTeacher.class_name && (
                  <div className="text-xs text-text-secondary">Class Teacher: {selectedTeacher.class_name}</div>
                )}
              </div>
            </div>
            <button
              className="flex items-center gap-1.5 text-primary text-sm font-medium px-3 py-2 min-h-[44px] rounded-lg active:bg-primary/10 transition-colors"
              onClick={() => setSelectedTeacherId(null)}
            >
              <RefreshCw size={14} /> Change
            </button>
          </div>

          {entriesLoading && (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Card key={i} className="flex items-center gap-4">
                  <Skeleton className="w-12 h-12 rounded-md shrink-0" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-3 w-16" />
                  </div>
                </Card>
              ))}
            </div>
          )}

          {!entriesLoading && (
            <div className="space-y-2.5">
              {Array.from({ length: 9 }, (_, i) => i + 1).map((periodNumber) => {
                const entry = entryByPeriod.get(periodNumber);
                const isFree = !entry || entry.is_free;
                return (
                  <div key={periodNumber} style={{ animationDelay: `${(periodNumber - 1) * 25}ms` }} className="animate-fade-in">
                    <Card className={`flex items-center gap-4 ${isFree ? 'bg-surface border-dashed shadow-none' : ''}`}>
                      <div
                        className={`w-11 h-11 flex items-center justify-center rounded-lg font-bold text-base shrink-0 ${
                          isFree ? 'bg-border-subtle text-text-muted' : 'bg-primary/10 text-primary'
                        }`}
                      >
                        {periodNumber}
                      </div>
                      {isFree ? (
                        <div className="font-medium text-text-muted">Free</div>
                      ) : (
                        <div className="min-w-0">
                          <div className="font-bold truncate">{entry.subject ?? 'Untitled'}</div>
                          {entry.class_name && <div className="text-sm text-text-secondary truncate">{entry.class_name}</div>}
                        </div>
                      )}
                    </Card>
                    {periodNumber === 5 && (
                      <div className="flex items-center gap-3 py-3">
                        <div className="flex-1 h-px bg-border" />
                        <span className="flex items-center gap-1.5 text-xs font-semibold text-text-muted uppercase tracking-wide">
                          <Coffee size={13} /> Recess &middot; 2:30 - 3:00 PM
                        </span>
                        <div className="flex-1 h-px bg-border" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

        </div>
      )}
    </div>
  );
}

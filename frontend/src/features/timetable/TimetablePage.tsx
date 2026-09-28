import { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Coffee, RefreshCw, Plus, Pencil, Check } from 'lucide-react';
import { FilterChips } from '../../components/ui/FilterChips';
import { Card } from '../../components/ui/Card';
import { SearchInput } from '../../components/ui/SearchInput';
import { Avatar } from '../../components/ui/Avatar';
import { Skeleton } from '../../components/ui/Skeleton';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
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

interface PeriodForm {
  subject: string;
  class_name: string;
  is_free: boolean;
  is_recess: boolean;
  time_start: string;
  time_end: string;
}

const BLANK_FORM: PeriodForm = { subject: '', class_name: '', is_free: false, is_recess: false, time_start: '', time_end: '' };

function formFromEntry(entry: TimetableEntry | undefined): PeriodForm {
  if (!entry) return BLANK_FORM;
  return {
    subject: entry.subject ?? '',
    class_name: entry.class_name ?? '',
    is_free: entry.is_free,
    is_recess: entry.is_recess,
    time_start: entry.time_start ?? '',
    time_end: entry.time_end ?? '',
  };
}

export function TimetablePage() {
  const [day, setDay] = useState<Weekday>(todayWeekday());
  const [teacherSearch, setTeacherSearch] = useState('');
  const [selectedTeacherId, setSelectedTeacherId] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editingPeriod, setEditingPeriod] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<PeriodForm>(BLANK_FORM);
  const [showAddTeacher, setShowAddTeacher] = useState(false);
  const [newTeacherName, setNewTeacherName] = useState('');
  const [newTeacherClass, setNewTeacherClass] = useState('');
  const queryClient = useQueryClient();

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

  const createTeacherMutation = useMutation({
    mutationFn: () => teacherService.createTeacher({ name: newTeacherName.trim(), class_name: newTeacherClass.trim() || null }),
    onSuccess: (teacher) => {
      queryClient.invalidateQueries({ queryKey: ['teachers'] });
      setShowAddTeacher(false);
      setNewTeacherName('');
      setNewTeacherClass('');
      // Jump straight into editing the new teacher's timetable - that's the
      // whole point of adding them.
      setSelectedTeacherId(teacher.id);
      setIsEditing(true);
    },
  });

  const savePeriodMutation = useMutation({
    mutationFn: () => {
      if (!selectedTeacherId || editingPeriod === null) throw new Error('No period selected');
      return timetableService.upsertEntry(selectedTeacherId, day, editingPeriod, {
        subject: editForm.is_free ? null : editForm.subject.trim() || null,
        class_name: editForm.is_free ? null : editForm.class_name.trim() || null,
        is_free: editForm.is_free,
        is_recess: editForm.is_recess,
        time_start: editForm.time_start || null,
        time_end: editForm.time_end || null,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timetable', day, selectedTeacherId] });
      setEditingPeriod(null);
    },
  });

  const openPeriodEditor = (periodNumber: number) => {
    setEditForm(formFromEntry(entryByPeriod.get(periodNumber)));
    setEditingPeriod(periodNumber);
  };

  return (
    <div className="p-4 space-y-4">
      <FilterChips options={DAYS} value={day} onChange={(v) => setDay(v as Weekday)} />

      {!selectedTeacher ? (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="flex-1 min-w-0">
              <SearchInput
                placeholder="Search teacher..."
                value={teacherSearch}
                onChange={(e) => setTeacherSearch(e.target.value)}
                onClear={() => setTeacherSearch('')}
              />
            </div>
            <Button size="md" className="gap-1.5 shrink-0" onClick={() => setShowAddTeacher(true)}>
              <Plus size={18} /> Add Teacher
            </Button>
          </div>
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
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-3 min-w-0">
              <Avatar name={selectedTeacher.name} />
              <div className="min-w-0">
                <div className="font-bold truncate">{selectedTeacher.name}</div>
                {selectedTeacher.class_name && (
                  <div className="text-xs text-text-secondary truncate">Class Teacher: {selectedTeacher.class_name}</div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              <Button
                size="sm"
                variant={isEditing ? 'primary' : 'ghost'}
                className="gap-1.5"
                onClick={() => setIsEditing((v) => !v)}
              >
                {isEditing ? <Check size={14} /> : <Pencil size={14} />}
                {isEditing ? 'Done' : 'Edit Timetable'}
              </Button>
              <button
                className="flex items-center gap-1.5 text-primary text-sm font-medium px-3 py-2 min-h-[44px] rounded-lg active:bg-primary/10 transition-colors"
                onClick={() => {
                  setSelectedTeacherId(null);
                  setIsEditing(false);
                }}
              >
                <RefreshCw size={14} /> Change
              </button>
            </div>
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
                    <Card
                      onClick={isEditing ? () => openPeriodEditor(periodNumber) : undefined}
                      className={`flex items-center gap-4 ${isFree ? 'bg-surface border-dashed shadow-none' : ''} ${
                        isEditing ? 'cursor-pointer active:scale-[0.99] transition-transform ring-1 ring-border' : ''
                      }`}
                    >
                      <div
                        className={`w-11 h-11 flex items-center justify-center rounded-lg font-bold text-base shrink-0 ${
                          isFree ? 'bg-border-subtle text-text-muted' : 'bg-primary/10 text-primary'
                        }`}
                      >
                        {periodNumber}
                      </div>
                      {isFree ? (
                        <div className="font-medium text-text-muted flex-1">Free</div>
                      ) : (
                        <div className="min-w-0 flex-1">
                          <div className="font-bold truncate">{entry.subject ?? 'Untitled'}</div>
                          {entry.class_name && <div className="text-sm text-text-secondary truncate">{entry.class_name}</div>}
                        </div>
                      )}
                      {isEditing && <Pencil size={15} className="text-text-muted shrink-0" />}
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

      <Modal isOpen={showAddTeacher} onClose={() => setShowAddTeacher(false)} title="Add Teacher">
        <div className="flex flex-col gap-3">
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Name</label>
            <input
              type="text"
              value={newTeacherName}
              onChange={(e) => setNewTeacherName(e.target.value)}
              placeholder="e.g. Mrs. S. M. Deshmukh"
              className="w-full px-4 py-3 min-h-[44px] rounded-md border border-border bg-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1">Class Teacher Of (optional)</label>
            <input
              type="text"
              value={newTeacherClass}
              onChange={(e) => setNewTeacherClass(e.target.value)}
              placeholder="e.g. Class IX-2"
              className="w-full px-4 py-3 min-h-[44px] rounded-md border border-border bg-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent text-sm"
            />
          </div>
          <Button
            onClick={() => createTeacherMutation.mutate()}
            disabled={!newTeacherName.trim() || createTeacherMutation.isPending}
          >
            {createTeacherMutation.isPending ? 'Adding...' : 'Add Teacher'}
          </Button>
          {createTeacherMutation.isError && (
            <p className="text-xs text-error text-center">Failed to add teacher. Please try again.</p>
          )}
        </div>
      </Modal>

      <Modal isOpen={editingPeriod !== null} onClose={() => setEditingPeriod(null)} title={`Period ${editingPeriod ?? ''}`}>
        <div className="flex flex-col gap-3">
          <div className="flex gap-4">
            <label className="flex items-center gap-2 text-sm font-medium">
              <input
                type="checkbox"
                checked={editForm.is_free}
                onChange={(e) => setEditForm((f) => ({ ...f, is_free: e.target.checked, is_recess: e.target.checked ? false : f.is_recess }))}
              />
              Free Period
            </label>
            <label className="flex items-center gap-2 text-sm font-medium">
              <input
                type="checkbox"
                checked={editForm.is_recess}
                onChange={(e) => setEditForm((f) => ({ ...f, is_recess: e.target.checked, is_free: e.target.checked ? false : f.is_free }))}
              />
              Recess
            </label>
          </div>
          {!editForm.is_free && !editForm.is_recess && (
            <>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Subject</label>
                <input
                  type="text"
                  value={editForm.subject}
                  onChange={(e) => setEditForm((f) => ({ ...f, subject: e.target.value }))}
                  className="w-full px-4 py-3 min-h-[44px] rounded-md border border-border bg-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Class</label>
                <input
                  type="text"
                  value={editForm.class_name}
                  onChange={(e) => setEditForm((f) => ({ ...f, class_name: e.target.value }))}
                  className="w-full px-4 py-3 min-h-[44px] rounded-md border border-border bg-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent text-sm"
                />
              </div>
            </>
          )}
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-xs font-medium text-text-secondary mb-1">Start Time</label>
              <input
                type="time"
                value={editForm.time_start}
                onChange={(e) => setEditForm((f) => ({ ...f, time_start: e.target.value }))}
                className="w-full px-3 py-3 min-h-[44px] rounded-md border border-border bg-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent text-sm"
              />
            </div>
            <div className="flex-1">
              <label className="block text-xs font-medium text-text-secondary mb-1">End Time</label>
              <input
                type="time"
                value={editForm.time_end}
                onChange={(e) => setEditForm((f) => ({ ...f, time_end: e.target.value }))}
                className="w-full px-3 py-3 min-h-[44px] rounded-md border border-border bg-bg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent text-sm"
              />
            </div>
          </div>
          <Button onClick={() => savePeriodMutation.mutate()} disabled={savePeriodMutation.isPending}>
            {savePeriodMutation.isPending ? 'Saving...' : 'Save'}
          </Button>
          {savePeriodMutation.isError && (
            <p className="text-xs text-error text-center">Failed to save. Please try again.</p>
          )}
        </div>
      </Modal>
    </div>
  );
}

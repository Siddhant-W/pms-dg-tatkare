import { useMemo, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X as XIcon } from 'lucide-react';
import { SearchInput } from '../../components/ui/SearchInput';
import { FilterChips } from '../../components/ui/FilterChips';
import { TeacherWithAttendance, AttendanceStatus } from '../../types';
import { Avatar } from '../../components/ui/Avatar';
import { StatusPill } from '../../components/ui/StatusPill';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { attendanceService } from '../../services/attendanceService';
import { useRecentSearches } from '../../hooks/useRecentSearches';

function todayISO() {
  return new Date().toISOString().split('T')[0];
}

export function AttendancePage() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('ALL');
  const [selectedTeacher, setSelectedTeacher] = useState<TeacherWithAttendance | null>(null);
  const queryClient = useQueryClient();
  const today = todayISO();
  const { recent, addRecent, clearRecent } = useRecentSearches();

  const filters = [
    { label: 'All', value: 'ALL' },
    { label: 'Not Marked', value: 'NOT_MARKED' },
    { label: 'Present', value: 'PRESENT' },
    { label: 'Absent', value: 'ABSENT' }
  ];

  const { data: teachers = [], isLoading, error } = useQuery({
    queryKey: ['teachers', today],
    queryFn: () => attendanceService.getTeachersWithAttendance(today),
  });

  const mutation = useMutation({
    mutationFn: ({ teacherId, status }: { teacherId: string; status: AttendanceStatus }) =>
      attendanceService.markAttendance(teacherId, today, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teachers', today] });
      queryClient.invalidateQueries({ queryKey: ['attendance-summary', today] });
      queryClient.invalidateQueries({ queryKey: ['proxy-requirements', today] });
      // A candidate list already open elsewhere is now stale - this teacher may
      // have just become available (or unavailable) for any pending period.
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      setSelectedTeacher(null);
    },
  });

  const filtered = useMemo(() => {
    return teachers.filter(t => {
      const matchSearch = t.name.toLowerCase().includes(search.toLowerCase());
      const matchFilter = filter === 'ALL' || t.attendance_status === filter;
      return matchSearch && matchFilter;
    });
  }, [teachers, search, filter]);

  const handleMark = (status: AttendanceStatus) => {
    if (selectedTeacher) {
      mutation.mutate({ teacherId: selectedTeacher.id, status });
    }
  };

  const handleSelectTeacher = (t: TeacherWithAttendance) => {
    if (search.trim()) addRecent(search.trim());
    setSelectedTeacher(t);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 pb-3 space-y-3 sticky top-0 bg-bg/95 backdrop-blur-md z-10 border-b border-border">
        <SearchInput placeholder="Search teachers..." value={search} onChange={e => setSearch(e.target.value)} onClear={() => setSearch('')} />
        <FilterChips options={filters} value={filter} onChange={setFilter} />
        {!search && recent.length > 0 && (
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar">
            <span className="text-xs text-text-secondary shrink-0">Recent:</span>
            {recent.map((term) => (
              <button
                key={term}
                onClick={() => setSearch(term)}
                className="whitespace-nowrap px-3 h-7 rounded-full text-xs font-medium bg-surface text-text-secondary hover:bg-border-subtle transition-colors shrink-0"
              >
                {term}
              </button>
            ))}
            <button onClick={clearRecent} className="flex items-center gap-0.5 text-xs text-text-muted shrink-0 ml-1">
              <XIcon size={12} /> Clear
            </button>
          </div>
        )}
      </div>

      <div className="p-4 space-y-2">
        {isLoading && (
          <div className="space-y-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-surface-elevated rounded-xl border border-border/80">
                <div className="flex items-center gap-3">
                  <Skeleton className="w-10 h-10 rounded-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                </div>
                <Skeleton className="h-6 w-20 rounded-full" />
              </div>
            ))}
          </div>
        )}
        {error && (
          <div className="text-center py-8 text-error">Failed to load teachers. Please try again.</div>
        )}
        {!isLoading && filtered.length === 0 && (
          <div className="text-center py-8 text-text-secondary">No teachers found.</div>
        )}
        {filtered.map((t, i) => (
          <div
            key={t.id}
            onClick={() => handleSelectTeacher(t)}
            style={{ animationDelay: `${Math.min(i, 8) * 30}ms` }}
            className="flex items-center justify-between p-3 bg-surface-elevated rounded-xl shadow-sm border border-border/80 cursor-pointer active:scale-[0.99] active:bg-surface transition-all animate-fade-in"
          >
            <div className="flex items-center gap-3 min-w-0">
              <Avatar name={t.name} />
              <div className="min-w-0">
                <div className="font-semibold truncate">{t.name}</div>
                {t.class_name && <div className="text-xs text-text-secondary truncate">Class Teacher: {t.class_name}</div>}
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <StatusPill status={t.attendance_status} />
            </div>
          </div>
        ))}
      </div>

      <Modal isOpen={!!selectedTeacher} onClose={() => setSelectedTeacher(null)} title={selectedTeacher?.name || ''}>
        <div className="flex flex-col gap-3">
          <p className="text-sm text-text-secondary mb-1">
            Current status: <span className="font-medium">{selectedTeacher?.attendance_status}</span>
          </p>
          <Button
            variant="primary"
            className="bg-success hover:bg-success/90"
            onClick={() => handleMark('PRESENT')}
            disabled={mutation.isPending}
          >
            Mark Present
          </Button>
          <Button
            variant="destructive"
            onClick={() => handleMark('ABSENT')}
            disabled={mutation.isPending}
          >
            Mark Absent
          </Button>
          <Button variant="ghost" onClick={() => setSelectedTeacher(null)} disabled={mutation.isPending}>
            Cancel
          </Button>
          {mutation.isError && (
            <p className="text-xs text-error text-center">Failed to update. Please try again.</p>
          )}
        </div>
      </Modal>
    </div>
  );
}

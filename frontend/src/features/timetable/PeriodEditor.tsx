import { useEffect, useRef, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { TriangleAlert } from 'lucide-react';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
import { Field, Input, Select } from '../../components/ui/Field';
import { timetableService } from '../../services/timetableService';
import { ApiError, parseApiError } from '../../lib/errors';
import { cn } from '../../lib/utils';
import { Teacher, TimetableEntry, Weekday } from '../../types';
import { DAYS, DAY_NAMES, PERIODS, trimTime } from './shared';

type Kind = 'lesson' | 'free' | 'recess';

interface FormState {
  teacherId: string;
  weekday: Weekday;
  period: number;
  kind: Kind;
  subject: string;
  className: string;
  timeStart: string;
  timeEnd: string;
}

export interface EditorTarget {
  teacherId: string;
  weekday: Weekday;
  period: number;
  entry?: TimetableEntry;
}

function initialForm(t: EditorTarget): FormState {
  const e = t.entry;
  return {
    teacherId: t.teacherId,
    weekday: t.weekday,
    period: t.period,
    // Tapping an empty slot almost always means "put a lesson here".
    kind: e?.is_recess ? 'recess' : 'lesson',
    subject: e?.subject ?? '',
    className: e?.class_name ?? '',
    timeStart: trimTime(e?.time_start),
    timeEnd: trimTime(e?.time_end),
  };
}

// Which backend field each form control reports errors under.
const FIELD_FOR_CONTROL: Record<string, string[]> = {
  teacher: ['teacher_id'],
  period: ['period_number'],
  kind: ['is_free', 'is_recess'],
  subject: ['subject'],
  class: ['class_name'],
  time: ['time_start', 'time_end'],
};

export function PeriodEditor({
  target,
  teachers,
  onClose,
  onRequestClear,
}: {
  target: EditorTarget | null;
  teachers: Teacher[];
  onClose: () => void;
  onRequestClear: (entry: TimetableEntry) => void;
}) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<FormState | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const noticeRef = useRef<HTMLDivElement>(null);

  // The warning and its "Save anyway" button sit at the bottom of a scrolling sheet.
  useEffect(() => {
    if (error?.code) noticeRef.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [error]);

  useEffect(() => {
    setForm(target ? initialForm(target) : null);
    setError(null);
  }, [target]);

  const save = useMutation({
    mutationFn: ({ allowOverlap }: { allowOverlap: boolean }) => {
      if (!form || !target) throw new Error('Nothing to save');
      const lesson = form.kind === 'lesson';
      const payload = {
        subject: lesson ? form.subject.trim() || null : null,
        class_name: lesson ? form.className.trim() || null : null,
        is_free: form.kind === 'free',
        is_recess: form.kind === 'recess',
        time_start: form.timeStart || null,
        time_end: form.timeEnd || null,
      };
      if (target.entry) {
        // Existing entry: edit in place, or move it if teacher/day/period changed.
        return timetableService.updateEntry(
          target.entry.id,
          { ...payload, teacher_id: form.teacherId, weekday: form.weekday, period_number: form.period },
          allowOverlap
        );
      }
      return timetableService.upsertEntry(form.teacherId, form.weekday, form.period, payload, allowOverlap);
    },
    onSuccess: () => {
      toast.success('Timetable updated');
      queryClient.invalidateQueries({ queryKey: ['timetable'] });
      onClose();
    },
    onError: (err) => setError(parseApiError(err, "Couldn't save this period.")),
  });

  if (!form || !target) return <Modal isOpen={false} onClose={onClose} title="Edit period">{null}</Modal>;

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((f) => (f ? { ...f, [key]: value } : f));
    setError(null);
  };
  const fieldError = (control: string) => {
    for (const name of FIELD_FOR_CONTROL[control]) if (error?.fieldErrors[name]) return error.fieldErrors[name];
    return undefined;
  };

  const teacher = teachers.find((t) => t.id === form.teacherId);
  const moved = !!target.entry && (form.teacherId !== target.teacherId || form.weekday !== target.weekday || form.period !== target.period);
  const overlap = error?.code === 'class_overlap';
  const occupied = error?.code === 'slot_occupied';
  // Anything the user should read that isn't attached to a specific control.
  const generalError = error && !overlap && Object.keys(error.fieldErrors).length === 0 ? error.message : null;

  return (
    <Modal
      isOpen
      onClose={onClose}
      title={target.entry ? 'Edit period' : 'Add a period'}
      description={`${teacher?.name ?? 'Teacher'} · ${DAY_NAMES[form.weekday]} · Period ${form.period}`}
    >
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          save.mutate({ allowOverlap: false });
        }}
        noValidate
      >
        <div role="radiogroup" aria-label="Period type" className="grid grid-cols-3 gap-1 rounded-lg bg-surface p-1">
          {(['lesson', 'free', 'recess'] as Kind[]).map((k) => (
            <button
              key={k}
              type="button"
              role="radio"
              aria-checked={form.kind === k}
              onClick={() => set('kind', k)}
              className={cn(
                'h-10 rounded-md text-sm font-semibold capitalize transition-colors',
                form.kind === k ? 'bg-primary text-white shadow-sm' : 'text-text-secondary hover:text-text-primary'
              )}
            >
              {k}
            </button>
          ))}
        </div>
        {fieldError('kind') && <p role="alert" className="text-xs font-medium text-error">{fieldError('kind')}</p>}

        {form.kind === 'lesson' && (
          <>
            <Field label="Subject" error={fieldError('subject')}>
              {(p) => <Input {...p} value={form.subject} onChange={(e) => set('subject', e.target.value)} placeholder="e.g. Mathematics" maxLength={60} autoComplete="off" />}
            </Field>
            <Field label="Class" error={fieldError('class')} hint="Like 6-I, 8-II or 10-I.">
              {(p) => <Input {...p} value={form.className} onChange={(e) => set('className', e.target.value)} placeholder="e.g. 6-I" autoComplete="off" />}
            </Field>
          </>
        )}

        <fieldset className="space-y-3 rounded-xl border border-border p-3">
          <legend className="px-1 text-xs font-bold uppercase tracking-wide text-text-muted">Teacher & slot</legend>
          <Field label="Teacher" error={fieldError('teacher')}>
            {(p) => (
              <Select {...p} value={form.teacherId} onChange={(e) => set('teacherId', e.target.value)}>
                {teachers.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
              </Select>
            )}
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Day">
              {(p) => (
                <Select {...p} value={form.weekday} onChange={(e) => set('weekday', e.target.value as Weekday)}>
                  {DAYS.map((d) => <option key={d.value} value={d.value}>{DAY_NAMES[d.value]}</option>)}
                </Select>
              )}
            </Field>
            <Field label="Period" error={fieldError('period')}>
              {(p) => (
                <Select {...p} value={form.period} onChange={(e) => set('period', Number(e.target.value))}>
                  {PERIODS.map((n) => <option key={n} value={n}>Period {n}</option>)}
                </Select>
              )}
            </Field>
          </div>
          {moved && <p className="text-xs text-text-secondary">This moves the lesson. The slot it leaves becomes a free period.</p>}
        </fieldset>

        <div className="grid grid-cols-2 gap-3">
          <Field label="Starts" optional error={fieldError('time')}>
            {(p) => <Input {...p} type="time" value={form.timeStart} onChange={(e) => set('timeStart', e.target.value)} />}
          </Field>
          <Field label="Ends" optional>
            {(p) => <Input {...p} type="time" value={form.timeEnd} onChange={(e) => set('timeEnd', e.target.value)} />}
          </Field>
        </div>

        {occupied && (
          <div ref={noticeRef} role="alert" className="flex gap-2 rounded-xl border border-error/30 bg-error-bg p-3 text-sm text-error">
            <TriangleAlert size={16} className="mt-0.5 shrink-0" aria-hidden />
            <p>{error?.message} Pick another slot, or clear the lesson there first.</p>
          </div>
        )}

        {overlap && (
          <div ref={noticeRef} role="alert" className="space-y-2 rounded-xl border border-warning/40 bg-warning-bg p-3 text-sm">
            <p className="flex gap-2 font-semibold text-text-primary">
              <TriangleAlert size={16} className="mt-0.5 shrink-0 text-warning" aria-hidden /> {error?.message}
            </p>
            {error!.conflicts.length > 0 && (
              <ul className="list-disc space-y-0.5 pl-9 text-text-secondary">
                {error!.conflicts.map((c, i) => (
                  <li key={i}>{c.teacher_name ?? 'Another teacher'}{c.subject ? ` · ${c.subject}` : ''}</li>
                ))}
              </ul>
            )}
            <p className="pl-6 text-text-secondary">Two teachers in one class is sometimes intended (split groups, labs). Save only if it is.</p>
            <Button size="sm" variant="secondary" className="ml-6" isLoading={save.isPending} onClick={() => save.mutate({ allowOverlap: true })}>
              Save anyway
            </Button>
          </div>
        )}

        {generalError && <p role="alert" className="text-sm font-medium text-error">{generalError}</p>}

        <div className="flex flex-col-reverse gap-2 pt-1 sm:flex-row sm:items-center sm:justify-between">
          {target.entry && !target.entry.is_free ? (
            <Button variant="ghost" className="text-error hover:bg-error-bg" onClick={() => onRequestClear(target.entry!)}>
              Clear this period
            </Button>
          ) : <span />}
          <div className="flex flex-col-reverse gap-2 sm:flex-row">
            <Button variant="ghost" onClick={onClose}>Cancel</Button>
            <Button type="submit" isLoading={save.isPending && !overlap}>Save</Button>
          </div>
        </div>
      </form>
    </Modal>
  );
}

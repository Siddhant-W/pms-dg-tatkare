import { useEffect, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
import { Field, Input } from '../../components/ui/Field';
import { teacherService } from '../../services/teacherService';
import { ApiError, parseApiError } from '../../lib/errors';
import { Teacher } from '../../types';

/** Add a teacher (`teacher === null`) or edit one. Pass `isOpen=false` to hide. */
export function TeacherEditor({
  isOpen,
  teacher,
  onClose,
  onCreated,
}: {
  isOpen: boolean;
  teacher: Teacher | null;
  onClose: () => void;
  onCreated?: (t: Teacher) => void;
}) {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [className, setClassName] = useState('');
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (isOpen) {
      setName(teacher?.name ?? '');
      setClassName(teacher?.class_name ?? '');
      setError(null);
    }
  }, [isOpen, teacher]);

  const save = useMutation({
    mutationFn: () => {
      const input = { name: name.trim(), class_name: className.trim() || null };
      return teacher ? teacherService.updateTeacher(teacher.id, input) : teacherService.createTeacher(input);
    },
    onSuccess: (saved) => {
      toast.success(teacher ? 'Teacher updated' : `${saved.name} added`);
      queryClient.invalidateQueries({ queryKey: ['teachers'] });
      if (!teacher) onCreated?.(saved);
      onClose();
    },
    onError: (err) => setError(parseApiError(err, "Couldn't save this teacher.")),
  });

  const general = error && Object.keys(error.fieldErrors).length === 0 ? error.message : null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={teacher ? 'Edit teacher' : 'Add teacher'}>
      <form
        className="space-y-4"
        noValidate
        onSubmit={(e) => {
          e.preventDefault();
          if (!name.trim()) return setError({ message: '', fieldErrors: { name: "Enter the teacher's name." }, conflicts: [], isNetworkError: false });
          save.mutate();
        }}
      >
        <Field label="Name" error={error?.fieldErrors.name}>
          {(p) => <Input {...p} value={name} onChange={(e) => { setName(e.target.value); setError(null); }} placeholder="e.g. Mrs. S. M. Deshmukh" maxLength={80} autoComplete="off" />}
        </Field>
        <Field label="Class teacher of" optional error={error?.fieldErrors.class_name} hint="Like 6-I or Class VIII-2. Leave empty for a subject teacher.">
          {(p) => <Input {...p} value={className} onChange={(e) => { setClassName(e.target.value); setError(null); }} placeholder="e.g. 9-II" autoComplete="off" />}
        </Field>
        {general && <p role="alert" className="text-sm font-medium text-error">{general}</p>}
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" isLoading={save.isPending}>{teacher ? 'Save changes' : 'Add teacher'}</Button>
        </div>
      </form>
    </Modal>
  );
}

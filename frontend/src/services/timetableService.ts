import { api } from '../lib/api';
import { TimetableEntry, Weekday } from '../types';

export interface TimetableEntryInput {
  subject: string | null;
  class_name: string | null;
  is_recess: boolean;
  is_free: boolean;
  time_start: string | null;
  time_end: string | null;
}

export type TimetableEntryPatch = Partial<TimetableEntryInput> & {
  teacher_id?: string;
  weekday?: Weekday;
  period_number?: number;
};

export const timetableService = {
  getTimetable: async (day: string, teacherId?: string): Promise<TimetableEntry[]> => {
    const { data } = await api.get(`/timetable`, { params: { day, teacher_id: teacherId } });
    return data;
  },
  // Create or replace the lesson in one teacher/day/period slot (admin only).
  upsertEntry: async (
    teacherId: string,
    weekday: Weekday,
    periodNumber: number,
    input: TimetableEntryInput,
    allowClassOverlap = false
  ) => {
    const { data } = await api.put<TimetableEntry>(`/timetable/${teacherId}/${weekday}/${periodNumber}`, input, {
      params: allowClassOverlap ? { allow_class_overlap: true } : undefined,
    });
    return data;
  },
  // Edit or move an existing entry (admin only).
  updateEntry: async (entryId: string, patch: TimetableEntryPatch, allowClassOverlap = false) => {
    const { data } = await api.put<TimetableEntry>(`/timetable/entries/${entryId}`, patch, {
      params: allowClassOverlap ? { allow_class_overlap: true } : undefined,
    });
    return data;
  },
  // Empty a slot (admin only).
  clearEntry: async (entryId: string) => {
    await api.delete(`/timetable/entries/${entryId}`);
  },
};

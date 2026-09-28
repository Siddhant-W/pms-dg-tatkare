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

export const timetableService = {
  getTimetable: async (day: string, teacherId?: string) => {
    const { data } = await api.get(`/timetable`, { params: { day, teacher_id: teacherId } });
    return data;
  },
  upsertEntry: async (teacherId: string, weekday: Weekday, periodNumber: number, input: TimetableEntryInput) => {
    const { data } = await api.put<TimetableEntry>(`/timetable/${teacherId}/${weekday}/${periodNumber}`, input);
    return data;
  },
};

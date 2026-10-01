import { api } from '../lib/api';
import { Teacher, TeacherWithAttendance, TimetableEntry } from '../types';

export const teacherService = {
  getTeachers: async (date: string, includeInactive = false) => {
    const { data } = await api.get<TeacherWithAttendance[]>(`/teachers`, {
      params: { date, include_inactive: includeInactive || undefined },
    });
    return data;
  },
  getTeacherTimetable: async (teacherId: string, day: string) => {
    const { data } = await api.get<TimetableEntry[]>(`/teachers/${teacherId}/timetable`, { params: { day } });
    return data;
  },
  createTeacher: async (input: { name: string; class_name?: string | null }) => {
    const { data } = await api.post<Teacher>('/teachers', input);
    return data;
  },
  updateTeacher: async (teacherId: string, input: { name?: string; class_name?: string | null; active?: boolean }) => {
    const { data } = await api.put<Teacher>(`/teachers/${teacherId}`, input);
    return data;
  },
};

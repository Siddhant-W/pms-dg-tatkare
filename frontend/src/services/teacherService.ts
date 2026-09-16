import { api } from '../lib/api';
import { TeacherWithAttendance, TimetableEntry } from '../types';

export const teacherService = {
  getTeachers: async (date: string) => {
    const { data } = await api.get<TeacherWithAttendance[]>(`/teachers`, { params: { date } });
    return data;
  },
  getTeacherTimetable: async (teacherId: string, day: string) => {
    const { data } = await api.get<TimetableEntry[]>(`/teachers/${teacherId}/timetable`, { params: { day } });
    return data;
  }
};

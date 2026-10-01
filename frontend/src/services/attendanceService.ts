import { api } from '../lib/api';
import { AttendanceStatus, AttendanceSummary, ResetAllResult, TeacherWithAttendance } from '../types';

export const attendanceService = {
  // Get all teachers with their attendance status for a given date
  getTeachersWithAttendance: async (date: string): Promise<TeacherWithAttendance[]> => {
    const { data } = await api.get('/teachers', { params: { date } });
    return data;
  },

  // Get summary counts for a date
  getAttendanceSummary: async (date: string): Promise<AttendanceSummary> => {
    const { data } = await api.get('/attendance/summary', { params: { date } });
    return data;
  },

  // Mark a teacher's attendance for a specific date
  markAttendance: async (teacherId: string, date: string, status: AttendanceStatus) => {
    const { data } = await api.put(`/attendance/${teacherId}`, { status }, { params: { date } });
    return data;
  },

  // Clear a teacher's attendance for a specific date back to NOT_MARKED
  resetAttendance: async (teacherId: string, date: string) => {
    await api.delete(`/attendance/${teacherId}`, { params: { date } });
  },

  // "Mark all present": clears every absence for the date (and the proxy work that hung off them).
  resetAll: async (date: string): Promise<ResetAllResult> => {
    const { data } = await api.delete('/attendance', { params: { date } });
    return data;
  },
};

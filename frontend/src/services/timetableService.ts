import { api } from '../lib/api';

export const timetableService = {
  getTimetable: async (day: string, teacherId?: string) => {
    const { data } = await api.get(`/timetable`, { params: { day, teacher_id: teacherId } });
    return data;
  }
};

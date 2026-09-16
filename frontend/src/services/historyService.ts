import { api } from '../lib/api';

export const historyService = {
  getHistory: async (date?: string, teacherId?: string) => {
    const { data } = await api.get(`/history`, { params: { date, teacher_id: teacherId } });
    return data;
  }
};

import { api } from '../lib/api';

export const analyticsService = {
  getDailyStats: async (date: string) => {
    const { data } = await api.get(`/analytics`, { params: { date } });
    return data;
  }
};

import { api } from '../lib/api';
import { FavoriteTeacher } from '../types';

export const favoritesService = {
  getFavorites: async (): Promise<FavoriteTeacher[]> => {
    const { data } = await api.get('/favorites');
    return data;
  },
  addFavorite: async (teacherId: string) => {
    await api.post(`/favorites/${teacherId}`);
  },
  removeFavorite: async (teacherId: string) => {
    await api.delete(`/favorites/${teacherId}`);
  },
};

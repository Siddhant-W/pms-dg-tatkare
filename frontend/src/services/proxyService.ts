import { api } from '../lib/api';

export const proxyService = {
  // Get all proxy requirements for a date
  getProxyRequirements: async (date: string) => {
    const { data } = await api.get('/proxy-requirements', { params: { date } });
    return data;
  },

  // Get available candidates for a specific requirement
  getCandidates: async (requirementId: string) => {
    const { data } = await api.get(`/proxy-requirements/${requirementId}/candidates`);
    return data;
  },

  // Assign a proxy teacher to a requirement
  assignProxy: async (requirementId: string, proxyTeacherId: string) => {
    const { data } = await api.post('/proxy-assignments', {
      requirement_id: requirementId,
      proxy_teacher_id: proxyTeacherId,
    });
    return data;
  },

  // Cancel an existing assignment
  cancelAssignment: async (assignmentId: string) => {
    const { data } = await api.delete(`/proxy-assignments/${assignmentId}`);
    return data;
  },
};

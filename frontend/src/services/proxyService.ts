import { api } from '../lib/api';
import { ProxyAssignmentDetail, ProxyCandidate, ProxyRequirement } from '../types';

export const proxyService = {
  // Get all proxy requirements for a date
  getProxyRequirements: async (date: string): Promise<ProxyRequirement[]> => {
    const { data } = await api.get('/proxy-requirements', { params: { date } });
    return data;
  },

  getRequirement: async (requirementId: string): Promise<ProxyRequirement> => {
    const { data } = await api.get(`/proxy-requirements/${requirementId}`);
    return data;
  },

  // Available candidates for a requirement, best first
  getCandidates: async (requirementId: string): Promise<ProxyCandidate[]> => {
    const { data } = await api.get(`/proxy-requirements/${requirementId}/candidates`);
    return data;
  },

  // Everything the Assigned Proxies page lists for a date
  getAssignments: async (date: string, status: 'ASSIGNED' | 'CANCELLED' | 'ALL' = 'ALL'): Promise<ProxyAssignmentDetail[]> => {
    const { data } = await api.get('/proxy-assignments', { params: { date, status } });
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

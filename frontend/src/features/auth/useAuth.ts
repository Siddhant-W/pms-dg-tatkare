import { create } from 'zustand';
import {
  api,
  clearAccessToken,
  requestRefresh,
  setAccessToken,
  setUnauthorizedHandler,
} from '../../lib/api';

export interface Supervisor {
  id: string;
  username: string;
  full_name: string | null;
  role: 'ADMIN' | 'SUPERVISOR';
}

/**
 * 'checking' is the initial state while we attempt a silent refresh. Without
 * it, ProtectedRoute would bounce an authenticated user to /login on every
 * page reload, because the access token lives in memory only.
 */
export type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated';

interface AuthState {
  status: AuthStatus;
  user: Supervisor | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  bootstrap: () => Promise<void>;
  setAuthenticated: (value: boolean) => void;
}

export const useAuth = create<AuthState>((set) => ({
  status: 'checking',
  user: null,
  isAuthenticated: false,

  login: async (username, password) => {
    const { data } = await api.post('/auth/login', { username, password });
    if (!data?.access_token) {
      throw new Error('Login response did not contain an access token');
    }
    setAccessToken(data.access_token);
    set({ status: 'authenticated', isAuthenticated: true, user: data.user ?? null });
  },

  logout: async () => {
    try {
      // Clears the HttpOnly refresh cookie server-side; without this the next
      // silent refresh would sign the user straight back in.
      await api.post('/auth/logout');
    } catch {
      // Logging out locally must succeed even if the network call fails.
    }
    clearAccessToken();
    set({ status: 'unauthenticated', isAuthenticated: false, user: null });
  },

  bootstrap: async () => {
    try {
      await requestRefresh();
      const { data } = await api.get('/auth/me');
      set({ status: 'authenticated', isAuthenticated: true, user: data ?? null });
    } catch {
      clearAccessToken();
      set({ status: 'unauthenticated', isAuthenticated: false, user: null });
    }
  },

  // Kept for backwards compatibility with existing callers.
  setAuthenticated: (value) =>
    set((state) => ({
      status: value ? 'authenticated' : 'unauthenticated',
      isAuthenticated: value,
      user: value ? state.user : null,
    })),
}));

// When a refresh fails mid-session, drop straight back to the login screen.
setUnauthorizedHandler(() => {
  useAuth.setState({ status: 'unauthenticated', isAuthenticated: false, user: null });
});

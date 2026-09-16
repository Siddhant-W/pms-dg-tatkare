import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

/**
 * Access token lives in memory only. The refresh token is an HttpOnly cookie
 * managed by the backend, so `withCredentials` must be enabled for every
 * request that can hit /auth/refresh.
 */
let accessToken = '';

export const setAccessToken = (token: string) => {
  accessToken = token;
};

export const getAccessToken = () => accessToken;

export const clearAccessToken = () => {
  accessToken = '';
};

// Called when the session is definitively gone, so the auth store can react
// without api.ts importing the store (avoids a circular import).
let onUnauthorized: (() => void) | null = null;
export const setUnauthorizedHandler = (handler: () => void) => {
  onUnauthorized = handler;
};

// Defaults to a relative path so the Vite dev proxy handles it as same-origin
// (no CORS, cookies just work). Override with VITE_API_URL when the API is
// deployed on a different host.
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

/** Bare client for /auth/refresh so it never re-enters the interceptor. */
const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export async function requestRefresh(): Promise<string> {
  const { data } = await refreshClient.post('/auth/refresh');
  // The backend returns snake_case `access_token`.
  const token: string | undefined = data?.access_token;
  if (!token) {
    throw new Error('Refresh response did not contain an access token');
  }
  setAccessToken(token);
  return token;
}

// Single-flight refresh: concurrent 401s share one refresh call instead of
// firing a stampede that invalidates each other.
let refreshPromise: Promise<string> | null = null;

function refreshOnce(): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = requestRefresh().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableConfig | undefined;

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      // Never try to "refresh" a failed login/refresh/logout call - a wrong
      // password would otherwise be swallowed and turn into a redirect.
      (originalRequest.url ?? '').includes('/auth/')
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      const token = await refreshOnce();
      originalRequest.headers.Authorization = `Bearer ${token}`;
      return await api(originalRequest);
    } catch (refreshError) {
      clearAccessToken();
      onUnauthorized?.();
      return Promise.reject(refreshError);
    }
  }
);

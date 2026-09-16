import os

base_dir = r"s:\PMS\frontend"

files = {
    "package.json": """{
  "name": "pms-frontend",
  "version": "0.1.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx"
  },
  "dependencies": {
    "@tanstack/react-query": "^5.56.0",
    "axios": "^1.7.0",
    "clsx": "^2.1.0",
    "date-fns": "^3.6.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@typescript-eslint/eslint-plugin": "^7.0.0",
    "@typescript-eslint/parser": "^7.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.20",
    "eslint": "^8.57.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.0",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0",
    "vite-plugin-pwa": "^0.20.0",
    "workbox-window": "^7.1.0"
  }
}""",
    "vite.config.ts": """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Proxy Management System',
        short_name: 'PMS',
        description: 'School teacher proxy management for Mrs. Vaishali Patil',
        theme_color: '#2563eb',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192.svg',
            sizes: '192x192',
            type: 'image/svg+xml'
          },
          {
            src: '/icons/icon-512.svg',
            sizes: '512x512',
            type: 'image/svg+xml'
          }
        ]
      },
      workbox: {
        runtimeCaching: [
          { urlPattern: /^\\/api\\/timetable/, handler: 'StaleWhileRevalidate' },
          { urlPattern: /^\\/api\\/teachers/, handler: 'NetworkFirst' },
        ]
      }
    }),
  ],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } },
});
""",
    "tailwind.config.ts": """export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        surface: 'var(--color-surface)',
        'surface-elevated': 'var(--color-surface-elevated)',
        border: 'var(--color-border)',
        primary: 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        'text-muted': 'var(--color-text-muted)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
      },
      transitionDuration: {
        fast: '150ms',
        base: '200ms',
        slow: '250ms',
      },
    },
  },
  plugins: [],
};
""",
    "postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",
    "tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
""",
    "tsconfig.node.json": """{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts", "tailwind.config.ts"]
}
""",
    ".eslintrc.cjs": """module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
  },
}
""",
    ".prettierrc": """{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
""",
    ".env.example": """VITE_API_URL=http://localhost:8000
""",
    "README.md": """# Proxy Management System (Frontend)

## Prerequisites
- Node 20+
- npm

## Setup
1. `npm install`
2. Copy `.env.example` to `.env`
3. `npm run dev`

## Project Structure
- `src/app/` - App initialization
- `src/components/ui/` - Shared UI components
- `src/features/` - Feature modules
- `src/hooks/` - Custom hooks
- `src/lib/` - Utils & configs
- `src/services/` - API services
- `src/types/` - Shared types
- `src/routes/` - Router definitions
""",
    "index.html": """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/icons/icon-192.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
    <meta name="theme-color" content="#2563eb" />
    <title>Proxy Management System</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""",
    "public/manifest.json": """{
  "name": "Proxy Management System",
  "short_name": "PMS",
  "description": "School teacher proxy management for Mrs. Vaishali Patil",
  "theme_color": "#2563eb",
  "background_color": "#ffffff",
  "display": "standalone",
  "orientation": "portrait",
  "start_url": "/",
  "icons": [
    {
      "src": "/icons/icon-192.svg",
      "sizes": "192x192",
      "type": "image/svg+xml"
    },
    {
      "src": "/icons/icon-512.svg",
      "sizes": "512x512",
      "type": "image/svg+xml"
    }
  ]
}
""",
    "public/icons/icon-192.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
  <rect width="192" height="192" fill="#2563eb"/>
  <text x="96" y="112" font-family="sans-serif" font-size="64" fill="white" text-anchor="middle">P</text>
</svg>
""",
    "public/icons/icon-512.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#2563eb"/>
  <text x="256" y="300" font-family="sans-serif" font-size="160" fill="white" text-anchor="middle">P</text>
</svg>
""",
    "src/main.tsx": """import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './app/App';
import '@/styles/globals.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""",
    "src/app/App.tsx": """import { RouterProvider } from 'react-router-dom';
import { router } from '../routes';
import { QueryProvider } from './QueryProvider';
import { ToastContainer } from '../components/ui/ToastContainer';

export function App() {
  return (
    <QueryProvider>
      <RouterProvider router={router} />
      <ToastContainer />
    </QueryProvider>
  );
}
""",
    "src/app/QueryProvider.tsx": """import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '../lib/queryClient';
import { ReactNode } from 'react';

export function QueryProvider({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
""",
    "src/lib/queryClient.ts": """import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
    },
  },
});
""",
    "src/lib/utils.ts": """import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
""",
    "src/lib/api.ts": """import axios from 'axios';

let accessToken = '';

export const setAccessToken = (token: string) => {
  accessToken = token;
};

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
});

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const { data } = await axios.post(`${api.defaults.baseURL}/auth/refresh`);
        accessToken = data.accessToken;
        return api(originalRequest);
      } catch (err) {
        accessToken = '';
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }
    return Promise.reject(error);
  }
);
""",
    "src/types/index.ts": """export type Weekday = 'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY' | 'SATURDAY';
export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'NOT_MARKED';
export type ProxyStatus = 'PENDING' | 'ASSIGNED' | 'UNRESOLVED';

export interface Teacher { id: string; name: string; class_name: string | null; active: boolean; }
export interface TeacherWithAttendance extends Teacher { attendance_status: AttendanceStatus; }
export interface TimetableEntry { id: string; teacher_id: string; weekday: Weekday; period_number: number; subject: string | null; class_name: string | null; is_recess: boolean; is_free: boolean; time_start: string | null; time_end: string | null; }
export interface Attendance { id: string; teacher_id: string; date: string; status: AttendanceStatus; marked_at: string; }
export interface ProxyRequirement { id: string; date: string; period_number: number; absent_teacher_id: string; absent_teacher_name: string; class_name: string; subject: string | null; status: ProxyStatus; assignment?: ProxyAssignment; }
export interface ProxyAssignment { id: string; requirement_id: string; proxy_teacher_id: string; proxy_teacher_name: string; assigned_at: string; }
export interface Candidate { teacher: Teacher; proxy_count_today: number; reasons: string[]; }
export interface CandidateResult { recommended: Candidate | null; others: Candidate[]; }
export interface DailyStats { date: string; absent_count: number; requirements_count: number; assigned_count: number; unresolved_count: number; avg_assignment_time_seconds: number | null; collision_attempts: number; }
export interface AuditEvent { id: string; event_type: string; entity_type: string; entity_id: string; metadata: Record<string, unknown>; created_at: string; actor_name: string; }
""",
    "src/styles/tokens.css": """:root {
  /* Colors - Light Mode */
  --color-bg: #ffffff;
  --color-surface: #f9fafb;
  --color-surface-elevated: #ffffff;
  --color-border: #e5e7eb;
  --color-border-subtle: #f3f4f6;
  
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-primary-fg: #ffffff;
  
  --color-success: #16a34a;
  --color-success-bg: #f0fdf4;
  --color-warning: #d97706;
  --color-warning-bg: #fffbeb;
  --color-error: #dc2626;
  --color-error-bg: #fef2f2;
  
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-text-muted: #9ca3af;
  --color-text-inverse: #ffffff;
  
  /* Present/Absent/Not Marked status colors */
  --color-present: #16a34a;
  --color-present-bg: #dcfce7;
  --color-absent: #dc2626;
  --color-absent-bg: #fee2e2;
  --color-not-marked: #6b7280;
  --color-not-marked-bg: #f3f4f6;
  
  /* Proxy status colors */
  --color-pending: #d97706;
  --color-pending-bg: #fef3c7;
  --color-assigned: #16a34a;
  --color-assigned-bg: #dcfce7;
  --color-unresolved: #dc2626;
  --color-unresolved-bg: #fee2e2;
  
  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  
  /* Border radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.07), 0 4px 6px -4px rgba(0,0,0,0.05);
  
  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  
  /* Bottom nav safe area */
  --bottom-nav-height: 64px;
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 250ms ease;
}

[data-theme="dark"] {
  --color-bg: #0a0a0a;
  --color-surface: #111111;
  --color-surface-elevated: #1a1a1a;
  --color-border: #2a2a2a;
  --color-border-subtle: #1f1f1f;
  --color-text-primary: #f9fafb;
  --color-text-secondary: #9ca3af;
  --color-text-muted: #6b7280;
}
""",
    "src/styles/globals.css": """@import './tokens.css';
@tailwind base;
@tailwind components;
@tailwind utilities;

* { box-sizing: border-box; }
body {
  font-family: var(--font-sans);
  background-color: var(--color-bg);
  color: var(--color-text-primary);
  -webkit-font-smoothing: antialiased;
}

/* Safe area utilities */
.safe-bottom { padding-bottom: env(safe-area-inset-bottom); }

/* Skeleton shimmer */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton-shimmer {
  background: linear-gradient(90deg, var(--color-border-subtle) 25%, var(--color-border) 50%, var(--color-border-subtle) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@media (prefers-reduced-motion: reduce) {
  .skeleton-shimmer { animation: none; background: var(--color-border-subtle); }
}

/* Focus ring */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
""",
    "src/routes/index.tsx": """import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { LoginPage } from '../features/auth/LoginPage';
import { AppShell } from '../components/AppShell';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { AttendancePage } from '../features/attendance/AttendancePage';
import { TimetablePage } from '../features/timetable/TimetablePage';
import { HistoryPage } from '../features/history/HistoryPage';
import { MorePage } from '../features/settings/MorePage';
import { CandidatePage } from '../features/proxy/CandidatePage';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    element: <ProtectedRoute><AppShell /></ProtectedRoute>,
    children: [
      { path: '/', element: <DashboardPage /> },
      { path: '/attendance', element: <AttendancePage /> },
      { path: '/timetable', element: <TimetablePage /> },
      { path: '/history', element: <HistoryPage /> },
      { path: '/more', element: <MorePage /> },
      { path: '/proxy/:requirementId/candidates', element: <CandidatePage /> },
    ],
  },
]);
""",
    "src/routes/ProtectedRoute.tsx": """import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../features/auth/useAuth';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
""",
    "src/features/auth/useAuth.ts": """import { create } from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  setAuthenticated: (value: boolean) => void;
}

export const useAuth = create<AuthState>((set) => ({
  isAuthenticated: false,
  setAuthenticated: (value) => set({ isAuthenticated: value }),
}));
""",
    "src/features/auth/LoginPage.tsx": """import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './useAuth';
import { setAccessToken } from '../../lib/api';

export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { setAuthenticated } = useAuth();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Dummy login logic
    setAccessToken('dummy-token');
    setAuthenticated(true);
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg p-4">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-bold text-center mb-2">D.G. Tatkare School</h1>
        <h2 className="text-xl text-center text-text-secondary mb-8">PMS</h2>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input 
            type="text" 
            placeholder="Username" 
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 min-h-[44px] rounded-md border border-border focus:outline-primary"
            required
          />
          <input 
            type="password" 
            placeholder="Password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 min-h-[44px] rounded-md border border-border focus:outline-primary"
            required
          />
          <button 
            type="submit" 
            className="w-full bg-primary text-white font-medium py-3 rounded-md min-h-[44px] hover:bg-primary-hover transition-colors"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
}
"""
}

# The remaining files are basic stubs based on requirements
remaining_files = {
    "src/components/ui/Button.tsx": """import React from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none disabled:opacity-50 disabled:pointer-events-none',
          {
            'bg-primary text-white hover:bg-primary-hover': variant === 'primary',
            'bg-transparent text-text-primary hover:bg-surface': variant === 'ghost',
            'bg-error text-white hover:bg-error/90': variant === 'destructive',
            'h-9 px-3 text-sm': size === 'sm',
            'h-11 px-4 min-h-[44px] text-base': size === 'md',
            'h-14 px-6 text-lg': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {isLoading ? <span className="mr-2 border-2 border-t-transparent border-white rounded-full w-4 h-4 animate-spin"></span> : null}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';
""",
    "src/components/ui/StatusPill.tsx": """import { cn } from '../../lib/utils';
import { AttendanceStatus, ProxyStatus } from '../../types';

export function StatusPill({ status }: { status: AttendanceStatus | ProxyStatus | string }) {
  let colorClass = 'bg-not-marked-bg text-not-marked';
  let label = status;
  let icon = '⚪';

  switch (status) {
    case 'PRESENT':
    case 'ASSIGNED':
      colorClass = 'bg-present-bg text-present';
      icon = '✓';
      break;
    case 'ABSENT':
    case 'UNRESOLVED':
      colorClass = 'bg-absent-bg text-absent';
      icon = '✕';
      break;
    case 'PENDING':
      colorClass = 'bg-pending-bg text-pending';
      icon = '⏱';
      break;
  }

  return (
    <span className={cn('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold', colorClass)}>
      <span>{icon}</span>
      {label}
    </span>
  );
}
""",
    "src/components/ui/Card.tsx": """import React from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ className, padding = 'md', ...props }: CardProps) {
  return (
    <div
      className={cn(
        'bg-surface-elevated rounded-lg shadow-sm border border-border overflow-hidden',
        {
          'p-0': padding === 'none',
          'p-3': padding === 'sm',
          'p-4': padding === 'md',
          'p-6': padding === 'lg',
        },
        className
      )}
      {...props}
    />
  );
}
""",
    "src/components/ui/Skeleton.tsx": """import { cn } from '../../lib/utils';

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('skeleton-shimmer rounded-md', className)} />;
}
""",
    "src/components/ui/SearchInput.tsx": """import React from 'react';
import { cn } from '../../lib/utils';

export interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  onClear?: () => void;
}

export function SearchInput({ className, value, onClear, onChange, ...props }: SearchInputProps) {
  return (
    <div className="relative flex items-center">
      <span className="absolute left-3 text-text-muted">🔍</span>
      <input
        type="text"
        value={value}
        onChange={onChange}
        className={cn(
          'w-full pl-10 pr-10 py-2 h-11 min-h-[44px] rounded-md border border-border focus:outline-primary bg-bg text-text-primary',
          className
        )}
        {...props}
      />
      {value && onClear && (
        <button
          type="button"
          onClick={onClear}
          className="absolute right-3 p-1 text-text-muted hover:text-text-primary min-h-[44px] min-w-[44px] flex items-center justify-center"
        >
          ✕
        </button>
      )}
    </div>
  );
}
""",
    "src/components/ui/FilterChips.tsx": """import React from 'react';
import { cn } from '../../lib/utils';

export interface FilterChipsProps {
  options: { label: string; value: string }[];
  value: string;
  onChange: (val: string) => void;
}

export function FilterChips({ options, value, onChange }: FilterChipsProps) {
  return (
    <div className="flex overflow-x-auto gap-2 py-2 no-scrollbar">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={cn(
            'whitespace-nowrap px-4 h-9 min-h-[44px] rounded-full text-sm font-medium transition-colors',
            value === opt.value
              ? 'bg-primary text-white'
              : 'bg-surface text-text-secondary hover:bg-border-subtle'
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
""",
    "src/components/ui/Avatar.tsx": """import { cn } from '../../lib/utils';

export function Avatar({ name, size = 'md' }: { name: string; size?: 'sm' | 'md' | 'lg' }) {
  const initials = name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase();
  const colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-red-500', 'bg-purple-500', 'bg-pink-500'];
  const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const color = colors[hash % colors.length];

  return (
    <div
      className={cn(
        'rounded-full flex items-center justify-center text-white font-bold',
        color,
        {
          'w-8 h-8 text-xs': size === 'sm',
          'w-10 h-10 text-sm': size === 'md',
          'w-12 h-12 text-base': size === 'lg',
        }
      )}
    >
      {initials}
    </div>
  );
}
""",
    "src/components/ui/ToastContainer.tsx": """import { useToast } from '../../hooks/useToast';

export function ToastContainer() {
  const { toasts } = useToast();
  return (
    <div className="fixed bottom-[80px] left-0 right-0 p-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => (
        <div key={t.id} className="bg-text-primary text-bg px-4 py-3 rounded-md shadow-lg pointer-events-auto transition-transform animate-slide-up">
          {t.message}
        </div>
      ))}
    </div>
  );
}
""",
    "src/components/ui/EmptyState.tsx": """export function EmptyState({ icon, title, description }: { icon: string; title: string; description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center px-4">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-text-primary mb-1">{title}</h3>
      {description && <p className="text-text-secondary text-sm">{description}</p>}
    </div>
  );
}
""",
    "src/components/ui/Modal.tsx": """import React from 'react';

export function Modal({ isOpen, onClose, title, children }: { isOpen: boolean; onClose: () => void; title: string; children: React.ReactNode }) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="bg-bg w-full max-w-md rounded-t-xl sm:rounded-xl shadow-xl overflow-hidden animate-slide-up" onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b border-border flex justify-between items-center">
          <h2 className="text-lg font-bold">{title}</h2>
          <button onClick={onClose} className="p-2 min-h-[44px] min-w-[44px]">✕</button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
}
""",
    "src/components/AppShell.tsx": """import { Outlet } from 'react-router-dom';
import { TopBar } from './TopBar';
import { BottomNav } from './BottomNav';

export function AppShell() {
  return (
    <div className="min-h-screen bg-bg flex flex-col">
      <TopBar />
      <main className="flex-1 overflow-y-auto pb-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom))]">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
""",
    "src/components/TopBar.tsx": """import { useNavigate, useLocation } from 'react-router-dom';

export function TopBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const canGoBack = location.pathname !== '/' && location.pathname !== '/attendance' && location.pathname !== '/timetable' && location.pathname !== '/history' && location.pathname !== '/more';

  return (
    <header className="sticky top-0 z-40 bg-bg/90 backdrop-blur-md border-b border-border px-4 h-14 flex items-center">
      {canGoBack && (
        <button onClick={() => navigate(-1)} className="mr-4 p-2 -ml-2 min-h-[44px] min-w-[44px] flex items-center justify-center">
          ←
        </button>
      )}
      <h1 className="text-lg font-bold">PMS</h1>
    </header>
  );
}
""",
    "src/components/BottomNav.tsx": """import { NavLink } from 'react-router-dom';
import { cn } from '../lib/utils';

export function BottomNav() {
  const links = [
    { to: '/', label: 'Today', icon: '🏠' },
    { to: '/attendance', label: 'Attendance', icon: '👥' },
    { to: '/timetable', label: 'Timetable', icon: '📅' },
    { to: '/history', label: 'History', icon: '🕒' },
    { to: '/more', label: 'More', icon: '☰' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 h-[var(--bottom-nav-height)] safe-bottom bg-surface-elevated border-t border-border flex justify-around items-center z-40">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) =>
            cn('flex flex-col items-center justify-center w-full h-full min-h-[44px] min-w-[44px]', isActive ? 'text-primary' : 'text-text-muted')
          }
        >
          <span className="text-xl mb-1">{link.icon}</span>
          <span className="text-[10px] font-medium">{link.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
""",
    "src/hooks/useToast.ts": """import { create } from 'zustand';

interface Toast { id: string; message: string; type: 'success'|'error'|'info'; }
interface ToastStore { toasts: Toast[]; addToast: (msg: string, type?: 'success'|'error'|'info') => void; }

export const useToast = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (message, type = 'info') => {
    const id = Math.random().toString(36).slice(2);
    set((state) => ({ toasts: [...state.toasts, { id, message, type }] }));
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
    }, 4000);
  },
}));
""",
    "src/hooks/useDebounce.ts": """import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
}
""",
    "src/hooks/useOnline.ts": """import { useState, useEffect } from 'react';

export function useOnline() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  return isOnline;
}
""",
    "src/features/dashboard/DashboardPage.tsx": """import { Card } from '../../components/ui/Card';
import { ProxyRequirementCard } from '../proxy/ProxyRequirementCard';
import { ProxyRequirement } from '../../types';

export function DashboardPage() {
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  
  // Dummy data
  const reqs: ProxyRequirement[] = [
    { id: '1', date: '2026-08-30', period_number: 1, absent_teacher_id: 't1', absent_teacher_name: 'Mr. Sharma', class_name: '10A', subject: 'Math', status: 'PENDING' }
  ];

  return (
    <div className="p-4 space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Good morning, Mrs. Patil</h1>
        <p className="text-text-secondary">{today}</p>
      </header>

      <div className="grid grid-cols-2 gap-4">
        <Card padding="md" className="flex flex-col items-center">
          <span className="text-3xl font-bold text-error">4</span>
          <span className="text-sm text-text-secondary mt-1">Absent</span>
        </Card>
        <Card padding="md" className="flex flex-col items-center">
          <span className="text-3xl font-bold text-warning">12</span>
          <span className="text-sm text-text-secondary mt-1">Proxies Needed</span>
        </Card>
      </div>

      <section>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Needs Attention</h2>
        </div>
        <div className="space-y-3">
          {reqs.map(req => <ProxyRequirementCard key={req.id} requirement={req} />)}
        </div>
      </section>
    </div>
  );
}
""",
    "src/features/proxy/ProxyRequirementCard.tsx": """import { Card } from '../../components/ui/Card';
import { ProxyRequirement } from '../../types';
import { StatusPill } from '../../components/ui/StatusPill';
import { Button } from '../../components/ui/Button';
import { useNavigate } from 'react-router-dom';

export function ProxyRequirementCard({ requirement }: { requirement: ProxyRequirement }) {
  const navigate = useNavigate();
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex justify-between items-start">
        <div>
          <div className="font-bold">Period {requirement.period_number} • {requirement.class_name}</div>
          <div className="text-sm text-text-secondary">Absent: {requirement.absent_teacher_name}</div>
          {requirement.subject && <div className="text-sm text-text-secondary">Subject: {requirement.subject}</div>}
        </div>
        <StatusPill status={requirement.status} />
      </div>
      {requirement.status === 'PENDING' && (
        <Button size="sm" onClick={() => navigate(`/proxy/${requirement.id}/candidates`)}>
          Assign
        </Button>
      )}
      {requirement.assignment && (
        <div className="text-sm text-success mt-2">
          Assigned to: {requirement.assignment.proxy_teacher_name}
        </div>
      )}
    </Card>
  );
}
""",
    "src/features/proxy/CandidatePage.tsx": """import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';

export function CandidatePage() {
  const { requirementId } = useParams();
  const navigate = useNavigate();
  
  return (
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold mb-4">Assign Proxy</h1>
      <p>Requirement ID: {requirementId}</p>
      
      <div className="bg-surface-elevated p-4 rounded-lg shadow-sm border border-border">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white">SK</div>
          <div>
            <div className="font-bold">Mrs. Kadam</div>
            <div className="text-xs text-text-secondary">Free period • 0 proxies today</div>
          </div>
        </div>
        <Button className="w-full" onClick={() => navigate(-1)}>Assign Proxy</Button>
      </div>
    </div>
  );
}
""",
    "src/features/attendance/AttendancePage.tsx": """import { useState } from 'react';
import { SearchInput } from '../../components/ui/SearchInput';
import { FilterChips } from '../../components/ui/FilterChips';
import { TeacherWithAttendance } from '../../types';
import { Avatar } from '../../components/ui/Avatar';
import { StatusPill } from '../../components/ui/StatusPill';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';

export function AttendancePage() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('ALL');
  const [selectedTeacher, setSelectedTeacher] = useState<TeacherWithAttendance | null>(null);

  const filters = [
    { label: 'All', value: 'ALL' },
    { label: 'Not Marked', value: 'NOT_MARKED' },
    { label: 'Present', value: 'PRESENT' },
    { label: 'Absent', value: 'ABSENT' }
  ];

  const teachers: TeacherWithAttendance[] = [
    { id: '1', name: 'Mrs. Patil', class_name: '10A', active: true, attendance_status: 'PRESENT' },
    { id: '2', name: 'Mr. Sharma', class_name: '9B', active: true, attendance_status: 'ABSENT' },
    { id: '3', name: 'Ms. Deshmukh', class_name: null, active: true, attendance_status: 'NOT_MARKED' },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 pb-0 space-y-3 sticky top-14 bg-bg z-10 border-b border-border">
        <SearchInput placeholder="Search teachers..." value={search} onChange={e => setSearch(e.target.value)} onClear={() => setSearch('')} />
        <FilterChips options={filters} value={filter} onChange={setFilter} />
      </div>
      
      <div className="p-4 space-y-2">
        {teachers.map(t => (
          <div key={t.id} onClick={() => setSelectedTeacher(t)} className="flex items-center justify-between p-3 bg-surface-elevated rounded-lg shadow-sm border border-border cursor-pointer active:bg-surface transition-colors">
            <div className="flex items-center gap-3">
              <Avatar name={t.name} />
              <div>
                <div className="font-semibold">{t.name}</div>
                {t.class_name && <div className="text-xs text-text-secondary">Class Teacher: {t.class_name}</div>}
              </div>
            </div>
            <StatusPill status={t.attendance_status} />
          </div>
        ))}
      </div>

      <Modal isOpen={!!selectedTeacher} onClose={() => setSelectedTeacher(null)} title={selectedTeacher?.name || ''}>
        <div className="flex flex-col gap-3">
          <Button variant="primary" className="bg-success hover:bg-success/90" onClick={() => setSelectedTeacher(null)}>Mark Present</Button>
          <Button variant="destructive" onClick={() => setSelectedTeacher(null)}>Mark Absent</Button>
          <Button variant="ghost" onClick={() => setSelectedTeacher(null)}>Clear Status</Button>
        </div>
      </Modal>
    </div>
  );
}
""",
    "src/features/timetable/TimetablePage.tsx": """import { useState } from 'react';
import { FilterChips } from '../../components/ui/FilterChips';
import { Card } from '../../components/ui/Card';

export function TimetablePage() {
  const days = [
    { label: 'Mon', value: 'MONDAY' },
    { label: 'Tue', value: 'TUESDAY' },
    { label: 'Wed', value: 'WEDNESDAY' },
    { label: 'Thu', value: 'THURSDAY' },
    { label: 'Fri', value: 'FRIDAY' },
    { label: 'Sat', value: 'SATURDAY' },
  ];
  const [day, setDay] = useState('MONDAY');

  return (
    <div className="p-4 space-y-4">
      <FilterChips options={days} value={day} onChange={setDay} />
      
      <div className="space-y-3">
        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 bg-surface flex items-center justify-center rounded-md font-bold text-lg text-primary">1</div>
          <div>
            <div className="font-bold">Math</div>
            <div className="text-sm text-text-secondary">Class 10A</div>
          </div>
        </Card>
        
        <Card className="flex items-center gap-4 bg-not-marked-bg border-dashed">
          <div className="w-12 h-12 bg-surface flex items-center justify-center rounded-md font-bold text-lg text-text-muted">2</div>
          <div>
            <div className="font-bold text-text-muted">Free Period</div>
          </div>
        </Card>
      </div>
    </div>
  );
}
""",
    "src/features/history/HistoryPage.tsx": """import { EmptyState } from '../../components/ui/EmptyState';

export function HistoryPage() {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">History & Audit</h1>
      <EmptyState icon="🕒" title="No history found" description="Audit logs will appear here." />
    </div>
  );
}
""",
    "src/features/settings/MorePage.tsx": """import { Button } from '../../components/ui/Button';
import { useAuth } from '../auth/useAuth';
import { useNavigate } from 'react-router-dom';

export function MorePage() {
  const { setAuthenticated } = useAuth();
  const navigate = useNavigate();

  const toggleDarkMode = () => {
    document.documentElement.setAttribute('data-theme', 
      document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'
    );
  };

  const handleLogout = () => {
    setAuthenticated(false);
    navigate('/login');
  };

  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold">VP</div>
        <div>
          <h2 className="text-xl font-bold">Mrs. Vaishali Patil</h2>
          <p className="text-text-secondary">Supervisor</p>
        </div>
      </div>
      
      <div className="space-y-3">
        <Button variant="ghost" className="w-full justify-start text-left border border-border" onClick={toggleDarkMode}>
          🌗 Toggle Dark Mode
        </Button>
        <Button variant="destructive" className="w-full justify-start text-left" onClick={handleLogout}>
          🚪 Logout
        </Button>
      </div>
    </div>
  );
}
""",
}

files.update(remaining_files)

# Ensure directories exist and write files
for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath.replace('/', '\\'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Scaffolded {len(files)} files successfully.")

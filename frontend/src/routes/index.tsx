import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { LoginPage } from '../features/auth/LoginPage';
import { AppShell } from '../components/AppShell';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { AttendancePage } from '../features/attendance/AttendancePage';
import { TimetablePage } from '../features/timetable/TimetablePage';
import { MorePage } from '../features/settings/MorePage';
import { AssignedProxiesPage } from '../features/proxy/AssignedProxiesPage';
import { AdminRoute } from './AdminRoute';
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
      { path: '/proxies', element: <AssignedProxiesPage /> },
      { path: '/timetable', element: <TimetablePage /> },
      {
        path: '/timetable/settings',
        lazy: async () => {
          const { TimetableSettingsPage } = await import('../features/timetable/TimetableSettingsPage');
          return { element: <AdminRoute><TimetableSettingsPage /></AdminRoute> };
        },
      },
      { path: '/history', lazy: async () => ({ Component: (await import('../features/history/HistoryPage')).HistoryPage }) },
      { path: '/more', element: <MorePage /> },
      { path: '/analytics', lazy: async () => ({ Component: (await import('../features/analytics/AnalyticsPage')).AnalyticsPage }) },
      { path: '/proxy/:requirementId/candidates', element: <CandidatePage /> },
    ],
  },
]);

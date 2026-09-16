import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { LoginPage } from '../features/auth/LoginPage';
import { AppShell } from '../components/AppShell';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { AttendancePage } from '../features/attendance/AttendancePage';
import { TimetablePage } from '../features/timetable/TimetablePage';
import { HistoryPage } from '../features/history/HistoryPage';
import { MorePage } from '../features/settings/MorePage';
import { CandidatePage } from '../features/proxy/CandidatePage';
import { AnalyticsPage } from '../features/analytics/AnalyticsPage';

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
      { path: '/analytics', element: <AnalyticsPage /> },
      { path: '/proxy/:requirementId/candidates', element: <CandidatePage /> },
    ],
  },
]);

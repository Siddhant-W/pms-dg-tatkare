import { Home, Users, CalendarDays, BarChart3, History, HandHelping, type LucideIcon } from 'lucide-react';

export interface NavItem {
  to: string;
  /** Full name, used in the desktop sidebar and page titles. */
  label: string;
  /** Short name for the cramped mobile tab bar. */
  shortLabel: string;
  Icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Today', shortLabel: 'Today', Icon: Home },
  { to: '/attendance', label: 'Attendance', shortLabel: 'Attendance', Icon: Users },
  { to: '/proxies', label: 'Assigned Proxies', shortLabel: 'Proxies', Icon: HandHelping },
  { to: '/timetable', label: 'Timetable', shortLabel: 'Timetable', Icon: CalendarDays },
  { to: '/analytics', label: 'Analytics', shortLabel: 'Analytics', Icon: BarChart3 },
  { to: '/history', label: 'History', shortLabel: 'History', Icon: History },
];

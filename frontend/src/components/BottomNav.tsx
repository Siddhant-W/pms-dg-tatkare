import { NavLink } from 'react-router-dom';
import { Home, Users, CalendarDays, History, Menu } from 'lucide-react';
import { cn } from '../lib/utils';

export function BottomNav() {
  const links = [
    { to: '/', label: 'Today', Icon: Home },
    { to: '/attendance', label: 'Attendance', Icon: Users },
    { to: '/timetable', label: 'Timetable', Icon: CalendarDays },
    { to: '/history', label: 'History', Icon: History },
    { to: '/more', label: 'More', Icon: Menu },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 h-[var(--bottom-nav-height)] safe-bottom bg-surface-elevated/95 backdrop-blur-md border-t border-border flex justify-around items-center z-40">
      {links.map(({ to, label, Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className="flex flex-col items-center justify-center w-full h-full min-h-[44px] min-w-[44px] group"
        >
          {({ isActive }) => (
            <>
              <span
                className={cn(
                  'flex items-center justify-center w-11 h-7 rounded-full transition-all duration-200 ease-out',
                  isActive ? 'bg-primary/10' : 'bg-transparent group-active:bg-surface'
                )}
              >
                <Icon
                  size={20}
                  strokeWidth={isActive ? 2.4 : 2}
                  className={cn('transition-colors duration-200', isActive ? 'text-primary' : 'text-text-muted')}
                />
              </span>
              <span
                className={cn(
                  'text-[10px] font-medium mt-0.5 transition-colors duration-200',
                  isActive ? 'text-primary' : 'text-text-muted'
                )}
              >
                {label}
              </span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}

import { NavLink, useNavigate } from 'react-router-dom';
import { LogOut, Settings2 } from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuth } from '../features/auth/useAuth';
import { Avatar } from './ui/Avatar';
import { NAV_ITEMS } from './nav';

/** Desktop navigation: a fixed navy rail with the brand, the six sections and the signed-in user. */
export function Sidebar() {
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);
  const navigate = useNavigate();
  const isAdmin = user?.role === 'ADMIN';

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col bg-nav text-nav-fg lg:flex">
      <div className="flex items-center gap-3 px-6 pb-6 pt-7">
        <img src="/assets/presento-icon.png" alt="" className="h-10 w-10 rounded-xl" />
        <div className="min-w-0">
          <p className="font-heading text-xl font-bold leading-none tracking-wider">Presento</p>
          <span className="gold-rule mt-2" aria-hidden />
        </div>
      </div>

      <nav aria-label="Main" className="flex-1 space-y-1 px-3">
        {NAV_ITEMS.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition-colors',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent',
                isActive ? 'bg-nav-hover text-white' : 'text-nav-muted hover:bg-nav-hover hover:text-nav-fg'
              )
            }
          >
            {({ isActive }) => (
              <>
                <span
                  aria-hidden
                  className={cn('absolute inset-y-2 left-0 w-[3px] rounded-r bg-accent transition-opacity', isActive ? 'opacity-100' : 'opacity-0')}
                />
                <Icon size={19} aria-hidden className={isActive ? 'text-accent' : ''} />
                {label}
              </>
            )}
          </NavLink>
        ))}
        {isAdmin && (
          <NavLink
            to="/timetable/settings"
            className={({ isActive }) =>
              cn(
                'mt-4 flex items-center gap-3 rounded-lg border border-white/10 px-3 py-2.5 text-sm font-semibold transition-colors',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent',
                isActive ? 'bg-nav-hover text-white' : 'text-nav-muted hover:bg-nav-hover hover:text-nav-fg'
              )
            }
          >
            <Settings2 size={19} aria-hidden />
            Timetable settings
          </NavLink>
        )}
      </nav>

      <div className="m-3 flex items-center gap-3 rounded-xl bg-nav-hover p-3">
        <button
          type="button"
          onClick={() => navigate('/more')}
          className="flex min-w-0 flex-1 items-center gap-3 rounded-lg text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label="Account and settings"
        >
          <Avatar name={user?.full_name || user?.username || 'User'} className="bg-white/15 text-white" />
          <span className="min-w-0">
            <span className="block truncate text-sm font-semibold text-white">{user?.full_name || user?.username}</span>
            <span className="block text-xs text-nav-muted">{isAdmin ? 'Administrator' : 'Supervisor'}</span>
          </span>
        </button>
        <button
          type="button"
          aria-label="Log out"
          onClick={async () => {
            await logout();
            navigate('/login', { replace: true });
          }}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-nav-muted transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
        >
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
}

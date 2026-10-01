import { NavLink } from 'react-router-dom';
import { cn } from '../lib/utils';
import { NAV_ITEMS } from './nav';

/** Phone navigation. Solid (no blur/opacity), gold pill marks the active tab. */
export function BottomNav() {
  return (
    <nav
      aria-label="Main"
      className="safe-bottom fixed inset-x-0 bottom-0 z-40 flex h-[var(--bottom-nav-height)] items-stretch justify-around border-t border-border bg-surface-elevated lg:hidden"
    >
      {NAV_ITEMS.map(({ to, shortLabel, Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className="group flex min-h-[44px] min-w-0 flex-1 flex-col items-center justify-center focus-visible:outline-none"
        >
          {({ isActive }) => (
            <>
              {/* Active tab uses the gold accent fill (brand spec: "highlights,
                  active tab"), navy content on top - never white on gold. */}
              <span
                className={cn(
                  'flex h-7 w-11 items-center justify-center rounded-full transition-all duration-200 ease-out group-focus-visible:ring-2 group-focus-visible:ring-accent',
                  isActive ? 'bg-accent' : 'bg-transparent group-active:bg-surface'
                )}
              >
                <Icon
                  size={20}
                  strokeWidth={isActive ? 2.4 : 2}
                  aria-hidden
                  className={cn('transition-colors duration-200', isActive ? 'text-accent-fg' : 'text-text-muted')}
                />
              </span>
              <span
                className={cn(
                  'mt-0.5 max-w-full truncate px-0.5 text-[10px] font-semibold tracking-tight transition-colors duration-200',
                  isActive ? 'text-primary' : 'text-text-muted'
                )}
              >
                {shortLabel}
              </span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}

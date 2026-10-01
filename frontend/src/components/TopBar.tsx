import { useNavigate, useLocation } from 'react-router-dom';
import { ChevronLeft, UserCircle2 } from 'lucide-react';
import { NAV_ITEMS } from './nav';
import { IconButton } from './ui/IconButton';

const TOP_LEVEL = new Set([...NAV_ITEMS.map((i) => i.to), '/more']);

/** Phone header: brand, a back button on sub-screens, and the account shortcut. Hidden on desktop (the sidebar has both). */
export function TopBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const canGoBack = !TOP_LEVEL.has(location.pathname);

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-border bg-bg px-4 lg:hidden">
      <div className="flex items-center">
        {canGoBack && (
          <IconButton aria-label="Go back" className="-ml-2 mr-1" onClick={() => navigate(-1)}>
            <ChevronLeft size={22} />
          </IconButton>
        )}
        <img src="/assets/presento-icon.png" alt="" className="mr-2 h-9 w-9 rounded-lg" />
        <p className="font-heading text-lg font-bold tracking-wider text-text-primary">Presento</p>
      </div>
      {/* Settings/profile lives here now that every section has a tab. */}
      <IconButton aria-label="Account and settings" onClick={() => navigate('/more')}>
        <UserCircle2 size={24} />
      </IconButton>
    </header>
  );
}

import { useNavigate, useLocation } from 'react-router-dom';
import { ChevronLeft, UserCircle2 } from 'lucide-react';

export function TopBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const canGoBack = location.pathname !== '/' && location.pathname !== '/attendance' && location.pathname !== '/timetable' && location.pathname !== '/history' && location.pathname !== '/more' && location.pathname !== '/analytics';

  return (
    <header className="sticky top-0 z-40 bg-bg border-b border-border px-4 h-14 flex items-center justify-between">
      <div className="flex items-center">
        {canGoBack && (
          <button
            onClick={() => navigate(-1)}
            aria-label="Go back"
            className="mr-2 -ml-2 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-full text-text-primary active:bg-surface transition-colors"
          >
            <ChevronLeft size={22} />
          </button>
        )}
        <img src="/assets/presento-icon.png" alt="Presento logo" className="h-9 w-9 rounded-lg mr-2" />
        <h1 className="text-lg font-bold tracking-tight">Presento</h1>
      </div>
      {/* Settings/profile is reached from here now that "More" is no longer
          a bottom-nav tab (Analytics took its slot) - keeps logout and the
          dark-mode toggle reachable from every screen. */}
      <button
        onClick={() => navigate('/more')}
        aria-label="Settings and profile"
        className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-full text-text-primary active:bg-surface transition-colors"
      >
        <UserCircle2 size={24} />
      </button>
    </header>
  );
}

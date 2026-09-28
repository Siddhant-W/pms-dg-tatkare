import { useNavigate, useLocation } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';

export function TopBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const canGoBack = location.pathname !== '/' && location.pathname !== '/attendance' && location.pathname !== '/timetable' && location.pathname !== '/history' && location.pathname !== '/more';

  return (
    <header className="sticky top-0 z-40 bg-bg/85 backdrop-blur-md border-b border-border px-4 h-14 flex items-center">
      {canGoBack && (
        <button
          onClick={() => navigate(-1)}
          aria-label="Go back"
          className="mr-2 -ml-2 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-full text-text-primary active:bg-surface transition-colors"
        >
          <ChevronLeft size={22} />
        </button>
      )}
      <h1 className="text-lg font-bold tracking-tight">Presento</h1>
    </header>
  );
}

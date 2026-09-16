import { useState } from 'react';
import { BarChart3, Moon, Sun, LogOut, ChevronRight } from 'lucide-react';
import { useAuth } from '../auth/useAuth';
import { useNavigate } from 'react-router-dom';

function getInitials(name: string) {
  return name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase();
}

export function MorePage() {
  const logout = useAuth((s) => s.logout);
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(() => document.documentElement.getAttribute('data-theme') === 'dark');

  const toggleDarkMode = () => {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try {
      localStorage.setItem('pms.theme', next);
    } catch {
      // Private browsing or a full quota shouldn't block the toggle itself.
    }
    setIsDark(next === 'dark');
  };

  const handleLogout = async () => {
    // Clears the server-side refresh cookie too, not just local state.
    await logout();
    navigate('/login', { replace: true });
  };

  const name = 'Mrs. Vaishali Patil';

  return (
    <div className="p-4 space-y-6 animate-fade-in">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-xl font-bold shadow-sm">
          {getInitials(name)}
        </div>
        <div>
          <h2 className="text-xl font-bold tracking-tight">{name}</h2>
          <p className="text-text-secondary text-sm">Supervisor</p>
        </div>
      </div>

      <div className="rounded-xl border border-border/80 bg-surface-elevated shadow-sm divide-y divide-border overflow-hidden">
        <button
          onClick={() => navigate('/analytics')}
          className="w-full flex items-center gap-3 px-4 py-3.5 min-h-[44px] active:bg-surface transition-colors text-left"
        >
          <span className="flex items-center justify-center w-9 h-9 rounded-full bg-primary/10 text-primary shrink-0">
            <BarChart3 size={17} />
          </span>
          <span className="flex-1 font-medium">Analytics</span>
          <ChevronRight size={18} className="text-text-muted" />
        </button>
        <button
          onClick={toggleDarkMode}
          className="w-full flex items-center gap-3 px-4 py-3.5 min-h-[44px] active:bg-surface transition-colors text-left"
        >
          <span className="flex items-center justify-center w-9 h-9 rounded-full bg-primary/10 text-primary shrink-0">
            {isDark ? <Sun size={17} /> : <Moon size={17} />}
          </span>
          <span className="flex-1 font-medium">{isDark ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
      </div>

      <button
        onClick={handleLogout}
        className="w-full flex items-center gap-3 px-4 py-3.5 min-h-[44px] rounded-xl border border-error/20 bg-error-bg text-error active:bg-error/10 transition-colors font-medium"
      >
        <LogOut size={17} />
        Logout
      </button>
    </div>
  );
}

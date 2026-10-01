import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BarChart3, Moon, Sun, LogOut, ChevronRight, Settings2, History } from 'lucide-react';
import { Page } from '../../components/Page';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Avatar } from '../../components/ui/Avatar';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { useAuth } from '../auth/useAuth';

function Row({ icon, label, onClick, to }: { icon: React.ReactNode; label: string; onClick?: () => void; to?: string }) {
  const body = (
    <>
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary" aria-hidden>{icon}</span>
      <span className="flex-1 font-medium">{label}</span>
      <ChevronRight size={18} className="text-text-muted" aria-hidden />
    </>
  );
  const cls = 'flex min-h-[56px] w-full items-center gap-3 px-4 text-left transition-colors hover:bg-surface active:bg-surface';
  return to ? <Link to={to} className={cls}>{body}</Link> : <button type="button" onClick={onClick} className={cls}>{body}</button>;
}

export function MorePage() {
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(() => document.documentElement.getAttribute('data-theme') === 'dark');
  const isAdmin = user?.role === 'ADMIN';
  const name = user?.full_name || user?.username || 'Supervisor';

  const toggleDarkMode = () => {
    const next = isDark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try {
      localStorage.setItem('presento.theme', next);
    } catch {
      // Private browsing or a full quota shouldn't block the toggle itself.
    }
    setIsDark(next === 'dark');
  };

  const handleLogout = async () => {
    await logout(); // clears the server-side refresh cookie too
    navigate('/login', { replace: true });
  };

  return (
    <Page>
      <PageHeader eyebrow="Account" title="Settings" />

      <Card variant="accent" className="flex items-center gap-4">
        <Avatar name={name} size="lg" />
        <div className="min-w-0">
          <p className="truncate text-lg font-bold">{name}</p>
          <Badge tone={isAdmin ? 'gold' : 'navy'} className="mt-1">{isAdmin ? 'Administrator' : 'Supervisor'}</Badge>
        </div>
      </Card>

      <Card padding="none" className="divide-y divide-border">
        {isAdmin && <Row to="/timetable/settings" icon={<Settings2 size={17} />} label="Timetable settings" />}
        <Row to="/analytics" icon={<BarChart3 size={17} />} label="Analytics" />
        <Row to="/history" icon={<History size={17} />} label="History" />
        <Row onClick={toggleDarkMode} icon={isDark ? <Sun size={17} /> : <Moon size={17} />} label={isDark ? 'Light mode' : 'Dark mode'} />
      </Card>

      <Button variant="secondary" className="w-full text-error" leftIcon={<LogOut size={17} />} onClick={handleLogout}>Log out</Button>
    </Page>
  );
}

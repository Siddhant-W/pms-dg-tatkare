import { Outlet } from 'react-router-dom';
import { TopBar } from './TopBar';
import { BottomNav } from './BottomNav';

export function AppShell() {
  return (
    <div className="min-h-screen bg-bg flex flex-col">
      <TopBar />
      <main className="flex-1 overflow-y-auto pb-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom))]">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}

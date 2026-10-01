import { Outlet } from 'react-router-dom';
import { TopBar } from './TopBar';
import { BottomNav } from './BottomNav';
import { Sidebar } from './Sidebar';
import { OfflineBanner } from './OfflineBanner';

/**
 * Phones: header + content + bottom tab bar. From `lg`: a fixed navy sidebar
 * with the content centred beside it. The brand logo lives in the header on
 * phones and in the sidebar on desktop (so there is only ever one h1 per page).
 */
export function AppShell() {
  return (
    <div className="min-h-dvh lg:pl-64">
      <Sidebar />
      <div className="flex min-h-dvh flex-col">
        <TopBar />
        <OfflineBanner />
        <main
          id="main"
          className="mx-auto w-full max-w-5xl flex-1 pb-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom)+1.5rem)] lg:px-4 lg:pb-12"
        >
          <Outlet />
        </main>
        <BottomNav />
      </div>
    </div>
  );
}

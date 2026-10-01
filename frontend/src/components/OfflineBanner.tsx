import { WifiOff } from 'lucide-react';
import { useOnline } from '../hooks/useOnline';

/** Says so when the connection drops, instead of letting actions fail mysteriously. */
export function OfflineBanner() {
  const online = useOnline();
  if (online) return null;
  return (
    <div role="status" className="flex items-center justify-center gap-2 bg-accent px-4 py-2 text-center text-xs font-bold text-accent-fg animate-fade-in">
      <WifiOff size={14} aria-hidden />
      You're offline. Changes can't be saved until the connection returns.
    </div>
  );
}

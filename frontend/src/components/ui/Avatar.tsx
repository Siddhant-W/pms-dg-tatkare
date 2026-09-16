import { cn } from '../../lib/utils';

export function Avatar({ name, size = 'md' }: { name: string; size?: 'sm' | 'md' | 'lg' }) {
  const initials = name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase();
  // A curated, slightly muted palette reads calmer than raw Tailwind -500s
  // and stays consistent with the app's restrained accent-driven system.
  const colors = ['bg-indigo-500', 'bg-teal-600', 'bg-amber-600', 'bg-rose-500', 'bg-violet-500', 'bg-emerald-600', 'bg-sky-600', 'bg-fuchsia-600'];
  const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const color = colors[hash % colors.length];

  return (
    <div
      className={cn(
        'rounded-full flex items-center justify-center text-white font-semibold shrink-0',
        color,
        {
          'w-8 h-8 text-xs': size === 'sm',
          'w-10 h-10 text-sm': size === 'md',
          'w-12 h-12 text-base': size === 'lg',
        }
      )}
    >
      {initials}
    </div>
  );
}

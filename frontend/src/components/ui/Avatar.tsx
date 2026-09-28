import { cn } from '../../lib/utils';

export function Avatar({ name, size = 'md' }: { name: string; size?: 'sm' | 'md' | 'lg' }) {
  const initials = name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase();

  return (
    <div
      className={cn(
        // One consistent brand-tinted circle for every teacher, matching the
        // single-tone icon badges on the History page - no per-person hash palette.
        'rounded-full flex items-center justify-center bg-primary/10 text-primary font-semibold shrink-0',
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

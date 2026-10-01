import { cn } from '../../lib/utils';

export function Avatar({ name, size = 'md', className }: { name: string; size?: 'sm' | 'md' | 'lg'; className?: string }) {
  // Skip honorifics so "Mrs. Jadhav S.S." reads "JS", not "MJ".
  const parts = name.split(/\s+/).filter((p) => p && !/^(mr|mrs|ms|miss|dr|smt|shri|prof)\.?$/i.test(p));
  const initials = (parts.length ? parts : name.split(/\s+/)).map((n) => n[0]).slice(0, 2).join('').toUpperCase();

  return (
    <div
      aria-hidden
      className={cn(
        // One consistent brand-tinted circle for every teacher, matching the
        // single-tone icon badges on the History page - no per-person hash palette.
        'flex shrink-0 items-center justify-center rounded-full bg-primary/10 font-bold tracking-wide text-primary',
        {
          'h-8 w-8 text-xs': size === 'sm',
          'h-10 w-10 text-sm': size === 'md',
          'h-12 w-12 text-base': size === 'lg',
        },
        className
      )}
    >
      {initials}
    </div>
  );
}

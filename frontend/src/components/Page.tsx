import React from 'react';
import { cn } from '../lib/utils';

/** Consistent page padding/rhythm. Direct children rise in sequence on load (see .stagger in globals.css). */
export function Page({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('stagger space-y-6 px-4 pb-6 pt-5 lg:pt-8', className)}>{children}</div>;
}

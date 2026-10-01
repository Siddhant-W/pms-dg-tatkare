import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// twMerge resolves conflicting utilities (e.g. a component's default
// `bg-primary` vs a caller's `bg-success`) in favour of the last one, instead
// of leaving the winner to CSS source order.
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

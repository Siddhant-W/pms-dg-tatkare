import React, { useId } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';

interface FieldRenderProps {
  id: string;
  'aria-invalid'?: true;
  'aria-describedby'?: string;
}

/**
 * Label + control + hint/error, wired for screen readers: the label is bound
 * to the control and the message is announced via aria-describedby.
 */
export function Field({
  label,
  hint,
  error,
  optional,
  className,
  children,
}: {
  label: string;
  hint?: string;
  error?: string;
  optional?: boolean;
  className?: string;
  children: (props: FieldRenderProps) => React.ReactNode;
}) {
  const id = useId();
  const messageId = `${id}-msg`;
  return (
    <div className={cn('space-y-1.5', className)}>
      <label htmlFor={id} className="flex items-baseline justify-between text-xs font-semibold text-text-secondary">
        <span>{label}</span>
        {optional && <span className="font-medium text-text-muted">Optional</span>}
      </label>
      {children({ id, 'aria-invalid': error ? true : undefined, 'aria-describedby': error || hint ? messageId : undefined })}
      {(error || hint) && (
        <p id={messageId} className={cn('text-xs', error ? 'font-medium text-error' : 'text-text-muted')} role={error ? 'alert' : undefined}>
          {error ?? hint}
        </p>
      )}
    </div>
  );
}

const CONTROL =
  'w-full h-11 min-h-[44px] rounded-lg border bg-surface-elevated px-3.5 text-sm text-text-primary placeholder:text-text-muted ' +
  'transition-colors focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/30 disabled:opacity-60 disabled:cursor-not-allowed';

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement> & { invalid?: boolean }>(
  ({ className, invalid, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(CONTROL, invalid || props['aria-invalid'] ? 'border-error focus:border-error focus:ring-error/20' : 'border-border', className)}
      {...props}
    />
  )
);
Input.displayName = 'Input';

export const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement> & { invalid?: boolean }>(
  ({ className, invalid, children, ...props }, ref) => (
    <div className="relative">
      <select
        ref={ref}
        className={cn(CONTROL, 'appearance-none pr-10', invalid || props['aria-invalid'] ? 'border-error' : 'border-border', className)}
        {...props}
      >
        {children}
      </select>
      <ChevronDown size={16} className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-text-muted" aria-hidden />
    </div>
  )
);
Select.displayName = 'Select';

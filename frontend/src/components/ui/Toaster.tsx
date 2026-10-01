import { Toaster as Sonner } from 'sonner';

/** Brand-styled toast host. Call `toast.success(...)` / `toast.error(...)` from 'sonner'. */
export function Toaster() {
  return (
    <Sonner
      // Bottom-right on desktop (clear of page titles); on phones it sits just above the tab bar.
      position="bottom-right"
      offset={{ bottom: 20, right: 20 }}
      mobileOffset={{ bottom: 'calc(var(--bottom-nav-height) + 12px)', left: 16, right: 16 }}
      closeButton
      toastOptions={{
        classNames: {
          toast: '!rounded-xl !border !border-border !bg-surface-elevated !text-text-primary !shadow-lg !font-sans',
          title: '!text-sm !font-semibold',
          description: '!text-xs !text-text-secondary',
          success: '!border-l-4 !border-l-success',
          error: '!border-l-4 !border-l-error',
          closeButton: '!bg-surface-elevated !border-border',
        },
      }}
    />
  );
}

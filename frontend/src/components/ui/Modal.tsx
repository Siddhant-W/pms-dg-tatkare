import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { Button } from './Button';
import { IconButton } from './IconButton';
import { cn } from '../../lib/utils';

/**
 * Dialog built on Radix: focus is trapped and restored, Escape closes it, the
 * page behind is inert and scroll-locked, and it is announced with its title.
 * A bottom sheet on phones, a centred card from the sm breakpoint.
 */
export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  className,
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-nav/60 animate-fade-in" />
        <Dialog.Content
          // With no description, say so explicitly (otherwise Radix warns).
          {...(description ? {} : { 'aria-describedby': undefined })}
          className={cn(
            'dialog-content fixed z-50 flex max-h-[92dvh] w-full flex-col overflow-hidden bg-surface-elevated shadow-lg',
            'inset-x-0 bottom-0 rounded-t-2xl border-t border-border',
            'sm:inset-auto sm:left-1/2 sm:top-1/2 sm:max-w-md sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl sm:border',
            className
          )}
        >
          <div className="flex items-start justify-between gap-3 border-b border-border px-5 py-4">
            <div className="min-w-0">
              <Dialog.Title className="font-heading text-lg font-bold leading-snug text-text-primary">{title}</Dialog.Title>
              {description ? (
                <Dialog.Description className="mt-1 text-sm text-text-secondary">{description}</Dialog.Description>
              ) : null}
            </div>
            <Dialog.Close asChild>
              <IconButton aria-label="Close" size="sm" className="-mr-2 -mt-1">
                <X size={18} />
              </IconButton>
            </Dialog.Close>
          </div>
          <div className="overflow-y-auto px-5 py-4 pb-[max(1rem,env(safe-area-inset-bottom))]">{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

/** A yes/no question before something hard to undo. */
export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  tone = 'primary',
  isPending,
  children,
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  tone?: 'primary' | 'destructive';
  isPending?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <Modal isOpen={isOpen} onClose={() => !isPending && onClose()} title={title} description={description}>
      <div className="space-y-4">
        {children}
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="ghost" onClick={onClose} disabled={isPending}>
            {cancelLabel}
          </Button>
          <Button variant={tone === 'destructive' ? 'destructive' : 'primary'} onClick={onConfirm} isLoading={isPending}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

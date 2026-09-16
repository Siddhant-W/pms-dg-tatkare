import React from 'react';
import { X } from 'lucide-react';

export function Modal({ isOpen, onClose, title, children }: { isOpen: boolean; onClose: () => void; title: string; children: React.ReactNode }) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/50 animate-fade-in" onClick={onClose}>
      <div className="bg-bg w-full max-w-md rounded-t-2xl sm:rounded-2xl shadow-xl overflow-hidden animate-slide-up" onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b border-border flex justify-between items-center">
          <h2 className="text-lg font-bold">{title}</h2>
          <button
            onClick={onClose}
            aria-label="Close"
            className="p-2 -mr-2 min-h-[44px] min-w-[44px] rounded-full text-text-muted active:bg-surface transition-colors flex items-center justify-center"
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
}

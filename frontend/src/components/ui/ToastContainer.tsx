import { useToast } from '../../hooks/useToast';

export function ToastContainer() {
  const { toasts } = useToast();
  return (
    <div className="fixed bottom-[80px] left-0 right-0 p-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => (
        <div key={t.id} className="bg-text-primary text-bg px-4 py-3 rounded-md shadow-lg pointer-events-auto transition-transform animate-slide-up">
          {t.message}
        </div>
      ))}
    </div>
  );
}

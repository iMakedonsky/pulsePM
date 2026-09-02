import { type ReactNode, useState } from 'react';
import { CreateToastContext, type ToastType } from './toast-context.ts';

interface ToastMessage {
  id: number;
  message: string;
  type: ToastType;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (message: string, type: ToastType): void => {
    const id: number = Date.now();
    const newToast: ToastMessage = { id, message, type };

    setToasts((responseMessage) => [...responseMessage, newToast]);

    setTimeout(() => {
      // it fetches current toast and then call filter method which return new array with without previous toast
      setToasts((setOfToasts) => setOfToasts.filter((toast) => toast.id !== id));
    }, 5000); // Toast will be deleted after 5s
  };
  return (
    <CreateToastContext.Provider value={{ addToast }}>
      {children}
      <div className="absolute inset-x-0 top-8.75 z-50 flex flex-col items-center gap-3 px-4">
        {toasts.map((toast) => (
          <div
            className={`w-full max-w-md rounded-md border px-4 py-3 text-center shadow-sm backdrop-blur-sm ${toast.type === 'Error' ? 'border-red-300 bg-red-100 text-[var(--sea-ink)]' : 'border-[var(--line)] bg-cyan-100 text-[var(--sea-ink)]'}`}
            key={toast.id}
          >
            <h2 className="font-semibold text-lg">{toast.type}</h2>
            <p className="text-sm">{toast.message}</p>
          </div>
        ))}
      </div>
    </CreateToastContext.Provider>
  );
}

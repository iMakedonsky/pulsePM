import { createContext, useContext } from 'react';

export type ToastType = 'Success' | 'Error';

export interface ToastContexType {
  addToast: (message: string, type: ToastType) => void;
}

export const CreateToastContext = createContext<ToastContexType | null>(null);

export const useToast = (): ToastContexType => {
  const ctx = useContext(CreateToastContext);
  if (!ctx) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return ctx;
};

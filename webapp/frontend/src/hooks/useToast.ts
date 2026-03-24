import { useEffect, useState } from 'react';
import { toastManager } from '../utils/toastManager';
import type { ToastType, ToastMessage } from '../utils/toastManager';

export function useToast() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    return toastManager.subscribe(setToasts);
  }, []);

  return {
    toasts,
    removeToast: toastManager.remove,
    toast: (message: string, type: ToastType = 'info', description?: string) => toastManager.add({ message, type, description }),
    success: (message: string, description?: string) => toastManager.add({ message, type: 'success', description }),
    error: (message: string, description?: string) => toastManager.add({ message, type: 'error', description }),
    warning: (message: string, description?: string) => toastManager.add({ message, type: 'warning', description }),
    info: (message: string, description?: string) => toastManager.add({ message, type: 'info', description }),
  };
}

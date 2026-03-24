export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  description?: string;
}

type Listener = (toasts: ToastMessage[]) => void;
let toasts: ToastMessage[] = [];
let listeners: Listener[] = [];

export const toastManager = {
  subscribe(listener: Listener) {
    listeners.push(listener);
    listener(toasts);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  },
  add(toast: Omit<ToastMessage, 'id'>) {
    const id = Math.random().toString(36).substring(2, 9);
    toasts = [...toasts, { ...toast, id }];
    listeners.forEach((l) => l(toasts));
    setTimeout(() => this.remove(id), 5000);
  },
  remove(id: string) {
    toasts = toasts.filter((t) => t.id !== id);
    listeners.forEach((l) => l(toasts));
  },
};

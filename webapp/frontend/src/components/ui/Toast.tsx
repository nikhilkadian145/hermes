import { clsx } from 'clsx';
import { CheckCircle, WarningCircle, Info, XCircle, X } from '@phosphor-icons/react';
import { useToast } from '../../hooks/useToast';
import type { ToastMessage } from '../../utils/toastManager';

export function ToastContainer() {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-[calc(var(--bottom-bar-height,64px)+16px)] left-1/2 -translate-x-1/2 md:bottom-6 md:left-auto md:right-6 md:translate-x-0 z-[9999] flex flex-col gap-3 pointer-events-none">
      {toasts.map(toast => (
        <Toast key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

function Toast({ toast, onClose }: { toast: ToastMessage, onClose: () => void }) {
  const icons = {
    success: <CheckCircle weight="fill" className="text-success shrink-0" size={20} />,
    error: <XCircle weight="fill" className="text-danger shrink-0" size={20} />,
    warning: <WarningCircle weight="fill" className="text-warning shrink-0" size={20} />,
    info: <Info weight="fill" className="text-accent shrink-0" size={20} />,
  };

  const borders = {
    success: "border-l-[3px] border-l-success",
    error: "border-l-[3px] border-l-danger",
    warning: "border-l-[3px] border-l-warning",
    info: "border-l-[3px] border-l-accent",
  };

  return (
    <div className={clsx(
      "bg-bg-surface border border-border rounded-lg shadow-md p-4 min-w-[280px] max-w-[360px] flex items-start gap-3 pointer-events-auto",
      "animate-[toast-in_200ms_ease]",
      borders[toast.type]
    )}>
      <style>{`
        @keyframes toast-in {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      {icons[toast.type]}
      <div className="flex-1 flex flex-col gap-1 mt-[1px]">
        <span className="text-[14px] font-medium text-text-primary leading-tight">{toast.message}</span>
        {toast.description && <span className="text-[13px] text-text-secondary mt-1">{toast.description}</span>}
      </div>
      <button onClick={onClose} className="text-text-muted hover:text-text-primary shrink-0 transition-colors">
        <X size={16} />
      </button>
    </div>
  );
}

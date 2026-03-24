import React, { useEffect, useState } from 'react';
import { WarningCircle, X, Warning } from '@phosphor-icons/react';
import { apiFetch } from '../api/client';

type ErrorEventDetail = {
  type: 'network_error' | 'server_error';
  message: string;
  status?: number;
};

export const GlobalErrorHandler: React.FC = () => {
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [serverErrors, setServerErrors] = useState<{id: string, message: string}[]>([]);

  useEffect(() => {
    const handleApiError = (event: CustomEvent<ErrorEventDetail>) => {
      const detail = event.detail;

      if (detail.type === 'network_error') {
        setNetworkError(detail.message);
      } else if (detail.type === 'server_error') {
        const id = Math.random().toString(36).substr(2, 9);
        setServerErrors(prev => [...prev, { id, message: detail.message }]);
        
        // Auto remove server toasts after 5 seconds
        setTimeout(() => {
          setServerErrors(prev => prev.filter(e => e.id !== id));
        }, 5000);
      }
    };

    window.addEventListener('hermes:api-error', handleApiError as EventListener);
    
    // Check if network is back up periodically if it's down
    let interval: ReturnType<typeof setInterval>;
    if (networkError) {
      interval = setInterval(async () => {
        try {
          const res = await fetch("http://localhost:8000/api/system/status");
          if (res.ok) setNetworkError(null);
        } catch {
          // Still down
        }
      }, 5000);
    }

    return () => {
      window.removeEventListener('hermes:api-error', handleApiError as EventListener);
      if (interval) clearInterval(interval);
    };
  }, [networkError]);

  if (!networkError && serverErrors.length === 0) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-[100] pointer-events-none flex flex-col items-center gap-2 p-4 pt-6">
      
      {/* Network Error Banner (Persistent, highest priority) */}
      {networkError && (
        <div className="w-full max-w-2xl bg-red-950/90 border border-red-500/50 shadow-[0_0_30px_rgba(239,68,68,0.2)] rounded-xl p-4 flex items-center gap-4 backdrop-blur-md pointer-events-auto shrink-0 animate-in slide-in-from-top-4 fade-in duration-300">
          <div className="bg-red-500/20 p-2 rounded-lg shrink-0">
            <WarningCircle weight="fill" className="text-red-500 w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-red-50 font-medium font-outfit">Connection Lost</h3>
            <p className="text-sm text-red-200/80 leading-relaxed mt-0.5">
              {networkError}
            </p>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="shrink-0 px-4 py-2 bg-red-500 hover:bg-red-400 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
          >
            Refresh
          </button>
        </div>
      )}

      {/* Server Error Toasts (Transient) */}
      {!networkError && serverErrors.map(err => (
        <div key={err.id} className="w-full max-w-sm bg-neutral-900 border border-neutral-700 shadow-xl rounded-xl p-3 flex items-start gap-3 backdrop-blur-md pointer-events-auto shrink-0 animate-in slide-in-from-top-4 fade-in duration-300">
          <div className="bg-orange-500/20 text-orange-400 p-1.5 rounded-lg shrink-0 mt-0.5">
            <Warning weight="fill" className="w-4 h-4" />
          </div>
          <div className="flex-1 py-1">
            <p className="text-sm text-neutral-200 break-words leading-relaxed">{err.message}</p>
          </div>
          <button 
            onClick={() => setServerErrors(prev => prev.filter(e => e.id !== err.id))}
            className="shrink-0 p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-md transition-colors"
          >
            <X weight="bold" className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}

    </div>
  );
};

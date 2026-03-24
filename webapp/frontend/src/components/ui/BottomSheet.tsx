import { ReactNode, useEffect, useState } from "react";
import { clsx } from "clsx";

interface BottomSheetProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
}

export function BottomSheet({ open, onClose, title, children }: BottomSheetProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (open) setMounted(true);
    else setTimeout(() => setMounted(false), 250);
  }, [open]);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
      return () => { document.body.style.overflow = ""; };
    }
  }, [open]);

  if (!mounted && !open) return null;

  return (
    <div className={clsx(
      "fixed inset-0 z-[300] flex items-end justify-center transition-opacity duration-200",
      open ? "opacity-100" : "opacity-0 pointer-events-none"
    )}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-[1px]" onClick={onClose} />
      
      <div 
        className={clsx(
          "relative bg-bg-surface w-full max-h-[90vh] rounded-t-xl transition-transform duration-250 flex flex-col",
          open ? "translate-y-0" : "translate-y-full"
        )}
      >
        <div className="flex flex-col items-center pt-3 pb-2 shrink-0" onTouchStart={onClose} onClick={onClose} style={{ cursor: 'pointer' }}>
          <div className="w-10 h-1.5 bg-border rounded-full" />
          {title && <h3 className="mt-4 text-heading text-text-primary px-4 w-full text-center">{title}</h3>}
        </div>
        
        <div className="px-4 pb-6 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
}

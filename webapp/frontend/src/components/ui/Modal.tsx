import { ReactNode, useEffect, useState } from "react";
import { clsx } from "clsx";
import { X } from "@phosphor-icons/react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  size?: 'sm' | 'md' | 'lg' | 'full';
  children: ReactNode;
  footer?: ReactNode;
}

export function Modal({ open, onClose, title, size = 'md', children, footer }: ModalProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (open) setMounted(true);
    else setTimeout(() => setMounted(false), 200); // Wait for exit animation
  }, [open]);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
      const handleEsc = (e: KeyboardEvent) => {
        if (e.key === "Escape") onClose();
      };
      window.addEventListener("keydown", handleEsc);
      return () => {
        document.body.style.overflow = "";
        window.removeEventListener("keydown", handleEsc);
      };
    }
  }, [open, onClose]);

  if (!mounted && !open) return null;

  const sizes = {
    sm: "md:w-[400px]",
    md: "md:w-[600px]",
    lg: "md:w-[800px]",
    full: "md:w-[100vw] md:h-[100vh] md:max-w-none md:max-h-none md:rounded-none",
  };

  return (
    <div 
      className={clsx(
        "fixed inset-0 z-[200] flex items-center justify-center bg-black/40 transition-opacity duration-150",
        open ? "opacity-100" : "opacity-0 pointer-events-none"
      )}
      onClick={onClose}
    >
      <div 
        className={clsx(
          "bg-bg-surface flex flex-col shadow-lg transition-transform duration-150",
          "w-full h-full md:h-auto max-w-[100vw] max-h-[100vh] md:max-w-[calc(100vw-48px)] md:max-h-[calc(100vh-96px)]",
          "rounded-t-[16px] md:rounded-[16px] fixed bottom-0 left-0 md:relative overflow-hidden",
          sizes[size],
          open ? "translate-y-0 md:scale-100" : "translate-y-full md:translate-y-0 md:scale-95"
        )}
        onClick={e => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-6 pb-4 shrink-0">
          <h2 className="text-[20px] font-semibold leading-[1.3] text-text-primary">{title}</h2>
          <button 
            onClick={onClose}
            className="text-text-secondary hover:text-text-primary transition-colors p-1"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="px-6 pb-6 overflow-y-auto grow">
          {children}
        </div>
        
        {footer && (
          <div className="px-6 py-5 border-t border-border bg-bg-surface shrink-0">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

import { ReactNode } from "react";
import { clsx } from "clsx";

interface TooltipProps {
  content: ReactNode;
  delay?: number;
  children: ReactNode;
  className?: string;
}

export function Tooltip({ content, delay = 600, children, className }: TooltipProps) {
  return (
    <div className={clsx("group relative inline-flex", className)}>
      {children}
      <div 
        className={clsx(
          "pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-[200px]",
          "opacity-0 transition-opacity whitespace-normal break-words shadow-sm",
          "bg-text-primary text-text-inverse text-[12px] px-2 py-1 rounded-[4px] z-50",
          "md:group-hover:opacity-100 hidden md:block" // Hidden on mobile, shows on hover on desktop
        )}
        style={{ transitionDelay: `${delay}ms` }}
      >
        {content}
      </div>
    </div>
  );
}

import type { ReactNode } from 'react';
import { Breadcrumbs } from './Breadcrumbs';

export interface PageHeaderProps {
  title: string;
  actions?: ReactNode;
  breadcrumbs?: boolean;
}

export function PageHeader({ title, actions, breadcrumbs = true }: PageHeaderProps) {
  return (
    <>
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6 md:mb-8">
        <div>
          {breadcrumbs && <Breadcrumbs />}
          <h1 className="text-[22px] md:text-[28px] font-bold leading-[1.2] text-text-primary tracking-tight">
            {title}
          </h1>
        </div>
        
        {actions && (
          <div className="hidden md:flex items-center gap-3">
            {actions}
          </div>
        )}
      </div>

      {actions && (
        <div className="md:hidden fixed bottom-[var(--bottom-bar-height,64px)] inset-x-0 p-4 bg-bg-surface border-t border-border z-10 flex items-center gap-3 shadow-[0_-4px_12px_rgba(0,0,0,0.05)]">
          {actions}
        </div>
      )}
    </>
  );
}

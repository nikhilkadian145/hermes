import { HTMLAttributes } from 'react';
import { clsx } from 'clsx';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  clickable?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ clickable = false, padding = 'md', className, ...props }: CardProps) {
  const paddings = {
    none: 'p-0',
    sm: 'p-4',
    md: 'p-4 lg:p-6',
    lg: 'p-6 lg:p-8',
  };

  return (
    <div
      className={clsx(
        "bg-bg-surface border border-border rounded-lg shadow-sm",
        paddings[padding],
        clickable && "hover:border-border-strong hover:shadow-md cursor-pointer transition-all duration-200",
        className
      )}
      {...props}
    />
  );
}

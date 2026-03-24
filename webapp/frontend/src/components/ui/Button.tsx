import { ButtonHTMLAttributes, ReactNode } from 'react';
import { clsx } from 'clsx';
import { CircleNotch } from '@phosphor-icons/react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  className,
  children,
  ...props
}: ButtonProps) {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-md transition-colors duration-120 disabled:opacity-45 disabled:cursor-not-allowed";
  
  const variants = {
    primary: "bg-accent text-text-inverse hover:bg-accent-hover border-none",
    secondary: "bg-bg-surface text-text-primary border border-border hover:bg-bg-overlay hover:border-border-strong",
    ghost: "bg-transparent text-accent hover:bg-accent-subtle border-none",
    danger: "bg-danger text-text-inverse hover:brightness-90 border-none",
  };

  const sizes = {
    sm: "h-[28px] px-[10px] text-[12px]",
    md: "h-[36px] px-[14px] text-[14px]",
    lg: "h-[44px] px-[18px] text-[14px]"
  };

  return (
    <button
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        fullWidth && "w-full",
        className
      )}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && (
        <CircleNotch weight="bold" className="min-w-4 min-h-4 w-4 h-4 animate-spin mr-2" />
      )}
      {!loading && icon && iconPosition === 'left' && <span className="mr-2 flex items-center">{icon}</span>}
      {children}
      {!loading && icon && iconPosition === 'right' && <span className="ml-2 flex items-center">{icon}</span>}
    </button>
  );
}

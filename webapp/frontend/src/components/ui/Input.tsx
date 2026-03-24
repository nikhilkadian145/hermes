import { InputHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, id, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1 w-full">
        {label && (
          <label htmlFor={id} className="text-[12px] font-medium leading-[1.4] text-text-secondary">
            {label}
          </label>
        )}
        <input
          id={id}
          ref={ref}
          className={clsx(
            "h-[44px] lg:h-[36px] px-3 bg-bg-subtle border rounded-md text-text-primary font-sans text-[14px] w-full transition-all duration-120 placeholder:text-text-muted focus:outline-none focus:border-border-strong focus:ring-[3px] focus:ring-accent-subtle",
            error ? "border-danger" : "border-border",
            className
          )}
          {...props}
        />
        {error && (
          <span className="text-[11px] font-normal leading-[1.4] text-danger">
            {error}
          </span>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';

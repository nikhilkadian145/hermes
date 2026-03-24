import { InputHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';
import { CalendarBlank } from '@phosphor-icons/react';

export interface DatePickerProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: string;
}

export const DatePicker = forwardRef<HTMLInputElement, DatePickerProps>(
  ({ label, error, className, id, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1 w-full relative">
        {label && (
          <label htmlFor={id} className="text-[12px] font-medium leading-[1.4] text-text-secondary">
            {label}
          </label>
        )}
        <div className="relative">
          <input
            id={id}
            ref={ref}
            type="date"
            className={clsx(
              "h-[44px] lg:h-[36px] px-3 pr-10 bg-bg-subtle border rounded-md text-text-primary font-sans text-[14px] w-full transition-all duration-120 focus:outline-none focus:border-border-strong focus:ring-[3px] focus:ring-accent-subtle",
              error ? "border-danger" : "border-border",
              className
            )}
            {...props}
          />
          <CalendarBlank className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" size={18} />
        </div>
        {error && (
          <span className="text-[11px] font-normal leading-[1.4] text-danger">
            {error}
          </span>
        )}
      </div>
    );
  }
);
DatePicker.displayName = 'DatePicker';

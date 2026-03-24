import { SelectHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';
import { CaretDown } from '@phosphor-icons/react';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: SelectOption[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, className, id, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1 w-full relative">
        {label && (
          <label htmlFor={id} className="text-[12px] font-medium leading-[1.4] text-text-secondary">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            id={id}
            ref={ref}
            className={clsx(
              "h-[44px] lg:h-[36px] px-3 pr-10 bg-bg-subtle border rounded-md text-text-primary font-sans text-[14px] w-full transition-all duration-120 focus:outline-none focus:border-border-strong focus:ring-[3px] focus:ring-accent-subtle appearance-none",
              error ? "border-danger" : "border-border",
              className
            )}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <CaretDown className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" size={16} weight="bold" />
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
Select.displayName = 'Select';

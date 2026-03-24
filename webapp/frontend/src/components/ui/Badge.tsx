import { clsx } from 'clsx';

export type BadgeStatus = 'paid' | 'sent' | 'draft' | 'overdue' | 'due-soon' | 'processing' | 'review' | 'error' | 'void' | 'finalized' | 'custom';

export interface BadgeProps {
  status: BadgeStatus;
  label?: string;
  size?: 'sm' | 'md';
  className?: string;
}

export function Badge({ status, label, className }: BadgeProps) {
  const statusColors: Record<Exclude<BadgeStatus, 'custom'>, string> = {
    paid: 'bg-success-bg text-success',
    sent: 'bg-accent-subtle text-accent',
    draft: 'bg-neutral-bg text-neutral',
    overdue: 'bg-danger-bg text-danger',
    'due-soon': 'bg-warning-bg text-warning',
    processing: 'bg-accent-subtle text-accent',
    review: 'bg-warning-bg text-warning',
    error: 'bg-danger-bg text-danger',
    void: 'bg-neutral-bg text-neutral',
    finalized: 'bg-success-bg text-success',
  };

  const appliedClass = status === 'custom' ? '' : statusColors[status];
  
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full px-2 py-[2px] text-[11px] font-medium uppercase tracking-[0.05em]",
        appliedClass,
        status === 'processing' && 'animate-pulse',
        className
      )}
    >
      {label || status.replace('-', ' ')}
    </span>
  );
}

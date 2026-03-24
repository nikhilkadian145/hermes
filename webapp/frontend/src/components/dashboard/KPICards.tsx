import { Card } from '../ui/Card';
import { Skeleton } from '../ui/Skeleton';
import { formatCurrencyShort } from '../../utils/format';
import { ArrowUpRight, ArrowDownRight } from '@phosphor-icons/react';
import { clsx } from 'clsx';
import { useDashboardKPIs } from '../../hooks/useDashboardKPIs';

export function KPICards() {
  const { data, loading } = useDashboardKPIs();

  if (loading || !data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <Skeleton key={i} height={140} className="rounded-lg" />
        ))}
      </div>
    );
  }

  const kpis = [
    {
      label: 'Revenue (MTD)',
      value: formatCurrencyShort(data.revenue_mtd),
      delta: ((data.revenue_mtd - data.revenue_prev_month) / data.revenue_prev_month) * 100,
      goodDirection: 'up',
    },
    {
      label: 'Expenses (MTD)',
      value: formatCurrencyShort(data.expenses_mtd),
      delta: ((data.expenses_mtd - data.expenses_prev_month) / data.expenses_prev_month) * 100,
      goodDirection: 'down',
    },
    {
      label: 'Net Profit (MTD)',
      value: formatCurrencyShort(data.net_profit_mtd),
      delta: (((data.revenue_mtd - data.expenses_mtd) - (data.revenue_prev_month - data.expenses_prev_month)) / Math.abs(data.revenue_prev_month - data.expenses_prev_month)) * 100,
      goodDirection: 'up',
    },
    {
      label: 'Outstanding Payables',
      value: formatCurrencyShort(data.outstanding_receivables),
      delta: ((data.outstanding_receivables - data.outstanding_prev_week) / data.outstanding_prev_week) * 100,
      goodDirection: 'down',
    },
    {
      label: 'Overdue Invoices',
      value: `${data.overdue_count} (${formatCurrencyShort(data.overdue_total)})`,
      isBad: data.overdue_count > 0,
      delta: 0,
      goodDirection: 'down',
    },
    {
      label: 'Est. GST Liability',
      value: formatCurrencyShort(data.gst_liability_est),
      delta: 5.2, // mock
      goodDirection: 'down',
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6 md:overflow-visible overflow-x-auto pb-2 md:pb-0 snap-x">
      {kpis.map((kpi, idx) => {
        const isUp = kpi.delta > 0;
        const colorClass = kpi.goodDirection === 'up' 
          ? (isUp ? 'text-success' : 'text-danger')
          : (isUp ? 'text-danger' : 'text-success');

        return (
          <Card 
            key={idx} 
            className={clsx(
              "flex flex-col gap-2 min-w-[240px] snap-center",
              kpi.isBad && "border-l-4 border-l-danger"
            )}
            padding="md"
          >
            <div className="text-[13px] text-text-secondary uppercase tracking-[0.05em] font-medium">
              {kpi.label}
            </div>
            
            <div className="text-[32px] font-bold text-text-primary leading-none t-mono">
              {kpi.value}
            </div>
            
            {(kpi.delta !== 0) && (
              <div className={clsx("flex items-center gap-1 text-[12px] font-medium mt-auto", colorClass)}>
                {isUp ? <ArrowUpRight size={14} weight="bold" /> : <ArrowDownRight size={14} weight="bold" />}
                {Math.abs(kpi.delta).toFixed(1)}% <span className="text-text-muted font-normal ml-1">vs last period</span>
              </div>
            )}
            {(kpi.delta === 0) && (
               <div className="text-[12px] text-text-muted mt-auto">Action required</div>
            )}
          </Card>
        );
      })}
    </div>
  );
}

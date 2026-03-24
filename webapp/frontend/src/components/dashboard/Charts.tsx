import { useState, useEffect } from 'react';
import { 
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, 
  PieChart, Pie, Cell, BarChart, Bar 
} from 'recharts';
import { formatCurrencyShort, formatCurrency } from '../../utils/format';
import { clsx } from 'clsx';
import { Card } from '../ui/Card';
import { useApi } from '../../hooks/useApi';

const DONUT_COLORS = [
  'var(--accent)', 
  'var(--success)', 
  'var(--warning)', 
  'var(--danger)', 
  'var(--text-secondary)', 
  'var(--bg-overlay)'
];

const STATUS_COLORS = {
  paid: 'var(--success)',
  sent: 'var(--accent)',
  overdue: 'var(--danger)',
  draft: 'var(--neutral)',
};

const CustomLineTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-bg-surface border border-border shadow-lg rounded-md p-3 text-[13px] z-[100]">
        <div className="font-semibold mb-2 text-text-primary">{label}</div>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex justify-between gap-4 mb-1">
            <span style={{ color: entry.stroke || entry.fill }} className="font-medium">{entry.name}:</span>
            <span className="text-text-primary font-mono">{formatCurrency(entry.value)}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function RevenueExpenseChart() {
  const [period, setPeriod] = useState<3 | 6 | 12>(12);
  const { data } = useApi<any[]>(`/dashboard/charts/revenue-expenses?months=${period}`);
  const safeData = data || [];

  return (
    <Card className="flex flex-col h-full col-span-1 lg:col-span-2">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-bold text-[16px]">Revenue vs Expenses</h3>
        <div className="flex bg-bg-overlay rounded-md p-0.5">
          {[3, 6, 12].map(m => (
            <button
              key={m}
              onClick={() => setPeriod(m as any)}
              className={clsx(
                "px-3 py-1 text-[12px] font-medium rounded-sm transition-colors",
                period === m ? "bg-accent-subtle text-accent" : "text-text-secondary hover:text-text-primary"
              )}
            >
              {m}M
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex-1 min-h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={safeData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} dy={10} />
            <YAxis tickFormatter={(val) => formatCurrencyShort(val)} axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
            <RechartsTooltip content={<CustomLineTooltip />} cursor={{ stroke: 'var(--border)', strokeWidth: 1, strokeDasharray: '4 4' }} />
            <Line type="monotone" name="Revenue" dataKey="revenue" stroke="var(--accent)" strokeWidth={3} dot={false} activeDot={{ r: 6, strokeWidth: 0, fill: 'var(--accent)' }} />
            <Line type="monotone" name="Expenses" dataKey="expenses" stroke="var(--danger)" strokeWidth={3} dot={false} activeDot={{ r: 6, strokeWidth: 0, fill: 'var(--danger)' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export function ExpenseDonutChart() {
  const { data } = useApi<any[]>('/dashboard/charts/expense-breakdown?month=current');
  const safeData = data || [];

  const total = safeData.reduce((acc, curr) => acc + curr.total, 0);

  return (
    <Card className="flex flex-col h-full">
      <h3 className="font-bold text-[16px] mb-4">Expense Breakdown</h3>
      {safeData.length > 0 ? (
        <div className="flex-1 relative min-h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={safeData}
                innerRadius={65}
                outerRadius={90}
                paddingAngle={2}
                dataKey="total"
                stroke="none"
              >
                {safeData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={DONUT_COLORS[index % DONUT_COLORS.length]} />
                ))}
              </Pie>
              <RechartsTooltip 
                formatter={(value: number) => [formatCurrency(value), 'Total']} 
                contentStyle={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border)', borderRadius: '8px', fontSize: '13px' }}
                itemStyle={{ color: 'var(--text-primary)' }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-[12px] text-text-muted font-medium mb-1">Total</span>
            <span className="text-[18px] font-bold text-text-primary t-mono tracking-tighter">{formatCurrencyShort(total)}</span>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-text-muted text-[13px]">No expenses logged</div>
      )}
      <div className="flex flex-wrap gap-x-3 gap-y-2 mt-4 text-[12px] justify-center">
        {safeData.map((entry, index) => (
          <div key={index} className="flex items-center gap-1.5 min-w-[30%]">
            <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: DONUT_COLORS[index % DONUT_COLORS.length] }} />
            <span className="text-text-secondary truncate">{entry.category}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

export function InvoiceStatusChart() {
  const { data } = useApi<any[]>('/dashboard/charts/invoice-status?months=6');
  const safeData = data || [];

  return (
    <Card className="flex flex-col h-full">
      <h3 className="font-bold text-[16px] mb-6">Invoice Status</h3>
      <div className="flex-1 min-h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={safeData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} dy={10} />
            <RechartsTooltip 
              cursor={{ fill: 'var(--bg-overlay)' }}
              contentStyle={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border)', borderRadius: '8px', fontSize: '13px' }}
              itemStyle={{ color: 'var(--text-primary)' }}
            />
            <Bar dataKey="draft" name="Draft" stackId="a" fill={STATUS_COLORS.draft} radius={[0, 0, 4, 4]} barSize={32} />
            <Bar dataKey="sent" name="Sent" stackId="a" fill={STATUS_COLORS.sent} />
            <Bar dataKey="paid" name="Paid" stackId="a" fill={STATUS_COLORS.paid} />
            <Bar dataKey="overdue" name="Overdue" stackId="a" fill={STATUS_COLORS.overdue} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex items-center justify-center gap-4 mt-6 text-[12px]">
        <div className="flex items-center gap-1.5 text-text-secondary"><div className="w-2.5 h-2.5 rounded-full bg-success"></div> Paid</div>
        <div className="flex items-center gap-1.5 text-text-secondary"><div className="w-2.5 h-2.5 rounded-full bg-accent"></div> Sent</div>
        <div className="flex items-center gap-1.5 text-text-secondary"><div className="w-2.5 h-2.5 rounded-full bg-danger"></div> Overdue</div>
      </div>
    </Card>
  );
}

import { useApi } from './useApi';

export interface KPIResponse {
  revenue_mtd: number;
  expenses_mtd: number;
  net_profit_mtd: number;
  outstanding_receivables: number;
  outstanding_count: number;
  overdue_total: number;
  overdue_count: number;
  gst_liability_est: number;
  revenue_prev_month: number;
  expenses_prev_month: number;
  outstanding_prev_week: number;
}

export function useDashboardKPIs() {
  return useApi<KPIResponse>('/dashboard/kpis', {
    pollingIntervalMs: 60000, // Refetch every 60s
  });
}

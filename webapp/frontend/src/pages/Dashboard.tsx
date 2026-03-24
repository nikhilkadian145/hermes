import { PageHeader } from '../components/layout/PageHeader';
import { QuickActions } from '../components/dashboard/QuickActions';
import { KPICards } from '../components/dashboard/KPICards';
import { RevenueExpenseChart, ExpenseDonutChart, InvoiceStatusChart } from '../components/dashboard/Charts';
import { ActivityFeed } from '../components/dashboard/ActivityFeed';

export function Dashboard() {
  return (
    <div className="animate-[fade-in_300ms_ease]">
      <PageHeader 
        title="Good Morning, User." 
        breadcrumbs={false}
      />
      
      <QuickActions />
      <KPICards />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <RevenueExpenseChart />
        <ExpenseDonutChart />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6 lg:mb-0">
        <div className="lg:col-span-2 h-[400px]">
          <ActivityFeed />
        </div>
        <div className="lg:col-span-1 h-[400px]">
          <InvoiceStatusChart />
        </div>
      </div>
    </div>
  );
}

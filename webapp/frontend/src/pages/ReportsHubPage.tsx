import { useNavigate } from "react-router-dom";
import { PageHeader } from "../components/layout/PageHeader";

const reportConfig = [
  {
    title: "Financial Reports",
    items: [
      { id: "pl", name: "Profit & Loss", desc: "Income, expenses, and net profit over a period.", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
      { id: "balance-sheet", name: "Balance Sheet", desc: "Snapshot of assets, liabilities, and equity.", icon: "M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" },
      { id: "cash-flow", name: "Cash Flow", desc: "Inflows and outflows of cash categorized.", icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
      { id: "trial-balance", name: "Trial Balance", desc: "Closing balances of all ledger accounts.", icon: "M4 6h16M4 10h16M4 14h16M4 18h16" },
      { id: "general-ledger", name: "General Ledger", desc: "Detailed transactions for all accounts.", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" },
      { id: "day-book", name: "Day Book", desc: "Daily chronological record of transactions.", icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" },
    ]
  },
  {
    title: "GST Reports",
    items: [
      { id: "gstr-1", name: "GSTR-1", desc: "Details of outward supplies of goods or services.", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
      { id: "gstr-2b", name: "GSTR-2B Reconciliation", desc: "Auto-drafted ITC statement matching.", icon: "M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" },
      { id: "gst-liability", name: "GST Liability", desc: "Summary of gross GST output vs. ITC.", icon: "M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" },
      { id: "hsn-summary", name: "HSN/SAC Summary", desc: "Summary of outward supplies by HSN code.", icon: "M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" },
    ]
  },
  {
    title: "Receivables",
    items: [
      { id: "receivables-aging", name: "Accounts Receivable Aging", desc: "Unpaid invoices bucketed by days overdue.", icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" },
      { id: "customer-outstanding", name: "Customer Outstanding", desc: "Total amounts owed per client.", icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" },
    ]
  },
  {
    title: "Payables & Expenses",
    items: [
      { id: "payables-aging", name: "Accounts Payable Aging", desc: "Unpaid bills bucketed by days overdue.", icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" },
      { id: "expense-category", name: "Expenses by Category", desc: "Breakdown of operating costs.", icon: "M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" },
    ]
  },
  {
    title: "HERMES Intelligence",
    items: [
      { id: "anomaly", name: "Anomaly Report", desc: "AI-detected irregularities in transactions.", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
      { id: "audit-trail", name: "Audit Trail", desc: "Log of critical system actions and modifications.", icon: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" },
    ]
  }
];

export function ReportsHubPage() {
  const navigate = useNavigate();

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto w-[calc(100vw-16rem)] pl-32 pr-20 relative -left-8 py-8">
      <div className="mb-8">
        <PageHeader title="Reports Hub" />
        <p className="text-text-secondary mt-2">Comprehensive financial, tax, and operational reports.</p>
      </div>

      <div className="space-y-12 pb-16">
        {reportConfig.map((section, idx) => (
          <section key={idx}>
            <h2 className="text-lg font-bold font-display text-text-base border-b border-border pb-3 mb-6">
              {section.title}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {section.items.map((item) => (
                <div 
                  key={item.id}
                  onClick={() => navigate(`/reports/${item.id}`)}
                  className="bg-bg-surface border border-border rounded-xl p-5 hover:border-accent hover:shadow-sm cursor-pointer transition-all group flex flex-col h-full"
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-12 h-12 rounded-lg bg-bg-subtle text-accent flex items-center justify-center shrink-0 group-hover:bg-accent/10 transition-colors">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                        <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                      </svg>
                    </div>
                    <div>
                      <h3 className="font-semibold text-text-base group-hover:text-accent transition-colors">{item.name}</h3>
                      <p className="text-xs text-text-muted mt-1 leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                  
                  <div className="mt-auto pt-4 border-t border-border flex items-center justify-between">
                    <span className="text-xs text-text-muted">Generated instantly</span>
                    <span className="text-xs font-semibold text-accent flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                      Run Report
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}

        <section className="bg-bg-surface border border-accent/20 rounded-xl p-6 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold font-display text-text-base">Custom Report Builder</h2>
            <p className="text-sm text-text-secondary mt-1">Design a customized report format by selecting specific metrics and columns.</p>
          </div>
          <button onClick={() => navigate('/reports/custom')} className="h-10 px-5 bg-bg-subtle text-text-base font-semibold text-sm rounded-lg hover:bg-bg-overlay border border-border transition-colors flex items-center gap-2">
            Build Custom
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </button>
        </section>
      </div>
    </div>
  );
}

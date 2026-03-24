import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";

export function ReportViewerPage() {
  const { type } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Date controls
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const needsDateRange = ["pl", "cash-flow", "general-ledger", "expense-category"].includes(type || "");
  const needsAsOfDate = ["balance-sheet", "trial-balance"].includes(type || "");

  const getReportName = () => {
    return (type || "").split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = `http://localhost:8000/api/reports/${type}`;
      
      const params = new URLSearchParams();
      if (needsDateRange) {
        if (fromDate) params.append("from_date", fromDate);
        if (toDate) params.append("to_date", toDate);
      } else if (needsAsOfDate && fromDate) {
         params.append("as_of", fromDate);
      }
      
      const q = params.toString();
      if (q) url += `?${q}`;

      const res = await fetch(url);
      if (res.ok) {
        setData(await res.json());
      } else {
        // Fallback to generic report if endpoint not fully implemented
        const fallback = await apiFetch(`/reports/generic/${type}`);
        if (fallback.ok) setData(await fallback.json());
        else setError("Failed to load report data.");
      }
    } catch (err) {
      setError("Network or server error.");
    } finally {
      setLoading(false);
    }
  };

  // Auto-run on load if no mandatory params, or just run anyway for demo
  useEffect(() => {
    fetchReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type]);

  const handlePrint = () => {
    window.print();
  };

  const handleExport = async (format: 'pdf' | 'excel') => {
    try {
      const res = await apiFetch(`/reports/${type}/${format}`, { method: "POST" });
      const data = await res.json();
      alert(`Export requested. Format: ${format}. Result URL: ${data.url}`);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base w-[calc(100vw-16rem)] pl-32 pr-20 relative -left-8 pt-6 pb-20">
      <div className="flex items-center gap-3 mb-6 no-print">
        <button onClick={() => navigate("/reports")} className="p-2 -ml-2 text-text-muted hover:bg-bg-overlay hover:text-text-base rounded transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
        </button>
        <h1 className="text-xl font-bold font-display text-text-base">{getReportName()}</h1>
      </div>

      <div className="bg-bg-surface border border-border rounded-xl p-4 mb-6 flex flex-wrap items-end gap-4 no-print">
        {needsDateRange && (
          <>
            <div>
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">From Date</label>
              <input type="date" className="h-9 px-3 bg-bg-base border border-border rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-accent" value={fromDate} onChange={e => setFromDate(e.target.value)} />
            </div>
            <div>
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">To Date</label>
              <input type="date" className="h-9 px-3 bg-bg-base border border-border rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-accent" value={toDate} onChange={e => setToDate(e.target.value)} />
            </div>
            <Button variant="secondary" onClick={() => {
              const d = new Date();
              setToDate(d.toISOString().split('T')[0]);
              d.setMonth(d.getMonth()-1);
              setFromDate(d.toISOString().split('T')[0]);
            }}>Last 30 Days</Button>
          </>
        )}
        {needsAsOfDate && (
          <div>
            <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">As Of Date</label>
            <input type="date" className="h-9 px-3 bg-bg-base border border-border rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-accent" value={fromDate} onChange={e => setFromDate(e.target.value)} />
          </div>
        )}
        <Button variant="primary" onClick={fetchReport} loading={loading}>Run Report</Button>
      </div>

      <div className="flex-1 bg-white dark:bg-zinc-100 rounded-xl shadow-sm border border-border overflow-y-auto p-10 text-zinc-900 print:shadow-none print:border-none print:p-0">
        {loading ? (
          <div className="flex items-center justify-center h-64 text-zinc-500 animate-pulse">Generating Report...</div>
        ) : error ? (
          <div className="text-danger p-8 bg-danger/10 rounded-lg">{error}</div>
        ) : data ? (
          <div className="max-w-4xl mx-auto font-sans">
            {/* Standard Report Header */}
            <div className="text-center mb-10 border-b-2 border-zinc-200 pb-6">
              <h2 className="text-2xl font-bold uppercase tracking-widest text-zinc-900">{data.title || getReportName()}</h2>
              <p className="text-zinc-500 mt-2">
                {needsDateRange ? `Period: ${fromDate || 'Start'} to ${toDate || 'Present'}` : 
                 needsAsOfDate ? `As of: ${fromDate || 'Today'}` : 'Current Snapshot'}
              </p>
            </div>

            {/* P&L Render Logic */}
            {data.sections && (
              <div className="space-y-8">
                {data.sections.map((sec: any, i: number) => (
                  <div key={i}>
                    <h3 className="text-lg font-bold border-b border-zinc-300 pb-2 mb-3">{sec.name}</h3>
                    <div className="space-y-2">
                      {sec.items.map((item: any, j: number) => (
                        <div key={j} className="flex justify-between text-sm py-1">
                          <span>{item.name}</span>
                          <span className="font-mono">{item.amount.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</span>
                        </div>
                      ))}
                      <div className="flex justify-between font-bold text-sm bg-zinc-100 p-2 mt-2">
                        <span>Total {sec.name}</span>
                        <span className="font-mono">{sec.subtotal.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</span>
                      </div>
                    </div>
                  </div>
                ))}
                {data.net_income !== undefined && (
                  <div className="flex justify-between font-bold text-lg bg-zinc-200 p-3 mt-6 border-t-2 border-zinc-400">
                    <span>Net Income</span>
                    <span className="font-mono">{data.net_income.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</span>
                  </div>
                )}
              </div>
            )}

            {/* Balance Sheet Render Logic */}
            {data.assets && (
              <div className="grid grid-cols-2 gap-12">
                <div>
                  <h3 className="text-lg font-bold border-b border-zinc-300 pb-2 mb-3">Assets</h3>
                  {data.assets.map((a: any, i: number) => (
                    <div key={i} className="flex justify-between text-sm py-1">
                      <span>{a.name}</span>
                      <span className="font-mono">{a.amount.toLocaleString('en-IN')}</span>
                    </div>
                  ))}
                  <div className="flex justify-between font-bold text-sm bg-zinc-100 p-2 mt-2">
                    <span>Total Assets</span>
                    <span className="font-mono">{data.total_assets.toLocaleString('en-IN')}</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-bold border-b border-zinc-300 pb-2 mb-3">Liabilities & Equity</h3>
                  <div className="mb-4">
                    <h4 className="font-semibold text-xs text-zinc-500 uppercase tracking-wider mb-2">Liabilities</h4>
                    {data.liabilities.map((l: any, i: number) => (
                      <div key={i} className="flex justify-between text-sm py-1">
                        <span>{l.name}</span>
                        <span className="font-mono">{l.amount.toLocaleString('en-IN')}</span>
                      </div>
                    ))}
                  </div>
                  <div>
                    <h4 className="font-semibold text-xs text-zinc-500 uppercase tracking-wider mb-2">Equity</h4>
                    {data.equity.map((e: any, i: number) => (
                      <div key={i} className="flex justify-between text-sm py-1">
                        <span>{e.name}</span>
                        <span className="font-mono">{e.amount.toLocaleString('en-IN')}</span>
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-between font-bold text-sm bg-zinc-100 p-2 mt-6">
                    <span>Total Liab. & Equity</span>
                    <span className="font-mono">{(data.total_liabilities + data.total_equity).toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Aging Render Logic */}
            {data.buckets && (
              <div>
                <table className="w-full text-sm text-left border-collapse">
                  <thead>
                    <tr className="bg-zinc-100">
                      <th className="p-3 border-b border-zinc-300">0-30 Days</th>
                      <th className="p-3 border-b border-zinc-300">31-60 Days</th>
                      <th className="p-3 border-b border-zinc-300">61-90 Days</th>
                      <th className="p-3 border-b border-zinc-300">90+ Days</th>
                      <th className="p-3 border-b border-zinc-300 text-right">Total Outstanding</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="p-3 border-b border-zinc-200 font-mono">{data.buckets["0-30"].toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</td>
                      <td className="p-3 border-b border-zinc-200 font-mono">{data.buckets["31-60"].toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</td>
                      <td className="p-3 border-b border-zinc-200 font-mono">{data.buckets["61-90"].toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</td>
                      <td className="p-3 border-b border-zinc-200 font-mono text-danger font-semibold">{data.buckets["90+"].toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</td>
                      <td className="p-3 border-b border-zinc-200 text-right font-mono font-bold text-lg">{data.total.toLocaleString('en-IN', { style: 'currency', currency: 'INR' })}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {/* Generic Table Fallback */}
            {data.data && Array.isArray(data.data) && (
              <table className="w-full text-sm text-left border-collapse mt-4">
                <thead>
                  <tr className="bg-zinc-100 border-b-2 border-zinc-300">
                    {Object.keys(data.data[0]).map(k => (
                      <th key={k} className="p-3 font-semibold text-zinc-700">{k}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.data.map((row: any, i: number) => (
                    <tr key={i} className="border-b border-zinc-200">
                      {Object.values(row).map((v: any, j: number) => (
                        <td key={j} className={`p-3 ${typeof v === 'number' ? 'font-mono' : ''}`}>
                          {typeof v === 'number' ? v.toLocaleString('en-IN') : v}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Footer */}
            <div className="mt-16 text-center text-xs text-zinc-400 border-t border-zinc-100 pt-4">
              Generated by HERMES Financial System on {new Date().toLocaleString()}
            </div>
          </div>
        ) : null}
      </div>

      <div className="fixed bottom-0 left-64 right-0 h-16 bg-bg-surface border-t border-border flex items-center justify-between px-8 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] z-20 no-print">
        <span className="text-sm font-medium text-text-secondary">Report ready to share or export</span>
        <div className="flex items-center gap-3">
          <Button variant="ghost" onClick={handlePrint}>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" /></svg>
            Print
          </Button>
          <Button variant="secondary" onClick={() => handleExport('excel')}>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
            Download Excel
          </Button>
          <Button variant="primary" onClick={() => handleExport('pdf')}>
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            Download PDF
          </Button>
        </div>
      </div>
    </div>
  );
}

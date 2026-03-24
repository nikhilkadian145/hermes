import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { Badge } from "../components/ui/Badge";

export function AnomalyReportPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch("/reports/anomaly-report");
        if (res.ok) setData(await res.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  const summary = data?.summary || { flagged: 0, resolved: 0, dismissed: 0, total: 0 };
  const anomalies = data?.anomalies || [];

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate("/reports")} className="p-2 -ml-2 text-text-muted hover:bg-bg-overlay hover:text-text-base rounded transition-colors" title="Back to Reports">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
        </button>
        <h1 className="text-xl font-bold font-display text-text-base">Anomaly Report</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total Flagged", val: summary.total, color: "text-text-base" },
          { label: "Open", val: summary.flagged, color: "text-warning" },
          { label: "Resolved", val: summary.resolved, color: "text-green-500" },
          { label: "Dismissed", val: summary.dismissed, color: "text-text-muted" },
        ].map((c, i) => (
          <div key={i} className="bg-bg-surface border border-border rounded-xl p-4">
            <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-1">{c.label}</p>
            <p className={`text-2xl font-bold font-mono ${c.color}`}>{c.val}</p>
          </div>
        ))}
      </div>

      {/* Anomaly Table */}
      <div className="bg-bg-surface border border-border rounded-xl overflow-x-auto">
        {loading ? (
          <div className="p-12 text-center text-text-muted animate-pulse">Loading anomalies...</div>
        ) : anomalies.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="bg-bg-subtle text-text-secondary">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Type</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Bill</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Vendor</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Description</th>
                <th className="px-4 py-3 text-center font-semibold text-xs uppercase">Status</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Detected</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {anomalies.map((a: any) => (
                <tr key={a.id} className="hover:bg-bg-overlay transition-colors">
                  <td className="px-4 py-3">
                    <span className="bg-warning/10 text-warning font-medium px-2 py-0.5 rounded text-xs">
                      {a.anomaly_type || 'unknown'}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-accent">{a.bill_number || '—'}</td>
                  <td className="px-4 py-3 text-text-base">{a.vendor_name || '—'}</td>
                  <td className="px-4 py-3 text-text-secondary text-xs max-w-xs truncate">{a.description || '—'}</td>
                  <td className="px-4 py-3 text-center">
                    <Badge
                      status={a.status === 'resolved' ? 'paid' : a.status === 'dismissed' ? 'draft' : 'overdue'}
                      label={(a.status || 'flagged').toUpperCase()}
                    />
                  </td>
                  <td className="px-4 py-3 text-text-muted text-xs">{a.created_at || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-12 text-center text-text-muted">No anomalies detected. Your data looks clean!</div>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";

const API = "http://localhost:8000/api/audit";

const ACTION_COLORS: Record<string, string> = {
  CREATE: "paid",
  EDIT: "sent",
  DELETE: "overdue",
  DOWNLOAD: "draft",
  PROCESS: "sent",
  EXPORT: "draft",
  SETTING_CHANGE: "overdue",
  NOTE_ADDED: "paid",
};

export function AuditPage() {
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  // Filters
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [actionTypes, setActionTypes] = useState<string[]>([]);
  const [selectedActions, setSelectedActions] = useState<string[]>([]);
  const [recordTypes, setRecordTypes] = useState<string[]>([]);
  const [selectedRecord, setSelectedRecord] = useState("");

  // Export modal
  const [showExport, setShowExport] = useState(false);
  const [exportFrom, setExportFrom] = useState("");
  const [exportTo, setExportTo] = useState("");

  const fetchEntries = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (fromDate) params.append("from", fromDate);
      if (toDate) params.append("to", toDate);
      if (selectedActions.length) params.append("action_type", selectedActions.join(","));
      if (selectedRecord) params.append("record_type", selectedRecord);
      params.append("page", String(page));
      const res = await apiFetch(`?${params}`);
      if (res.ok) {
        const data = await res.json();
        setEntries(data.entries || []);
        setTotalPages(data.pages || 1);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [fromDate, toDate, selectedActions, selectedRecord, page]);

  useEffect(() => { fetchEntries(); }, [fetchEntries]);

  useEffect(() => {
    (async () => {
      try {
        const [aRes, rRes] = await Promise.all([
          apiFetch(`/action-types`),
          apiFetch(`/record-types`),
        ]);
        if (aRes.ok) setActionTypes((await aRes.json()).types || []);
        if (rRes.ok) setRecordTypes((await rRes.json()).types || []);
      } catch (e) { console.error(e); }
    })();
  }, []);

  const toggleAction = (t: string) => {
    setSelectedActions(prev => prev.includes(t) ? prev.filter(a => a !== t) : [...prev, t]);
    setPage(1);
  };

  const handleExport = () => {
    const params = new URLSearchParams();
    if (exportFrom) params.append("from", exportFrom);
    if (exportTo) params.append("to", exportTo);
    window.open(`${API}/export?${params}`, "_blank");
    setShowExport(false);
  };

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold font-display text-text-base">Audit Trail</h1>
          <p className="text-sm text-text-muted mt-0.5">Complete compliance log of all system activity.</p>
        </div>
        <Button variant="secondary" onClick={() => { setExportFrom(fromDate); setExportTo(toDate); setShowExport(true); }}>
          Export to CSV
        </Button>
      </div>

      {/* Info Banner */}
      <div className="bg-accent/5 border border-accent/20 rounded-xl px-4 py-3 mb-5 flex items-center gap-3">
        <svg className="w-5 h-5 text-accent shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
          <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        <p className="text-sm text-text-secondary">This log is <strong>read-only</strong> and cannot be modified. Every action is recorded automatically.</p>
      </div>

      {/* Filter Bar */}
      <div className="bg-bg-surface border border-border rounded-xl p-4 mb-5 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <label className="text-xs font-semibold text-text-muted uppercase">From</label>
          <input
            type="date"
            value={fromDate}
            onChange={e => { setFromDate(e.target.value); setPage(1); }}
            title="From date"
            className="h-8 px-2 bg-bg-base border border-border rounded-lg text-xs text-text-base focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs font-semibold text-text-muted uppercase">To</label>
          <input
            type="date"
            value={toDate}
            onChange={e => { setToDate(e.target.value); setPage(1); }}
            title="To date"
            className="h-8 px-2 bg-bg-base border border-border rounded-lg text-xs text-text-base focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </div>

        {/* Action type chips */}
        <div className="flex flex-wrap gap-1.5 ml-2">
          {actionTypes.map(t => (
            <button
              key={t}
              onClick={() => toggleAction(t)}
              className={`px-2.5 py-1 text-[11px] font-semibold rounded-full border transition-colors ${
                selectedActions.includes(t)
                  ? "bg-accent text-white border-accent"
                  : "bg-bg-base text-text-muted border-border hover:border-accent/50"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Record type */}
        {recordTypes.length > 0 && (
          <select
            title="Record Type"
            className="h-8 px-2 bg-bg-base border border-border rounded-lg text-xs text-text-base focus:outline-none focus:ring-1 focus:ring-accent ml-auto"
            value={selectedRecord}
            onChange={e => { setSelectedRecord(e.target.value); setPage(1); }}
          >
            <option value="">All Records</option>
            {recordTypes.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        )}
      </div>

      {/* Table */}
      <div className="bg-bg-surface border border-border rounded-xl overflow-hidden flex-1">
        {loading ? (
          <div className="p-12 text-center text-text-muted animate-pulse">Loading audit log...</div>
        ) : entries.length === 0 ? (
          <div className="p-12 text-center text-text-muted">No audit entries found for the selected filters.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-bg-subtle text-text-secondary sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase w-[170px]">Timestamp</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase w-[90px]">Source</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase w-[130px]">Action</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase w-[120px]">Record</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Details</th>
                <th className="px-4 py-3 text-center font-semibold text-xs uppercase w-[60px]"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {entries.map(e => (
                <>
                  <tr key={e.id} className="hover:bg-bg-overlay transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-text-muted whitespace-nowrap">{e.created_at || "—"}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                        e.source === "agent" ? "bg-accent/10 text-accent" : "bg-text-muted/10 text-text-secondary"
                      }`}>
                        {(e.source || "system").toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        status={(ACTION_COLORS[e.action_type] || "draft") as any}
                        label={e.action_type || "—"}
                      />
                    </td>
                    <td className="px-4 py-3">
                      {e.record_type && (
                        <span className="bg-bg-subtle text-text-base text-xs font-medium px-2 py-0.5 rounded border border-border">
                          {e.record_type} {e.record_id ? `#${e.record_id}` : ""}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-text-secondary text-xs max-w-sm truncate">{e.details || e.description || "—"}</td>
                    <td className="px-4 py-3 text-center">
                      {(e.details || e.before_value || e.after_value) && (
                        <button
                          onClick={() => setExpandedId(expandedId === e.id ? null : e.id)}
                          className="text-accent hover:underline text-xs font-medium"
                          title={expandedId === e.id ? "Collapse" : "Expand"}
                        >
                          {expandedId === e.id ? "▲" : "▼"}
                        </button>
                      )}
                    </td>
                  </tr>
                  {expandedId === e.id && (
                    <tr key={`${e.id}-detail`} className="bg-bg-subtle/50">
                      <td colSpan={6} className="px-6 py-4">
                        <div className="space-y-2 text-xs">
                          {e.details && (
                            <div>
                              <span className="font-semibold text-text-secondary">Details:</span>
                              <p className="text-text-base mt-0.5 whitespace-pre-wrap">{e.details}</p>
                            </div>
                          )}
                          {e.before_value && (
                            <div>
                              <span className="font-semibold text-text-secondary">Before:</span>
                              <pre className="mt-0.5 bg-bg-base border border-border rounded p-2 font-mono text-text-muted overflow-x-auto">{e.before_value}</pre>
                            </div>
                          )}
                          {e.after_value && (
                            <div>
                              <span className="font-semibold text-text-secondary">After:</span>
                              <pre className="mt-0.5 bg-bg-base border border-border rounded p-2 font-mono text-text-base overflow-x-auto">{e.after_value}</pre>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-4">
          <Button variant="ghost" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}>
            ← Prev
          </Button>
          <span className="text-sm text-text-muted font-mono">
            Page {page} of {totalPages}
          </span>
          <Button variant="ghost" size="sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
            Next →
          </Button>
        </div>
      )}

      {/* Export Modal */}
      {showExport && (
        <div className="fixed inset-0 z-[300] flex items-center justify-center bg-black/50">
          <div className="bg-bg-surface border border-border rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-fade-in">
            <h3 className="text-lg font-bold text-text-base mb-4">Export Audit Log</h3>
            <p className="text-sm text-text-secondary mb-4">Select the date range for the CSV export.</p>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-text-muted uppercase block mb-1">From</label>
                <input
                  type="date"
                  value={exportFrom}
                  onChange={e => setExportFrom(e.target.value)}
                  title="Export from date"
                  className="w-full h-9 px-3 bg-bg-base border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-1 focus:ring-accent"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-text-muted uppercase block mb-1">To</label>
                <input
                  type="date"
                  value={exportTo}
                  onChange={e => setExportTo(e.target.value)}
                  title="Export to date"
                  className="w-full h-9 px-3 bg-bg-base border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-1 focus:ring-accent"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-5">
              <Button variant="ghost" size="sm" onClick={() => setShowExport(false)}>Cancel</Button>
              <Button variant="primary" size="sm" onClick={handleExport}>Download CSV</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

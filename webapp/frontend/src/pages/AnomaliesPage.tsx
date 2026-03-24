import { useState, useEffect, useCallback } from "react";
import { apiFetch } from '../api/client';
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";

const API = "http://localhost:8000/api/anomalies";

const STATUS_OPTIONS = [
  { key: "all", label: "All" },
  { key: "unreviewed", label: "Unreviewed" },
  { key: "acknowledged", label: "Acknowledged" },
  { key: "escalated", label: "Escalated" },
  { key: "dismissed", label: "Dismissed" },
];

const DISMISS_REASONS = [
  "Same vendor, different branch",
  "One-time price change",
  "Already verified externally",
  "Other",
];

export function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("");
  const [types, setTypes] = useState<string[]>([]);
  const [unreviewedCount, setUnreviewedCount] = useState(0);

  // Modal state
  const [escalateId, setEscalateId] = useState<number | null>(null);
  const [escalateComment, setEscalateComment] = useState("");
  const [dismissId, setDismissId] = useState<number | null>(null);
  const [dismissReason, setDismissReason] = useState(DISMISS_REASONS[0]);

  const fetchAnomalies = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (typeFilter) params.append("type", typeFilter);
      const res = await apiFetch(`?${params}`);
      if (res.ok) setAnomalies(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [statusFilter, typeFilter]);

  const fetchUnreviewed = useCallback(async () => {
    try {
      const res = await apiFetch(`/count/unreviewed`);
      if (res.ok) {
        const data = await res.json();
        setUnreviewedCount(data.count);
      }
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchAnomalies(); }, [fetchAnomalies]);
  useEffect(() => {
    fetchUnreviewed();
    const t = setInterval(fetchUnreviewed, 60000);
    return () => clearInterval(t);
  }, [fetchUnreviewed]);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch(`/types`);
        if (res.ok) setTypes((await res.json()).types || []);
      } catch (e) { console.error(e); }
    })();
  }, []);

  const acknowledge = async (id: number) => {
    // Optimistic update
    setAnomalies(prev => prev.map(a => a.id === id ? { ...a, status: "acknowledged" } : a));
    setUnreviewedCount(c => Math.max(0, c - 1));
    try { await apiFetch(`/${id}/acknowledge`, { method: "PATCH" }); }
    catch (e) { console.error(e); fetchAnomalies(); }
  };

  const escalate = async () => {
    if (escalateId == null) return;
    setAnomalies(prev => prev.map(a => a.id === escalateId ? { ...a, status: "escalated" } : a));
    setUnreviewedCount(c => Math.max(0, c - 1));
    try {
      await apiFetch(`/${escalateId}/escalate`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comment: escalateComment }),
      });
    } catch (e) { console.error(e); fetchAnomalies(); }
    setEscalateId(null);
    setEscalateComment("");
  };

  const dismiss = async () => {
    if (dismissId == null) return;
    setAnomalies(prev => prev.map(a => a.id === dismissId ? { ...a, status: "dismissed" } : a));
    setUnreviewedCount(c => Math.max(0, c - 1));
    try {
      await apiFetch(`/${dismissId}/dismiss`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: dismissReason }),
      });
    } catch (e) { console.error(e); fetchAnomalies(); }
    setDismissId(null);
    setDismissReason(DISMISS_REASONS[0]);
  };

  const fmt = (n: number) => `₹${n?.toLocaleString("en-IN", { maximumFractionDigits: 0 }) || "0"}`;

  const cardBorder = (status: string) => {
    if (status === "acknowledged") return "border-l-green-500";
    if (status === "escalated") return "border-l-accent";
    if (status === "dismissed") return "border-l-text-muted";
    return "border-l-warning";
  };

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-xl font-bold font-display text-text-base">Anomalies</h1>
        {unreviewedCount > 0 && (
          <span className="inline-flex items-center justify-center min-w-[28px] h-7 px-2 bg-danger text-white text-sm font-bold rounded-full animate-pulse">
            {unreviewedCount}
          </span>
        )}
      </div>

      {/* Filter Bar */}
      <div className="bg-bg-surface border border-border rounded-xl p-4 mb-6 flex items-center gap-4 flex-wrap">
        {/* Status filter */}
        <div className="flex rounded-lg overflow-hidden border border-border">
          {STATUS_OPTIONS.map(s => (
            <button
              key={s.key}
              onClick={() => setStatusFilter(s.key)}
              className={`px-3 py-2 text-xs font-semibold transition-colors ${
                statusFilter === s.key
                  ? "bg-accent text-white"
                  : "bg-bg-base text-text-secondary hover:bg-bg-subtle"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* Type filter */}
        {types.length > 0 && (
          <select
            title="Anomaly Type"
            className="h-9 px-3 bg-bg-base border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-1 focus:ring-accent"
            value={typeFilter}
            onChange={e => setTypeFilter(e.target.value)}
          >
            <option value="">All Types</option>
            {types.map(t => (
              <option key={t} value={t}>{t.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}</option>
            ))}
          </select>
        )}
      </div>

      {/* Anomaly Cards */}
      {loading ? (
        <div className="text-center p-12 text-text-muted animate-pulse">Loading anomalies...</div>
      ) : anomalies.length === 0 ? (
        <div className="bg-bg-surface border border-border rounded-xl p-12 text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-green-500/30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="font-semibold text-text-base">No anomalies found</p>
          <p className="text-sm text-text-muted mt-1">Your data looks clean for the selected filters.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {anomalies.map(a => (
            <div
              key={a.id}
              className={`bg-bg-surface border border-border rounded-xl p-5 border-l-[3px] transition-opacity ${cardBorder(a.status)} ${
                a.status === "dismissed" ? "opacity-60" : ""
              }`}
            >
              {/* Top row */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="bg-warning/10 text-warning text-xs font-bold px-2 py-0.5 rounded uppercase tracking-wide">
                    ⚠ {(a.anomaly_type || "unknown").replace(/_/g, " ")}
                  </span>
                  <Badge
                    status={a.status === "acknowledged" ? "paid" : a.status === "escalated" ? "sent" : a.status === "dismissed" ? "draft" : "overdue"}
                    label={a.status || "flagged"}
                  />
                </div>
                {a.confidence && (
                  <span className="text-xs font-mono text-text-muted">Confidence: {Math.round(a.confidence * 100)}%</span>
                )}
              </div>

              {/* Description */}
              <p className="text-sm text-text-base font-medium mb-1">
                {a.description || `Anomaly detected on bill ${a.bill_number || a.bill_id}`}
              </p>
              {a.vendor_name && (
                <p className="text-sm text-text-secondary mb-3">
                  {a.bill_number && <span className="font-mono text-accent">{a.bill_number}</span>}
                  {a.vendor_name && <span> from <strong>{a.vendor_name}</strong></span>}
                  {a.bill_total && <span> ({fmt(a.bill_total)})</span>}
                </p>
              )}

              {/* Flagged date */}
              <p className="text-xs text-text-muted mb-4">
                Flagged: {a.created_at || "—"}
              </p>

              {/* Actions */}
              {a.status !== "acknowledged" && a.status !== "dismissed" && (
                <div className="flex items-center gap-2">
                  <Button variant="secondary" size="sm" onClick={() => acknowledge(a.id)}>
                    ✓ Acknowledge
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => { setEscalateId(a.id); setEscalateComment(""); }}>
                    ↑ Escalate
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => { setDismissId(a.id); setDismissReason(DISMISS_REASONS[0]); }}>
                    Dismiss ↓
                  </Button>
                </div>
              )}
              {a.status === "acknowledged" && (
                <p className="text-xs text-green-500 font-medium">✓ Acknowledged</p>
              )}
              {a.status === "dismissed" && a.resolution_reason && (
                <p className="text-xs text-text-muted">Dismissed: {a.resolution_reason}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Escalate Modal */}
      {escalateId !== null && (
        <div className="fixed inset-0 z-[300] flex items-center justify-center bg-black/50">
          <div className="bg-bg-surface border border-border rounded-2xl shadow-2xl w-full max-w-md p-6 animate-fade-in">
            <h3 className="text-lg font-bold text-text-base mb-4">Escalate Anomaly</h3>
            <textarea
              className="w-full bg-bg-base border border-border rounded-lg p-3 text-sm text-text-base resize-none focus:outline-none focus:ring-1 focus:ring-accent"
              rows={3}
              placeholder="Add escalation comment..."
              value={escalateComment}
              onChange={e => setEscalateComment(e.target.value)}
            />
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="ghost" size="sm" onClick={() => setEscalateId(null)}>Cancel</Button>
              <Button variant="primary" size="sm" onClick={escalate}>Escalate</Button>
            </div>
          </div>
        </div>
      )}

      {/* Dismiss Popover Modal */}
      {dismissId !== null && (
        <div className="fixed inset-0 z-[300] flex items-center justify-center bg-black/50">
          <div className="bg-bg-surface border border-border rounded-2xl shadow-2xl w-full max-w-md p-6 animate-fade-in">
            <h3 className="text-lg font-bold text-text-base mb-4">Dismiss Anomaly</h3>
            <p className="text-sm text-text-secondary mb-3">Select a reason:</p>
            <div className="space-y-2">
              {DISMISS_REASONS.map(r => (
                <label key={r} className="flex items-center gap-3 bg-bg-base border border-border rounded-lg px-4 py-3 cursor-pointer hover:border-accent/40 transition-colors">
                  <input
                    type="radio"
                    name="dismiss-reason"
                    checked={dismissReason === r}
                    onChange={() => setDismissReason(r)}
                    className="accent-accent"
                  />
                  <span className="text-sm text-text-base">{r}</span>
                </label>
              ))}
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="ghost" size="sm" onClick={() => setDismissId(null)}>Cancel</Button>
              <Button variant="primary" size="sm" onClick={dismiss}>Confirm Dismiss</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

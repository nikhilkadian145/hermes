import { useState, useEffect, useCallback } from "react";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";

const API = "http://localhost:8000/api/system";

const STATUS_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  running: { bg: "bg-green-500", text: "text-white", label: "RUNNING" },
  degraded: { bg: "bg-amber-500", text: "text-white", label: "DEGRADED" },
  stopped: { bg: "bg-danger", text: "text-white", label: "STOPPED" },
};

const SEV_COLORS: Record<string, string> = {
  ERROR: "text-danger",
  WARNING: "text-warning",
  INFO: "text-text-muted",
};

export function SystemHealthPage() {
  const [status, setStatus] = useState<any>(null);
  const [queue, setQueue] = useState<any>({ items: [], paused: false });
  const [perfData, setPerfData] = useState<any[]>([]);
  const [errors, setErrors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sevFilter, setSevFilter] = useState("");

  const fetchAll = useCallback(async () => {
    try {
      const [sRes, qRes, pRes, eRes] = await Promise.all([
        apiFetch(`/status`),
        apiFetch(`/queue`),
        apiFetch(`/performance?hours=24`),
        apiFetch(`/errors?limit=100${sevFilter ? `&severity=${sevFilter}` : ""}`),
      ]);
      if (sRes.ok) setStatus(await sRes.json());
      if (qRes.ok) setQueue(await qRes.json());
      if (pRes.ok) { const d = await pRes.json(); setPerfData(d.data || []); }
      if (eRes.ok) { const d = await eRes.json(); setErrors(d.entries || []); }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [sevFilter]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // Poll queue every 5 seconds
  useEffect(() => {
    const t = setInterval(async () => {
      try {
        const res = await apiFetch(`/queue`);
        if (res.ok) setQueue(await res.json());
      } catch { /* silent */ }
    }, 5000);
    return () => clearInterval(t);
  }, []);

  const handleRequeue = async (id: number) => {
    await apiFetch(`/queue/${id}/requeue`, { method: "POST" });
    fetchAll();
  };

  const handleRequeueAllFailed = async () => {
    await apiFetch(`/queue/requeue-all-failed`, { method: "POST" });
    fetchAll();
  };

  const handleTogglePause = async () => {
    const endpoint = queue.paused ? "resume" : "pause";
    await apiFetch(`/queue/${endpoint}`, { method: "POST" });
    fetchAll();
  };

  const formatUptime = (secs: number) => {
    const d = Math.floor(secs / 86400);
    const h = Math.floor((secs % 86400) / 3600);
    const m = Math.floor((secs % 3600) / 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
  };

  const copyErrors = () => {
    const text = errors.map(e => e.line).join("\n");
    navigator.clipboard.writeText(text);
  };

  const downloadLog = () => {
    const text = errors.map(e => e.line).join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "hermes_errors.log"; a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <div className="p-12 text-center text-text-muted animate-pulse">Loading system health...</div>;

  const sc = STATUS_CONFIG[status?.agent_status] || STATUS_CONFIG.stopped;
  const diskPct = status ? Math.round((status.disk_used_gb / status.disk_total_gb) * 100) : 0;

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      <div className="mb-6">
        <h1 className="text-xl font-bold font-display text-text-base">System Health</h1>
        <p className="text-sm text-text-muted mt-0.5">Monitor HERMES backend, processing queue, and performance.</p>
      </div>

      {/* ── Status Cards ── */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        {/* Agent Status — prominent */}
        <div className={`col-span-2 md:col-span-1 ${sc.bg} rounded-xl p-5 flex flex-col items-center justify-center min-h-[120px]`}>
          <div className={`w-3 h-3 rounded-full bg-white/30 mb-2 ${status?.agent_status === "running" ? "animate-pulse" : ""}`} />
          <p className={`text-2xl font-black ${sc.text} tracking-wide`}>{sc.label}</p>
          <p className={`text-xs ${sc.text} opacity-70 mt-1`}>v{status?.version || "1.0.0"}</p>
        </div>

        {/* Queue Depth */}
        <div className="bg-bg-surface border border-border rounded-xl p-4 flex flex-col">
          <p className="text-xs text-text-muted uppercase font-semibold mb-1">Queue</p>
          <p className="text-3xl font-bold text-text-base">{status?.queue_depth ?? 0}</p>
          <p className="text-xs text-text-muted mt-auto">{status?.queue_processing ?? 0} processing</p>
        </div>

        {/* Avg Processing Time */}
        <div className="bg-bg-surface border border-border rounded-xl p-4 flex flex-col">
          <p className="text-xs text-text-muted uppercase font-semibold mb-1">Avg Time</p>
          <p className="text-3xl font-bold text-text-base">{status?.avg_processing_time_secs ?? 0}<span className="text-sm font-normal text-text-muted">s</span></p>
          <p className="text-xs text-text-muted mt-auto">per document</p>
        </div>

        {/* Disk Usage */}
        <div className="bg-bg-surface border border-border rounded-xl p-4 flex flex-col">
          <p className="text-xs text-text-muted uppercase font-semibold mb-1">Disk</p>
          <p className="text-xl font-bold text-text-base">{status?.disk_used_gb ?? 0}<span className="text-sm font-normal text-text-muted"> / {status?.disk_total_gb ?? 0} GB</span></p>
          <div className="w-full h-2 bg-bg-subtle rounded-full mt-2 overflow-hidden">
            <div className={`h-full rounded-full transition-all ${diskPct > 85 ? "bg-danger" : diskPct > 65 ? "bg-warning" : "bg-green-500"}`} style={{ width: `${diskPct}%` }} />
          </div>
          <p className="text-xs text-text-muted mt-1">{diskPct}% used</p>
        </div>

        {/* Uptime */}
        <div className="bg-bg-surface border border-border rounded-xl p-4 flex flex-col">
          <p className="text-xs text-text-muted uppercase font-semibold mb-1">Uptime</p>
          <p className="text-2xl font-bold text-text-base">{formatUptime(status?.uptime_seconds ?? 0)}</p>
          <p className="text-xs text-text-muted mt-auto">{status?.last_backup ? `Backup: ${new Date(status.last_backup).toLocaleDateString()}` : "No backup logged"}</p>
        </div>
      </div>

      {/* ── Processing Queue ── */}
      <div className="bg-bg-surface border border-border rounded-xl mb-8 overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h2 className="font-semibold text-text-base">Processing Queue</h2>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={handleRequeueAllFailed}>Reprocess All Failed</Button>
            <Button variant={queue.paused ? "primary" : "secondary"} size="sm" onClick={handleTogglePause}>
              {queue.paused ? "▶ Resume Queue" : "⏸ Pause Queue"}
            </Button>
          </div>
        </div>
        {queue.paused && (
          <div className="px-5 py-2 bg-warning/10 border-b border-warning/20 text-xs font-semibold text-warning">
            ⚠ Queue is paused — new uploads will not be processed until resumed.
          </div>
        )}
        <div className="max-h-64 overflow-y-auto">
          {(queue.items || []).length === 0 ? (
            <div className="px-5 py-8 text-center text-text-muted text-sm">Queue is empty.</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-bg-subtle sticky top-0">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-text-muted">Filename</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-text-muted">Uploaded</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-text-muted">Status</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold text-text-muted">Error</th>
                  <th className="px-4 py-2 text-right text-xs font-semibold text-text-muted">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {queue.items.map((item: any) => (
                  <tr key={item.id} className="hover:bg-bg-overlay transition-colors">
                    <td className="px-4 py-2 text-text-base font-medium truncate max-w-[200px]">{item.filename || `File #${item.id}`}</td>
                    <td className="px-4 py-2 text-text-muted text-xs font-mono">{item.created_at || "—"}</td>
                    <td className="px-4 py-2">
                      <Badge
                        status={item.status === "completed" ? "paid" : item.status === "processing" ? "sent" : item.status === "error" ? "overdue" : "draft"}
                        label={item.status || "queued"}
                      />
                    </td>
                    <td className="px-4 py-2 text-xs text-danger truncate max-w-[200px]">{item.error_message || ""}</td>
                    <td className="px-4 py-2 text-right">
                      {(item.status === "error" || item.status === "completed") && (
                        <button onClick={() => handleRequeue(item.id)} className="text-xs text-accent hover:underline font-medium">Requeue</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* ── Performance Graph ── */}
      <div className="bg-bg-surface border border-border rounded-xl p-5 mb-8">
        <h2 className="font-semibold text-text-base mb-4">24-Hour Performance</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={perfData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="hour" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
              <YAxis yAxisId="left" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} label={{ value: "ms", angle: -90, position: "insideLeft", style: { fontSize: 10, fill: "var(--color-text-muted)" } }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} label={{ value: "docs/hr", angle: 90, position: "insideRight", style: { fontSize: 10, fill: "var(--color-text-muted)" } }} />
              <Tooltip contentStyle={{ backgroundColor: "var(--color-bg-surface)", border: "1px solid var(--color-border)", borderRadius: 8, fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line yAxisId="left" type="monotone" dataKey="api_response_ms" stroke="var(--color-accent)" strokeWidth={2} dot={false} name="API Response (ms)" />
              <Bar yAxisId="right" dataKey="docs_per_hour" fill="var(--color-accent)" opacity={0.2} name="Docs/Hour" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Error Log ── */}
      <div className="bg-bg-surface border border-border rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h2 className="font-semibold text-text-base">Error Log</h2>
          <div className="flex items-center gap-2">
            {["", "ERROR", "WARNING", "INFO"].map(s => (
              <button
                key={s}
                onClick={() => { setSevFilter(s); }}
                className={`px-2.5 py-1 text-[11px] font-semibold rounded-full border transition-colors ${
                  sevFilter === s
                    ? "bg-accent text-white border-accent"
                    : "bg-bg-base text-text-muted border-border hover:border-accent/50"
                }`}
              >
                {s || "All"}
              </button>
            ))}
            <button onClick={copyErrors} className="text-xs text-accent hover:underline font-medium ml-2" title="Copy All">Copy All</button>
            <button onClick={downloadLog} className="text-xs text-accent hover:underline font-medium" title="Download Log">Download .log</button>
          </div>
        </div>
        <div className="max-h-80 overflow-y-auto p-4">
          {errors.length === 0 ? (
            <p className="text-sm text-text-muted text-center py-6">No log entries found.</p>
          ) : (
            <pre className="font-mono text-xs leading-relaxed space-y-0.5">
              {errors.map((entry, i) => (
                <div key={i} className={`${SEV_COLORS[entry.severity] || "text-text-muted"}`}>
                  {entry.line}
                </div>
              ))}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

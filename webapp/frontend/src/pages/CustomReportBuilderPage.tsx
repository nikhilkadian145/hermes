import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

const DIMENSIONS = [
  { key: "vendor", label: "Vendor" },
  { key: "customer", label: "Customer" },
  { key: "category", label: "Category" },
  { key: "month", label: "Month" },
  { key: "quarter", label: "Quarter" },
];

const METRICS = [
  { key: "total_amount", label: "Total Amount" },
  { key: "count", label: "Count" },
  { key: "average", label: "Average" },
  { key: "min", label: "Min" },
  { key: "max", label: "Max" },
];

export function CustomReportBuilderPage() {
  const navigate = useNavigate();
  const [dimensions, setDimensions] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<string[]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [rows, setRows] = useState<any[][]>([]);
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<any[]>([]);
  const [templateName, setTemplateName] = useState("");
  const [showSave, setShowSave] = useState(false);
  const [saving, setSaving] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchPreview = useCallback(async (dims: string[], mets: string[]) => {
    if (dims.length === 0 && mets.length === 0) {
      setHeaders([]);
      setRows([]);
      return;
    }
    setLoading(true);
    try {
      const res = await apiFetch("/reports/custom/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dimensions: dims, metrics: mets, filters: {} }),
      });
      if (res.ok) {
        const data = await res.json();
        setHeaders(data.headers || []);
        setRows(data.rows || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounced preview
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchPreview(dimensions, metrics), 500);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [dimensions, metrics, fetchPreview]);

  // Fetch saved templates
  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch("/reports/custom/templates");
        if (res.ok) {
          const data = await res.json();
          setTemplates(data.templates || []);
        }
      } catch (e) { console.error(e); }
    })();
  }, []);

  const addDimension = (key: string) => {
    if (!dimensions.includes(key)) setDimensions([...dimensions, key]);
  };

  const addMetric = (key: string) => {
    if (!metrics.includes(key)) setMetrics([...metrics, key]);
  };

  const removeDimension = (key: string) => setDimensions(dimensions.filter(d => d !== key));
  const removeMetric = (key: string) => setMetrics(metrics.filter(m => m !== key));

  const saveTemplate = async () => {
    if (!templateName.trim()) return;
    setSaving(true);
    try {
      await apiFetch("/reports/custom/templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: templateName, config: { dimensions, metrics } }),
      });
      setShowSave(false);
      setTemplateName("");
      const res = await apiFetch("/reports/custom/templates");
      if (res.ok) setTemplates((await res.json()).templates || []);
    } catch (err) { console.error(err); }
    finally { setSaving(false); }
  };

  const loadTemplate = (t: any) => {
    try {
      const cfg = typeof t.config === "string" ? JSON.parse(t.config) : t.config;
      setDimensions(cfg.dimensions || []);
      setMetrics(cfg.metrics || []);
    } catch (e) { console.error(e); }
  };

  const deleteTemplate = async (id: number) => {
    await apiFetch(`/reports/custom/templates/${id}`, { method: "DELETE" });
    setTemplates(templates.filter(t => t.id !== id));
  };

  const handleGenerate = async () => {
    try {
      const res = await apiFetch("/reports/custom/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dimensions, metrics, filters: {} }),
      });
      const data = await res.json();
      alert(`Report generated: ${data.message}\nURL: ${data.url}`);
    } catch (err) { console.error(err); }
  };

  const fmt = (v: any) => typeof v === "number" ? v.toLocaleString("en-IN") : (v ?? "—");

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate("/reports")} className="p-2 -ml-2 text-text-muted hover:bg-bg-overlay hover:text-text-base rounded transition-colors" title="Back to Reports">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
        </button>
        <div>
          <h1 className="text-xl font-bold font-display text-text-base">Custom Report Builder</h1>
          <p className="text-sm text-text-muted">Drag dimensions and metrics to build ad-hoc reports.</p>
        </div>
      </div>

      {/* Two-Panel Layout */}
      <div className="flex gap-6 flex-1 overflow-hidden">
        {/* Left Panel — Builder Controls */}
        <div className="w-[300px] shrink-0 flex flex-col gap-5 overflow-y-auto">
          {/* Dimensions */}
          <div className="bg-bg-surface border border-border rounded-xl p-4">
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">Dimensions (Group By)</h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {DIMENSIONS.map(d => (
                <button
                  key={d.key}
                  onClick={() => addDimension(d.key)}
                  disabled={dimensions.includes(d.key)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
                    dimensions.includes(d.key)
                      ? "bg-accent/10 text-accent border-accent/30 cursor-default"
                      : "bg-bg-base text-text-secondary border-border hover:border-accent hover:text-accent"
                  }`}
                >
                  + {d.label}
                </button>
              ))}
            </div>
            {dimensions.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {dimensions.map(key => (
                  <span key={key} className="inline-flex items-center gap-1 bg-accent/10 text-accent text-xs font-semibold px-2.5 py-1 rounded-full">
                    {DIMENSIONS.find(d => d.key === key)?.label}
                    <button onClick={() => removeDimension(key)} className="hover:text-danger ml-0.5" title="Remove">×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Metrics */}
          <div className="bg-bg-surface border border-border rounded-xl p-4">
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">Metrics (Aggregate)</h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {METRICS.map(m => (
                <button
                  key={m.key}
                  onClick={() => addMetric(m.key)}
                  disabled={metrics.includes(m.key)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
                    metrics.includes(m.key)
                      ? "bg-green-500/10 text-green-500 border-green-500/30 cursor-default"
                      : "bg-bg-base text-text-secondary border-border hover:border-green-500 hover:text-green-500"
                  }`}
                >
                  + {m.label}
                </button>
              ))}
            </div>
            {metrics.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {metrics.map(key => (
                  <span key={key} className="inline-flex items-center gap-1 bg-green-500/10 text-green-500 text-xs font-semibold px-2.5 py-1 rounded-full">
                    {METRICS.find(m => m.key === key)?.label}
                    <button onClick={() => removeMetric(key)} className="hover:text-danger ml-0.5" title="Remove">×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Save Template */}
          <div className="bg-bg-surface border border-border rounded-xl p-4">
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">Templates</h3>
            {showSave ? (
              <div className="flex gap-2 mb-3">
                <Input value={templateName} onChange={e => setTemplateName(e.target.value)} placeholder="Template name..." />
                <Button variant="primary" size="sm" onClick={saveTemplate} disabled={saving}>Save</Button>
                <Button variant="ghost" size="sm" onClick={() => setShowSave(false)}>×</Button>
              </div>
            ) : (
              <Button variant="secondary" size="sm" onClick={() => setShowSave(true)} className="w-full mb-3">
                Save Current as Template
              </Button>
            )}
            <div className="space-y-1.5 max-h-40 overflow-y-auto">
              {templates.map(t => (
                <div key={t.id} className="flex items-center justify-between bg-bg-subtle rounded-lg px-3 py-2 text-sm group">
                  <button onClick={() => loadTemplate(t)} className="text-text-base hover:text-accent font-medium truncate flex-1 text-left">
                    {t.name}
                  </button>
                  <button onClick={() => deleteTemplate(t.id)} className="text-text-muted hover:text-danger opacity-0 group-hover:opacity-100 transition-opacity ml-2" title="Delete">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </div>
              ))}
              {templates.length === 0 && <p className="text-xs text-text-muted">No saved templates yet.</p>}
            </div>
          </div>
        </div>

        {/* Right Panel — Preview Table */}
        <div className="flex-1 bg-bg-surface border border-border rounded-xl overflow-hidden flex flex-col">
          <div className="bg-bg-subtle px-5 py-3 border-b border-border flex items-center justify-between shrink-0">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
              Live Preview {rows.length > 0 && `(${rows.length} rows)`}
            </span>
            {loading && <span className="text-xs text-accent animate-pulse">Querying...</span>}
          </div>

          <div className="flex-1 overflow-auto">
            {headers.length === 0 ? (
              <div className="h-full flex items-center justify-center text-text-muted p-12">
                <div className="text-center">
                  <svg className="w-16 h-16 mx-auto mb-4 text-text-muted/30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1">
                    <path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="font-medium">Add dimensions and metrics to preview your report</p>
                  <p className="text-sm mt-1 text-text-muted">Select at least one option from the left panel.</p>
                </div>
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-bg-subtle sticky top-0">
                  <tr>
                    {headers.map((h, i) => (
                      <th key={i} className="px-4 py-3 text-left font-semibold text-xs uppercase tracking-wider text-text-secondary border-b border-border">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {rows.map((row, i) => (
                    <tr key={i} className="hover:bg-bg-overlay transition-colors">
                      {row.map((cell, j) => (
                        <td key={j} className={`px-4 py-3 ${typeof cell === 'number' ? 'font-mono text-right' : ''}`}>
                          {fmt(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Action Bar */}
      <div className="mt-4 bg-bg-surface border border-border rounded-xl p-4 flex items-center justify-between">
        <span className="text-sm text-text-secondary">
          {dimensions.length} dimensions, {metrics.length} metrics selected
        </span>
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={() => { setDimensions([]); setMetrics([]); }}>
            Clear All
          </Button>
          <Button variant="primary" onClick={handleGenerate} disabled={headers.length === 0}>
            Run Full Report
          </Button>
        </div>
      </div>
    </div>
  );
}

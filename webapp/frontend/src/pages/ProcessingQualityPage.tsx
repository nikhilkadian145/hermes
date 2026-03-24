import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function ProcessingQualityPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch("/reports/processing-quality");
        if (res.ok) setData(await res.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  const m = data?.metrics || { total_documents: 0, avg_confidence: 0, correction_rate: 0, error_rate: 0, error_count: 0 };

  const gaugeColor = (val: number) => {
    if (val >= 90) return "text-green-500";
    if (val >= 70) return "text-warning";
    return "text-danger";
  };

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate("/reports")} className="p-2 -ml-2 text-text-muted hover:bg-bg-overlay hover:text-text-base rounded transition-colors" title="Back to Reports">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
        </button>
        <h1 className="text-xl font-bold font-display text-text-base">Processing Quality</h1>
      </div>

      {loading ? (
        <div className="p-12 text-center text-text-muted animate-pulse">Loading metrics...</div>
      ) : (
        <>
          {/* KPI Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div className="bg-bg-surface border border-border rounded-xl p-6 text-center">
              <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Documents Processed</p>
              <p className="text-4xl font-bold font-mono text-text-base">{m.total_documents}</p>
            </div>

            <div className="bg-bg-surface border border-border rounded-xl p-6 text-center">
              <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Avg OCR Confidence</p>
              <p className={`text-4xl font-bold font-mono ${gaugeColor(m.avg_confidence)}`}>{m.avg_confidence}%</p>
              <div className="w-full bg-bg-subtle rounded-full h-2 mt-3">
                <div className={`h-2 rounded-full transition-all ${m.avg_confidence >= 90 ? 'bg-green-500' : m.avg_confidence >= 70 ? 'bg-warning' : 'bg-danger'}`} style={{width: `${m.avg_confidence}%`}} />
              </div>
            </div>

            <div className="bg-bg-surface border border-border rounded-xl p-6 text-center">
              <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Correction Rate</p>
              <p className="text-4xl font-bold font-mono text-warning">{m.correction_rate}%</p>
              <p className="text-xs text-text-muted mt-2">Fields manually edited</p>
            </div>

            <div className="bg-bg-surface border border-border rounded-xl p-6 text-center">
              <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">Error Rate</p>
              <p className={`text-4xl font-bold font-mono ${m.error_rate > 5 ? 'text-danger' : 'text-green-500'}`}>{m.error_rate}%</p>
              <p className="text-xs text-text-muted mt-2">{m.error_count} failed documents</p>
            </div>
          </div>

          {/* Insight Bar */}
          <div className="bg-accent/5 border border-accent/20 rounded-xl p-5 flex items-start gap-4">
            <svg className="w-6 h-6 text-accent mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <div>
              <p className="font-semibold text-text-base text-sm">Quality Insights</p>
              <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                {m.avg_confidence >= 90 
                  ? "Excellent OCR quality. Documents are being processed accurately with minimal manual intervention needed."
                  : m.avg_confidence >= 70
                  ? "Moderate quality. Some vendors may have poor scan quality. Consider reviewing vendor-specific documents."
                  : "OCR quality needs improvement. Many documents require manual corrections."}
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

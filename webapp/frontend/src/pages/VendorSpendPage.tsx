import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function VendorSpendPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch("/reports/vendor-spend-analysis?months=12");
        if (res.ok) setData(await res.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  const vendors = data?.vendors || {};
  const vendorNames = Object.keys(vendors);

  const fmt = (n: number) => `₹${n.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

  // Detect price drift for a vendor (>20% jump)
  const hasDrift = (points: any[]): boolean => {
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1].spend;
      const curr = points[i].spend;
      if (prev > 0 && Math.abs(curr - prev) / prev > 0.2) return true;
    }
    return false;
  };

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate("/reports")} className="p-2 -ml-2 text-text-muted hover:bg-bg-overlay hover:text-text-base rounded transition-colors" title="Back to Reports">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
        </button>
        <h1 className="text-xl font-bold font-display text-text-base">Vendor Spend Analysis</h1>
      </div>

      {loading ? (
        <div className="p-12 text-center text-text-muted animate-pulse">Loading vendor data...</div>
      ) : vendorNames.length === 0 ? (
        <div className="bg-bg-surface border border-border rounded-xl p-12 text-center text-text-muted">
          No vendor spend data available for the last 12 months.
        </div>
      ) : (
        <div className="space-y-6">
          {vendorNames.map(name => {
            const points = vendors[name] as any[];
            const totalSpend = points.reduce((s: number, p: any) => s + p.spend, 0);
            const drift = hasDrift(points);
            const maxSpend = Math.max(...points.map((p: any) => p.spend), 1);

            return (
              <div key={name} className={`bg-bg-surface border rounded-xl p-5 ${drift ? 'border-warning/50' : 'border-border'}`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-text-base">{name}</h3>
                    {drift && (
                      <span className="bg-warning/10 text-warning text-xs font-semibold px-2 py-0.5 rounded flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
                        Price Drift Detected
                      </span>
                    )}
                  </div>
                  <span className="font-mono font-bold text-text-base">{fmt(totalSpend)}</span>
                </div>

                {/* Bar Chart */}
                <div className="flex items-end gap-1 h-24">
                  {points.map((p: any, i: number) => {
                    const height = (p.spend / maxSpend) * 100;
                    // Detect jump for this specific bar
                    const isJump = i > 0 && points[i - 1].spend > 0 && Math.abs(p.spend - points[i - 1].spend) / points[i - 1].spend > 0.2;
                    return (
                      <div key={i} className="flex flex-col items-center flex-1 gap-1">
                        <div
                          className={`w-full rounded-t transition-all ${isJump ? 'bg-warning' : 'bg-accent/60'}`}
                          style={{ height: `${Math.max(height, 2)}%` }}
                          title={`${p.month}: ${fmt(p.spend)} (${p.bills} bills)`}
                        />
                        <span className="text-[9px] text-text-muted font-mono">{p.month.slice(5)}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

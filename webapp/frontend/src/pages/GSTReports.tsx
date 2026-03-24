import { useState, useEffect, useCallback } from 'react';
import { apiFetch } from '../api/client';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

const API = '/api/reports';

type TabKey = 'gstr1' | 'itc' | 'hsn';

const QUARTERS = [
  { key: 'Q1', label: 'Q1 (Apr–Jun)', from: '-04-01', to: '-06-30' },
  { key: 'Q2', label: 'Q2 (Jul–Sep)', from: '-07-01', to: '-09-30' },
  { key: 'Q3', label: 'Q3 (Oct–Dec)', from: '-10-01', to: '-12-31' },
  { key: 'Q4', label: 'Q4 (Jan–Mar)', from: '-01-01', to: '-03-31' },
];

function getCurrentFY() {
  const now = new Date();
  return now.getMonth() >= 3 ? now.getFullYear() : now.getFullYear() - 1;
}

function getCurrentQuarter(): string {
  const m = new Date().getMonth(); // 0-indexed
  if (m >= 3 && m <= 5) return 'Q1';
  if (m >= 6 && m <= 8) return 'Q2';
  if (m >= 9 && m <= 11) return 'Q3';
  return 'Q4';
}

function fmt(n: number) {
  return `₹${n.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
}

export default function GSTReportsPage() {
  const [tab, setTab] = useState<TabKey>('gstr1');
  const [quarterKey, setQuarterKey] = useState(getCurrentQuarter());
  const [year, setYear] = useState(getCurrentFY());
  const [gstData, setGstData] = useState<any>(null);
  const [itcData, setItcData] = useState<any>(null);
  const [hsnData, setHsnData] = useState<any>(null);
  const [liabilityData, setLiabilityData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);

  const getDateRange = useCallback(() => {
    const q = QUARTERS.find(q => q.key === quarterKey)!;
    const fy = quarterKey === 'Q4' ? year + 1 : year;
    return { from: `${fy}${q.from}`, to: `${fy}${q.to}` };
  }, [quarterKey, year]);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    const { from, to } = getDateRange();
    const qs = `from_date=${from}&to_date=${to}`;
    try {
      const [gstRes, itcRes, hsnRes, liabRes] = await Promise.all([
        apiFetch(`/gst?${qs}`),
        apiFetch(`/gst/itc?${qs}`),
        apiFetch(`/gst/hsn-summary?${qs}`),
        apiFetch(`/gst/liability?${qs}`),
      ]);
      if (gstRes.ok) setGstData(await gstRes.json());
      if (itcRes.ok) setItcData(await itcRes.json());
      if (hsnRes.ok) setHsnData(await hsnRes.json());
      if (liabRes.ok) setLiabilityData(await liabRes.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [getDateRange]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleExportJSON = async () => {
    setExporting(true);
    try {
      const res = await apiFetch(`/gst/export-json?quarter=${quarterKey}&year=${year}`, { method: 'POST' });
      const data = await res.json();
      alert(`Export ready: ${data.message}\nDownload: ${data.url}`);
    } catch (err) {
      console.error(err);
    } finally {
      setExporting(false);
    }
  };

  const outputTotal = liabilityData?.output_tax?.total || 0;
  const itcTotal = liabilityData?.input_tax_credit?.total || itcData?.total_itc || 0;
  const netPayable = liabilityData?.net_payable?.total || (outputTotal - itcTotal);

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'gstr1', label: 'GSTR-1' },
    { key: 'itc', label: 'Input Tax Credit' },
    { key: 'hsn', label: 'HSN/SAC Summary' },
  ];

  const years = Array.from({ length: 5 }, (_, i) => getCurrentFY() - i);

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold font-display text-text-base">GST Reports</h1>
          <p className="text-sm text-text-muted mt-1">Generate and export GST returns for filing.</p>
        </div>
        <Button variant="primary" onClick={handleExportJSON} disabled={exporting}>
          {exporting ? 'Exporting...' : 'Export for GST Portal (JSON)'}
        </Button>
      </div>

      {/* Quarter Selector */}
      <div className="bg-bg-surface border border-border rounded-xl p-4 mb-6 flex items-center gap-4 flex-wrap">
        <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Financial Year</label>
        <select
          title="Financial Year"
          className="h-9 px-3 bg-bg-base border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-1 focus:ring-accent"
          value={year}
          onChange={e => setYear(parseInt(e.target.value))}
        >
          {years.map(y => (
            <option key={y} value={y}>FY {y}–{String(y + 1).slice(2)}</option>
          ))}
        </select>

        <div className="flex rounded-lg overflow-hidden border border-border ml-4">
          {QUARTERS.map(q => (
            <button
              key={q.key}
              onClick={() => setQuarterKey(q.key)}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                quarterKey === q.key
                  ? 'bg-accent text-white'
                  : 'bg-bg-base text-text-secondary hover:bg-bg-subtle'
              }`}
            >
              {q.label}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
        <div className="bg-bg-surface border border-border rounded-xl p-5">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Output Tax Collected</p>
          <p className="text-2xl font-bold font-mono text-text-base">{fmt(outputTotal)}</p>
          <p className="text-xs text-text-muted mt-1">CGST + SGST / IGST on Sales</p>
        </div>
        <div className="bg-bg-surface border border-border rounded-xl p-5">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Input Tax Credit</p>
          <p className="text-2xl font-bold font-mono text-green-500">{fmt(itcTotal)}</p>
          <p className="text-xs text-text-muted mt-1">ITC claimed on purchases</p>
        </div>
        <div className={`bg-bg-surface border rounded-xl p-5 ${netPayable > 0 ? 'border-danger/50' : 'border-border'}`}>
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Net GST Payable</p>
          <p className={`text-2xl font-bold font-mono ${netPayable > 0 ? 'text-danger' : 'text-green-500'}`}>
            {netPayable > 0 ? fmt(netPayable) : fmt(Math.abs(netPayable))}
          </p>
          <p className="text-xs text-text-muted mt-1">
            {netPayable > 0 ? 'Amount to be paid to government' : 'Excess ITC — carry forward'}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-border mb-6">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-5 py-3 text-sm font-semibold border-b-2 transition-colors ${
              tab === t.key
                ? 'border-accent text-accent'
                : 'border-transparent text-text-muted hover:text-text-base'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1">
        {loading && <div className="text-center p-12 text-text-muted animate-pulse">Loading quarter data...</div>}
        {!loading && tab === 'gstr1' && <GSTR1Tab data={gstData} />}
        {!loading && tab === 'itc' && <ITCTab data={itcData} />}
        {!loading && tab === 'hsn' && <HSNTab data={hsnData} />}
      </div>

      {/* Export Helper */}
      <div className="bg-accent/5 border border-accent/20 rounded-xl p-5 mt-6 flex items-center gap-4">
        <svg className="w-8 h-8 text-accent shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
          <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <p className="text-sm font-semibold text-text-base">Ready to file?</p>
          <p className="text-xs text-text-secondary mt-0.5">
            Upload the exported JSON at <span className="font-mono text-accent">gstn.org → Returns → GSTR-1 → Upload JSON</span>
          </p>
        </div>
      </div>
    </div>
  );
}

/* ---------- GSTR-1 Tab ---------- */
function GSTR1Tab({ data }: { data: any }) {
  if (!data) return <p className="text-text-muted p-4">No data available for this quarter.</p>;

  return (
    <div className="space-y-6">
      {/* B2B Invoices */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <h3 className="font-semibold text-text-base">B2B Invoices</h3>
          <Badge status="draft" label={`${data.b2b?.length || 0} invoices`} />
        </div>
        {data.b2b?.length > 0 ? (
          <div className="overflow-x-auto bg-bg-surface border border-border rounded-xl">
            <table className="w-full text-sm">
              <thead className="bg-bg-subtle text-text-secondary">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Invoice #</th>
                  <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Date</th>
                  <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Client</th>
                  <th className="px-4 py-3 text-left font-semibold text-xs uppercase">GSTIN</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">Taxable</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">CGST</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">SGST</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">IGST</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.b2b.map((inv: any, i: number) => (
                  <tr key={i} className="hover:bg-bg-overlay transition-colors">
                    <td className="px-4 py-3 font-mono font-medium text-accent">{inv.invoice_number}</td>
                    <td className="px-4 py-3 text-text-secondary">{inv.date}</td>
                    <td className="px-4 py-3 text-text-base">{inv.client_name}</td>
                    <td className="px-4 py-3 font-mono text-xs text-text-muted">{inv.client_gstin || '—'}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(inv.taxable_value)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(inv.cgst)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(inv.sgst)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(inv.igst)}</td>
                    <td className="px-4 py-3 text-right font-mono font-semibold">{fmt(inv.total)}</td>
                  </tr>
                ))}
              </tbody>
              {data.totals && (
                <tfoot className="bg-bg-subtle font-bold text-text-base">
                  <tr>
                    <td colSpan={4} className="px-4 py-3">TOTAL</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(data.totals.total_taxable || 0)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(data.totals.total_cgst || 0)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(data.totals.total_sgst || 0)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(data.totals.total_igst || 0)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(data.totals.total_tax || 0)}</td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        ) : (
          <p className="text-text-muted text-sm p-4 bg-bg-surface border border-border rounded-xl">No B2B invoices for this quarter.</p>
        )}
      </div>

      {/* B2C Small Summary */}
      {data.b2c_small?.length > 0 && (
        <div>
          <h3 className="font-semibold text-text-base mb-3">B2C Small (Aggregated)</h3>
          <div className="overflow-x-auto bg-bg-surface border border-border rounded-xl">
            <table className="w-full text-sm">
              <thead className="bg-bg-subtle text-text-secondary">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Rate</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">Taxable</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">CGST</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">SGST</th>
                  <th className="px-4 py-3 text-right font-semibold text-xs uppercase">IGST</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.b2c_small.map((r: any, i: number) => (
                  <tr key={i} className="hover:bg-bg-overlay transition-colors">
                    <td className="px-4 py-3 font-medium">{r.rate}%</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(r.taxable)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(r.cgst)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(r.sgst)}</td>
                    <td className="px-4 py-3 text-right font-mono">{fmt(r.igst)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

/* ---------- ITC Tab ---------- */
function ITCTab({ data }: { data: any }) {
  if (!data) return <p className="text-text-muted p-4">No ITC data available for this quarter.</p>;

  return (
    <div className="space-y-6">
      <div className="bg-bg-surface border border-accent/30 rounded-xl p-5 flex items-center gap-4">
        <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
          <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <div>
          <p className="text-xs font-semibold text-text-muted uppercase">Total ITC Available</p>
          <p className="text-2xl font-bold font-mono text-green-500">{fmt(data.total_itc || 0)}</p>
        </div>
      </div>

      {data.by_rate?.length > 0 && (
        <div className="overflow-x-auto bg-bg-surface border border-border rounded-xl">
          <table className="w-full text-sm">
            <thead className="bg-bg-subtle text-text-secondary">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">GST Rate</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">CGST</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">SGST</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">IGST</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">Total</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">Bills</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.by_rate.map((r: any, i: number) => (
                <tr key={i} className="hover:bg-bg-overlay transition-colors">
                  <td className="px-4 py-3 font-medium">{r.gst_rate}%</td>
                  <td className="px-4 py-3 text-right font-mono">{fmt(r.cgst)}</td>
                  <td className="px-4 py-3 text-right font-mono">{fmt(r.sgst)}</td>
                  <td className="px-4 py-3 text-right font-mono">{fmt(r.igst)}</td>
                  <td className="px-4 py-3 text-right font-mono font-semibold">{fmt(r.total)}</td>
                  <td className="px-4 py-3 text-right text-text-muted">{r.bill_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ---------- HSN Tab ---------- */
function HSNTab({ data }: { data: any }) {
  const items = Array.isArray(data) ? data : [];

  return (
    <div>
      {items.length > 0 ? (
        <div className="overflow-x-auto bg-bg-surface border border-border rounded-xl">
          <table className="w-full text-sm">
            <thead className="bg-bg-subtle text-text-secondary">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">HSN/SAC</th>
                <th className="px-4 py-3 text-left font-semibold text-xs uppercase">Rate</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">Qty</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">Taxable</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">CGST</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">SGST</th>
                <th className="px-4 py-3 text-right font-semibold text-xs uppercase">IGST</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {items.map((r: any, i: number) => (
                <tr key={i} className="hover:bg-bg-overlay transition-colors">
                  <td className="px-4 py-3 font-mono font-semibold text-accent">{r.hsn_code}</td>
                  <td className="px-4 py-3">{r.gst_rate}%</td>
                  <td className="px-4 py-3 text-right font-mono">{r.total_qty}</td>
                  <td className="px-4 py-3 text-right font-mono">{fmt(r.taxable_value)}</td>
                  <td className="px-4 py-3 text-right font-mono">{fmt(r.cgst)}</td>
                  <td className="px-4 py-3 text-right font-mono">{fmt(r.sgst)}</td>
                  <td className="px-4 py-3 text-right font-mono">{fmt(r.igst)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-text-muted text-sm p-4 bg-bg-surface border border-border rounded-xl">
          No HSN data available for this quarter. HSN codes are assigned per invoice line item.
        </p>
      )}
    </div>
  );
}

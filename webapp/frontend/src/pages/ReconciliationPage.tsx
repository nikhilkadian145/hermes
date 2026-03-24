import { useState, useEffect, useCallback, useRef } from "react";
import { apiFetch } from '../api/client';
import { PageHeader } from "../components/layout/PageHeader";
import { Button } from "../components/ui/Button";

interface BankEntry {
  id: number;
  date: string;
  description: string;
  reference: string;
  amount: number;
  type: "debit" | "credit";
  status: "unmatched" | "matched" | "ignored";
  matched_to_payment_id?: number;
}

interface HermesPayment {
  id: number;
  amount: number;
  date: string;
  mode: string;
  reference: string;
}

interface MatchSuggestion {
  payment_id: number;
  bank_entry_id: number;
  confidence: number;
  bank_entry_summary: string;
}

export function ReconciliationPage() {
  const [unmatchedHermes, setUnmatchedHermes] = useState<HermesPayment[]>([]);
  const [unmatchedBank, setUnmatchedBank] = useState<BankEntry[]>([]);
  const [matched, setMatched] = useState<any[]>([]);
  const [suggestions, setSuggestions] = useState<MatchSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchRecData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch("/payments/reconciliation");
      if (res.ok) {
        const data = await res.json();
        setUnmatchedHermes(data.unmatched_hermes || []);
        setUnmatchedBank(data.unmatched_bank || []);
        setMatched(data.matched || []);
        setSuggestions(data.suggestions || []);
      }
    } catch (err) {
      console.error("Failed to fetch reconciliation data", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchRecData(); }, [fetchRecData]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await apiFetch("/upload/bank-statement", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        alert(`Successfully imported ${data.imported} bank rows.`);
        fetchRecData();
      } else {
        alert("Failed to import CSV.");
      }
    } catch (err) {
      console.error(err);
      alert("Error uploading bank statement.");
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
      setUploading(false);
    }
  };

  const confirmMatch = async (paymentId: number, bankEntryId: number) => {
    try {
      await apiFetch("/payments/reconciliation/confirm-match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payment_id: paymentId, bank_entry_id: bankEntryId })
      });
      fetchRecData();
    } catch (err) {
      console.error(err);
    }
  };

  const ignoreEntry = async (bankEntryId: number) => {
    try {
      await apiFetch("/payments/reconciliation/ignore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bank_entry_id: bankEntryId })
      });
      fetchRecData();
    } catch (err) {
      console.error(err);
    }
  };

  const fmt = (n: number) => "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 0 });
  const formatDate = (d: string) => d; // YYYY-MM-DD

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base">
      <div className="flex items-center justify-between px-6 border-b border-border bg-bg-surface shrink-0 h-16">
        <div>
          <h1 className="text-xl font-bold font-display text-text-base">Reconciliation</h1>
        </div>
        <div>
          <input 
            type="file" 
            accept=".csv" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            className="hidden" 
            id="bank-csv-upload" 
          />
          <Button 
            variant="primary" 
            size="sm" 
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? "Importing..." : "Import Bank CSV"}
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {/* Summary strip */}
        <div className="bg-bg-surface border border-border rounded-xl p-4 mb-6 flex justify-around text-center">
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Matched Payments</p>
            <p className="text-xl font-mono text-success">{matched.length}</p>
          </div>
          <div className="w-px bg-border my-2"></div>
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Unmatched in HERMES</p>
            <p className="text-xl font-mono text-warning">{unmatchedHermes.length}</p>
          </div>
          <div className="w-px bg-border my-2"></div>
          <div>
            <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Unmatched in Bank</p>
            <p className="text-xl font-mono text-warning">{unmatchedBank.length}</p>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-text-muted animate-pulse">Loading reconciliation data...</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* HERMES Panel */}
            <div className="bg-bg-surface border border-border rounded-xl flex flex-col h-[600px]">
              <div className="px-4 py-3 border-b border-border bg-bg-subtle shrink-0 font-semibold text-sm">
                Unmatched HERMES Payments
              </div>
              <div className="flex-1 overflow-y-auto p-2">
                {unmatchedHermes.map(h => {
                  const suggestion = suggestions.find(s => s.payment_id === h.id);
                  return (
                    <div key={h.id} className="p-3 mb-2 border border-border rounded-lg shadow-sm hover:border-accent/40 bg-bg-base transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-semibold text-text-base font-mono">{fmt(h.amount)}</p>
                          <p className="text-xs text-text-muted">{formatDate(h.date)} · <span className="uppercase">{h.mode}</span></p>
                        </div>
                        <span className="text-xs font-mono text-text-secondary bg-bg-subtle px-2 py-1 rounded">Ref: {h.reference || "N/A"}</span>
                      </div>
                      
                      {suggestion && (
                        <div className="mt-3 p-3 bg-accent-subtle/30 rounded border border-accent/20">
                          <p className="text-xs text-accent font-medium mb-2">
                            Possible match ↔ {suggestion.confidence}% confidence
                          </p>
                          <p className="text-sm font-mono text-text-base mb-3 truncate">{suggestion.bank_entry_summary}</p>
                          <div className="flex gap-2">
                            <Button variant="primary" size="sm" onClick={() => confirmMatch(h.id, suggestion.bank_entry_id)}>
                              ✓ Match
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
                {unmatchedHermes.length === 0 && <p className="text-center text-text-muted text-sm py-12">No unmatched payments.</p>}
              </div>
            </div>

            {/* Bank Statement Panel */}
            <div className="bg-bg-surface border border-border rounded-xl flex flex-col h-[600px]">
              <div className="px-4 py-3 border-b border-border bg-bg-subtle shrink-0 font-semibold text-sm">
                Unmatched Bank Entries
              </div>
              <div className="flex-1 overflow-y-auto p-2">
                {unmatchedBank.map(b => (
                  <div key={b.id} className="p-3 mb-2 border border-border rounded-lg shadow-sm hover:border-accent/40 bg-bg-base transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1 min-w-0 mr-3">
                        <p className="font-medium text-text-base text-sm truncate" title={b.description}>{b.description}</p>
                        <p className="text-xs text-text-muted">{formatDate(b.date)}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <p className={`font-mono font-semibold ${b.type === "credit" ? "text-success" : "text-text-base"}`}>
                          {b.type === "credit" ? "+" : "-"}{fmt(b.amount)}
                        </p>
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-2 border-t border-border pt-2">
                      <Button variant="ghost" size="sm" onClick={() => ignoreEntry(b.id)}>✗ Ignore</Button>
                    </div>
                  </div>
                ))}
                {unmatchedBank.length === 0 && <p className="text-center text-text-muted text-sm py-12">No raw bank entries.</p>}
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}

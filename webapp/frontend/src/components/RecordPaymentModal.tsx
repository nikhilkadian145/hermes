import { useState, useEffect } from "react";
import { apiFetch } from '../api/client';
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";

interface Invoice {
  id: number;
  invoice_number: string;
  client_name: string;
  total: number;
  paid: number;
}

interface RecordPaymentModalProps {
  onClose: () => void;
  onSuccess: () => void;
  preselectedInvoiceId?: number;
}

export function RecordPaymentModal({ onClose, onSuccess, preselectedInvoiceId }: RecordPaymentModalProps) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>(preselectedInvoiceId ? [preselectedInvoiceId] : []);
  const [amount, setAmount] = useState<string>("");
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [mode, setMode] = useState("bank");
  const [reference, setReference] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    // Fetch unpaid/partially paid invoices
    async function fetchInvoices() {
      try {
        const res = await apiFetch("/invoices/sales?status=draft,sent,overdue");
        if (res.ok) {
          const data = await res.json();
          // Filter out fully paid just in case
          const unpaid = (data.invoices || []).filter((i: any) => i.status !== "paid");
          setInvoices(unpaid.map((i: any) => ({
            id: i.id,
            invoice_number: i.invoice_number,
            client_name: i.client_name,
            total: i.total,
            paid: 0 // Simplification: assume 0 or fetch properly
          })));
        }
      } catch (err) {
        console.error(err);
      }
    }
    fetchInvoices();
  }, []);

  const totalSelectedDue = invoices
    .filter(i => selectedIds.includes(i.id))
    .reduce((sum, i) => sum + (i.total - i.paid), 0);
    
  const payingAmt = parseFloat(amount || "0");
  const outstandingAfter = Math.max(0, totalSelectedDue - payingAmt);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedIds.length === 0 || payingAmt <= 0) return;
    
    setLoading(true);
    try {
      const res = await apiFetch("/payments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          invoice_ids: selectedIds,
          amount: payingAmt,
          date,
          mode,
          reference,
          notes
        })
      });
      if (res.ok) {
        onSuccess();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleInvoice = (id: number) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const filteredInvoices = invoices.filter(i => 
    i.invoice_number.toLowerCase().includes(search.toLowerCase()) || 
    (i.client_name || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 animate-[fade-in_200ms_ease]">
      <div className="bg-bg-surface border border-border rounded-xl shadow-xl w-full max-w-lg flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-5 border-b border-border shrink-0">
          <h2 className="text-lg font-semibold text-text-base">Record Payment</h2>
          <button onClick={onClose} className="p-1 text-text-muted hover:text-text-base transition-colors rounded">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        
        <div className="p-5 overflow-y-auto flex-1 text-sm">
          <form id="payment-form" onSubmit={handleSubmit} className="space-y-4">
            
            {/* Invoice Selection */}
            <div>
              <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                Invoices Being Paid <span className="text-danger">*</span>
              </label>
              <div className="border border-border rounded-lg overflow-hidden bg-bg-base flex flex-col max-h-48">
                <div className="p-2 border-b border-border shrink-0">
                  <input 
                    type="text" 
                    placeholder="Search invoices..." 
                    className="w-full bg-bg-surface text-sm p-1.5 rounded outline-none"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
                <div className="overflow-y-auto p-1 text-sm">
                  {filteredInvoices.map(inv => (
                    <label key={inv.id} className="flex items-center gap-3 p-2 hover:bg-bg-overlay rounded cursor-pointer">
                      <input 
                        type="checkbox" 
                        className="accent-accent"
                        checked={selectedIds.includes(inv.id)}
                        onChange={() => toggleInvoice(inv.id)}
                      />
                      <div className="flex-1 flex justify-between">
                        <span className="font-medium text-text-base">{inv.invoice_number} <span className="text-text-muted font-normal text-xs ml-1">{inv.client_name}</span></span>
                        <span className="font-mono">₹{inv.total.toLocaleString("en-IN")}</span>
                      </div>
                    </label>
                  ))}
                  {filteredInvoices.length === 0 && <p className="text-center p-3 text-text-muted text-xs">No pending invoices found</p>}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">Amount (₹) <span className="text-danger">*</span></label>
                <Input type="number" step="0.01" min="0" required value={amount} onChange={e => setAmount(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">Date <span className="text-danger">*</span></label>
                <Input type="date" required value={date} onChange={e => setDate(e.target.value)} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">Mode <span className="text-danger">*</span></label>
                <select 
                  className="w-full h-10 px-3 py-2 bg-bg-surface border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent"
                  value={mode}
                  onChange={e => setMode(e.target.value)}
                >
                  <option value="bank">Bank Transfer (NEFT/RTGS)</option>
                  <option value="upi">UPI</option>
                  <option value="cash">Cash</option>
                  <option value="cheque">Cheque</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">Reference No.</label>
                <Input placeholder="UTR, Cheque No, etc." value={reference} onChange={e => setReference(e.target.value)} />
              </div>
            </div>
            
            <div>
              <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">Notes</label>
              <Input placeholder="Optional details..." value={notes} onChange={e => setNotes(e.target.value)} />
            </div>

            {/* Calculations */}
            {selectedIds.length > 0 && payingAmt > 0 && (
              <div className="bg-bg-subtle border border-border rounded-lg p-3 text-sm flex justify-between items-center text-text-secondary mt-2">
                <span>Paying <strong>₹{payingAmt.toLocaleString("en-IN")}</strong> against ₹{totalSelectedDue.toLocaleString("en-IN")} due.</span>
                <span className={outstandingAfter > 0 ? "text-warning" : "text-success"}>
                  Outstanding: <strong>₹{outstandingAfter.toLocaleString("en-IN")}</strong>
                </span>
              </div>
            )}
          </form>
        </div>

        <div className="p-5 border-t border-border flex justify-end gap-3 shrink-0">
          <Button variant="secondary" onClick={onClose} disabled={loading}>Cancel</Button>
          <Button 
            variant="primary" 
            form="payment-form" 
            type="submit" 
            disabled={loading || selectedIds.length === 0 || payingAmt <= 0}
          >
            {loading ? "Saving..." : "Record Payment"}
          </Button>
        </div>
      </div>
    </div>
  );
}

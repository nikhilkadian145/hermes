import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { format } from "date-fns";
import { clsx } from "clsx";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Skeleton } from "../components/ui/Skeleton";

export function InvoiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState<any>(null);
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState("");
  const [savingNotes, setSavingNotes] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const fetchInvoice = async () => {
    try {
      const res = await apiFetch(`/invoices/sales/${id}`);
      if (res.ok) {
        const data = await res.json();
        setInvoice(data);
        setNotes(data.notes || "");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPayments = async () => {
    try {
      const res = await apiFetch(`/invoices/sales/${id}/payment-history`);
      if (res.ok) {
        const data = await res.json();
        setPayments(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    Promise.all([fetchInvoice(), fetchPayments()]).finally(() => setLoading(false));
  }, [id]);

  const handleDownloadPdf = async () => {
    setDownloading(true);
    try {
      const res = await apiFetch(`/invoices/sales/${id}/pdf`);
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const filename = `${invoice?.invoice_number || 'invoice'}.pdf`;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert("PDF not available yet. It might still be generating.");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setDownloading(false);
    }
  };

  const markPaid = async () => {
    try {
      const res = await apiFetch(`/invoices/sales/${id}/mark-paid`, { method: "POST" });
      if (res.ok) {
        fetchInvoice();
        fetchPayments();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const voidInvoice = async () => {
    if (confirm("Are you sure you want to void this invoice? This cannot be undone.")) {
      try {
        const res = await apiFetch(`/invoices/sales/${id}/void`, { method: "POST" });
        if (res.ok) fetchInvoice();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const saveNotes = async () => {
    setSavingNotes(true);
    try {
      await apiFetch(`/invoices/sales/${id}/notes`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes })
      });
    } catch (err) {
      console.error(err);
    } finally {
      setSavingNotes(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <Skeleton width={200} height={32} className="mb-8" />
        <div className="flex gap-8">
          <Skeleton width="60%" height={600} />
          <Skeleton width="40%" height={400} />
        </div>
      </div>
    );
  }

  if (!invoice) return <div className="p-8">Invoice not found.</div>;

  const totalPaid = payments.reduce((acc, p) => acc + p.amount, 0);
  const remaining = invoice.total - totalPaid;

  const statusColors: Record<string, "default"|"success"|"warning"|"danger"> = {
    draft: "default",
    sent: "warning",
    paid: "success",
    overdue: "danger",
    cancelled: "default"
  };

  return (
    <div className="flex flex-col h-full bg-bg-base overflow-y-auto">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border bg-bg-surface sticky top-0 z-10 flex items-center gap-4">
        <button onClick={() => navigate("/invoices/sales")} className="p-2 -ml-2 text-text-muted hover:text-text-base hover:bg-bg-subtle rounded-lg">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
        </button>
        <div>
          <h1 className="text-xl font-semibold flex items-center gap-3">
            {invoice.invoice_number}
            <Badge variant={statusColors[invoice.status] || "default"} className="text-xs uppercase tracking-wider">{invoice.status}</Badge>
          </h1>
          <p className="text-sm text-text-muted mt-0.5">{invoice.client.name} &middot; ₹{invoice.total.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</p>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row p-6 gap-6 max-w-[1600px] mx-auto w-full">
        {/* Left: Invoice Preview */}
        <div className="flex-1 lg:max-w-[60%] w-full">
          <div className="bg-white text-black p-8 md:p-12 rounded-xl shadow-sm border border-border min-h-[800px]">
            <InvoicePreviewHTML invoice={invoice} />
          </div>
        </div>

        {/* Right: Actions & Details */}
        <div className="w-full lg:w-[400px] flex-shrink-0 flex flex-col gap-6">
          {/* Action Panel */}
          <div className="bg-bg-surface p-5 rounded-xl border border-border flex flex-col gap-3">
            <Button variant="primary" className="w-full justify-center" onClick={handleDownloadPdf} disabled={downloading}>
              {downloading ? "Downloading..." : "Download PDF"}
            </Button>
            
            {invoice.status !== 'paid' && invoice.status !== 'cancelled' && (
              <Button variant="secondary" className="w-full justify-center text-text-success border-text-success/30 hover:bg-text-success/10" onClick={markPaid}>
                Mark as Paid
              </Button>
            )}

            {invoice.status !== 'paid' && invoice.status !== 'cancelled' && (
              <Button variant="ghost" className="w-full justify-center text-text-danger hover:bg-text-danger/10" onClick={voidInvoice}>
                Void Invoice
              </Button>
            )}
          </div>

          {/* Timeline */}
          <div className="bg-bg-surface p-5 rounded-xl border border-border">
            <h3 className="text-sm font-semibold mb-4 text-text-secondary uppercase tracking-wider">Status Timeline</h3>
            <div className="relative pl-6 space-y-4 border-l-2 border-border ml-3">
              <TimelineItem 
                title="Created" 
                date={invoice.created_at} 
                active={true} 
                completed={true} 
              />
              <TimelineItem 
                title="Sent" 
                date={invoice.status === 'draft' ? null : invoice.created_at} 
                active={invoice.status !== 'draft'} 
                completed={invoice.status === 'paid' || invoice.status === 'overdue'} 
                isDanger={invoice.status === 'cancelled'}
              />
              <TimelineItem 
                title={invoice.status === 'cancelled' ? 'Voided' : invoice.status === 'overdue' ? 'Overdue' : 'Paid'} 
                date={payments.length > 0 ? payments[payments.length-1].payment_date : (invoice.status === 'overdue' ? 'Now' : null)} 
                active={invoice.status === 'paid' || invoice.status === 'overdue' || invoice.status === 'cancelled'} 
                completed={invoice.status === 'paid'}
                isDanger={invoice.status === 'overdue' || invoice.status === 'cancelled'}
              />
            </div>
          </div>

          {/* Payment History */}
          {payments.length > 0 && (
            <div className="bg-bg-surface overflow-hidden rounded-xl border border-border">
              <div className="px-5 py-4 border-b border-border bg-bg-subtle">
                <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">Payment History</h3>
              </div>
              <div className="p-0">
                <table className="w-full text-sm">
                  <thead className="bg-bg-base border-b border-border text-left text-text-muted">
                    <tr>
                      <th className="px-5 py-2 font-medium">Date</th>
                      <th className="px-5 py-2 font-medium">Mode</th>
                      <th className="px-5 py-2 font-medium text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payments.map(p => (
                      <tr key={p.id} className="border-b border-border/50 last:border-0">
                        <td className="px-5 py-2.5">{format(new Date(p.payment_date), "dd MMM yy")}</td>
                        <td className="px-5 py-2.5 capitalize">{p.mode}</td>
                        <td className="px-5 py-2.5 text-right font-mono text-text-success">
                          +₹{p.amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="px-5 py-3 bg-bg-subtle border-t border-border flex justify-between text-sm">
                <span className="text-text-muted">Remaining Balance:</span>
                <span className={clsx("font-mono font-medium", remaining > 0 ? "text-text-warning" : "text-text-success")}>
                  ₹{remaining.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="bg-bg-surface p-5 rounded-xl border border-border">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">Internal Notes</h3>
              {savingNotes && <span className="text-xs text-text-muted">Saving...</span>}
            </div>
            <textarea
              className="w-full bg-bg-base border border-border rounded-lg p-3 text-sm focus:outline-none focus:border-accent min-h-[120px] resize-y"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              onBlur={saveNotes}
              placeholder="Add private notes about this invoice..."
            />
          </div>

        </div>
      </div>
    </div>
  );
}

function TimelineItem({ title, date, active, completed, isDanger = false }: any) {
  return (
    <div className="relative">
      <div className={clsx(
        "absolute -left-[31px] top-0.5 w-[14px] h-[14px] rounded-full border-2 bg-bg-surface",
        completed ? "border-accent bg-accent" : 
        active && isDanger ? "border-text-danger bg-text-danger" :
        active ? "border-accent" : "border-border"
      )} />
      <div className={clsx("text-sm font-medium", !active && "text-text-muted", isDanger && active && "text-text-danger")}>
        {title}
      </div>
      {date && <div className="text-xs text-text-muted mt-0.5">{typeof date === 'string' && date !== 'Now' ? format(new Date(date), "dd MMM yyyy, HH:mm") : date}</div>}
    </div>
  );
}

// Minimal HTML re-implementation of the invoice PDF
function InvoicePreviewHTML({ invoice }: { invoice: any }) {
  const { client, items } = invoice;
  return (
    <div className="font-sans text-[13px] leading-relaxed">
      {/* Header */}
      <div className="flex justify-between items-start mb-12">
        <div>
          <h1 className="text-4xl font-light text-neutral-800 tracking-tight mb-2">INVOICE</h1>
          <div className="text-neutral-500 font-mono text-sm">{invoice.invoice_number}</div>
        </div>
        <div className="text-right">
          <div className="font-semibold text-neutral-800 text-lg">HERMES DEMO BUSINESS</div>
          <div className="text-neutral-500 mt-1">
            GSTIN: 29ABCDE1234F1Z5<br/>
            123 Business Road, Tech Park<br/>
            Bangalore, Karnataka 560001
          </div>
        </div>
      </div>

      <div className="flex justify-between mb-12 border-t border-b border-neutral-100 py-6">
        <div>
          <div className="text-xs font-semibold text-neutral-400 uppercase tracking-widest mb-2">Billed To</div>
          <div className="font-medium text-neutral-800 text-base">{client.name}</div>
          {client.gstin && <div className="text-neutral-600 mt-1">GSTIN: {client.gstin}</div>}
          <div className="text-neutral-600 mt-1 whitespace-pre-line">{client.address}</div>
        </div>
        <div className="text-right flex gap-8">
          <div>
            <div className="text-xs font-semibold text-neutral-400 uppercase tracking-widest mb-2">Issue Date</div>
            <div className="text-neutral-800 font-medium">{format(new Date(invoice.issue_date), "dd MMM yyyy")}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-neutral-400 uppercase tracking-widest mb-2">Due Date</div>
            <div className="text-neutral-800 font-medium">{format(new Date(invoice.due_date), "dd MMM yyyy")}</div>
          </div>
        </div>
      </div>

      {/* Items */}
      <table className="w-full mb-8">
        <thead>
          <tr className="text-left text-xs font-semibold text-neutral-400 uppercase tracking-widest border-b-2 border-neutral-200">
            <th className="py-3 font-medium">Description</th>
            <th className="py-3 font-medium text-right">Qty</th>
            <th className="py-3 font-medium text-right">Rate</th>
            {invoice.tax_amount > 0 && <th className="py-3 font-medium text-right">Tax</th>}
            <th className="py-3 font-medium text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item: any) => (
            <tr key={item.id} className="border-b border-neutral-100">
              <td className="py-4 text-neutral-800">
                {item.description}
                {item.hsn_code && <div className="text-xs text-neutral-400 font-mono mt-1">HSN: {item.hsn_code}</div>}
              </td>
              <td className="py-4 text-right text-neutral-600 font-mono">{item.quantity}</td>
              <td className="py-4 text-right text-neutral-600 font-mono">₹{item.unit_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
              {invoice.tax_amount > 0 && (
                <td className="py-4 text-right text-neutral-600 font-mono">
                  {item.gst_rate ? `${item.gst_rate}%` : '-'}
                </td>
              )}
              <td className="py-4 text-right text-neutral-800 font-mono font-medium">₹{item.amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Totals */}
      <div className="flex justify-end">
        <div className="w-64">
          <div className="flex justify-between py-2 text-neutral-600">
            <span>Subtotal</span>
            <span className="font-mono">₹{invoice.subtotal.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
          </div>
          {invoice.tax_amount > 0 && (
            <div className="flex justify-between py-2 text-neutral-600">
              <span>GST</span>
              <span className="font-mono">₹{invoice.tax_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
            </div>
          )}
          <div className="flex justify-between py-4 text-lg font-bold text-neutral-900 border-t-2 border-neutral-200 mt-2">
            <span>Total</span>
            <span className="font-mono">₹{invoice.total.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
          </div>
        </div>
      </div>
      
      {invoice.total_in_words && (
        <div className="text-neutral-500 mt-4 text-sm text-right italic">
          Amount in words: {invoice.total_in_words}
        </div>
      )}
    </div>
  );
}

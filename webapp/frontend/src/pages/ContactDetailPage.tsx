import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

interface ContactDetail {
  id: number;
  name: string;
  phone: string;
  email: string;
  address: string;
  gstin: string;
  client_type: string;
  notes: string;
  total_billed: number;
  total_paid: number;
  outstanding: number;
  last_payment_date: string | null;
  invoices: Array<{
    id: number;
    invoice_number: string;
    issue_date: string;
    due_date: string;
    total: number;
    status: string;
  }>;
  payments: Array<{
    id: number;
    amount: number;
    payment_date: string;
    mode: string;
    reference: string;
    invoice_number: string;
  }>;
}

interface LedgerEntry {
  date: string;
  description: string;
  debit: number;
  credit: number;
  balance: number;
}

const TABS = ["Overview", "Transactions", "Ledger", "Notes"] as const;
type Tab = typeof TABS[number];

export function ContactDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [contact, setContact] = useState<ContactDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("Overview");
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [notes, setNotes] = useState("");
  const [notesSaving, setNotesSaving] = useState(false);

  const fmt = (n: number) => "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 0 });
  const formatDate = (d: string | null) => {
    if (!d) return "—";
    try { return new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }); }
    catch { return d; }
  };

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch(`/contacts/${id}`);
        if (res.ok) {
          const data = await res.json();
          setContact(data);
          setNotes(data.notes || "");
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  // Fetch ledger when tab changes
  useEffect(() => {
    if (tab !== "Ledger") return;
    async function loadLedger() {
      setLedgerLoading(true);
      try {
        const res = await apiFetch(`/contacts/${id}/ledger`);
        if (res.ok) {
          const data = await res.json();
          setLedger(data.entries || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLedgerLoading(false);
      }
    }
    loadLedger();
  }, [tab, id]);

  const saveNotes = async () => {
    setNotesSaving(true);
    try {
      await apiFetch(`/contacts/${id}/notes`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes }),
      });
    } catch (err) {
      console.error(err);
    } finally {
      setNotesSaving(false);
    }
  };

  const downloadCSV = () => {
    const header = "Date,Description,Debit,Credit,Balance";
    const rows = ledger.map(e =>
      `${e.date},"${e.description}",${e.debit},${e.credit},${e.balance}`
    );
    const csv = [header, ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ledger_${contact?.name || id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <div className="p-8 text-text-muted animate-pulse">Loading contact...</div>;
  if (!contact) return <div className="p-8 text-danger">Contact not found.</div>;

  return (
    <div className="animate-fade-in">
      {/* Back */}
      <button
        onClick={() => navigate("/contacts")}
        className="text-sm text-text-muted hover:text-accent transition-colors mb-4 inline-flex items-center gap-1"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
        All Contacts
      </button>

      {/* Header Card */}
      <div className="bg-bg-surface border border-border rounded-xl p-5 mb-6 flex flex-col sm:flex-row justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-full bg-accent-subtle flex items-center justify-center text-accent text-lg font-bold shrink-0">
            {contact.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-semibold text-text-base">{contact.name}</h1>
              <Badge
                status={contact.client_type === "customer" ? "paid" : "sent"}
                label={contact.client_type === "customer" ? "CUSTOMER" : "VENDOR"}
              />
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1.5 text-sm text-text-secondary">
              {contact.gstin && <span className="font-mono">{contact.gstin}</span>}
              {contact.email && <span>{contact.email}</span>}
              {contact.phone && <span>{contact.phone}</span>}
            </div>
            {contact.address && <p className="text-xs text-text-muted mt-1">{contact.address}</p>}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-0 border-b border-border mb-6 overflow-x-auto">
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-5 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors
              ${tab === t
                ? "border-accent text-accent"
                : "border-transparent text-text-secondary hover:text-text-base hover:border-border"
              }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[300px]">
        {/* OVERVIEW */}
        {tab === "Overview" && (
          <div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {[
                { label: "Total Billed", value: fmt(contact.total_billed), color: "text-text-base" },
                { label: "Total Paid", value: fmt(contact.total_paid), color: "text-success" },
                { label: "Outstanding", value: fmt(contact.outstanding), color: contact.outstanding > 0 ? "text-warning" : "text-success" },
                { label: "Last Payment", value: formatDate(contact.last_payment_date), color: "text-text-base" },
              ].map(card => (
                <div key={card.label} className="bg-bg-surface border border-border rounded-xl p-4">
                  <p className="text-xs text-text-muted uppercase tracking-wider mb-1">{card.label}</p>
                  <p className={`text-xl font-semibold font-mono ${card.color}`}>{card.value}</p>
                </div>
              ))}
            </div>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                window.open(`http://localhost:8000/api/contacts/${id}/statement/pdf`, "_blank");
              }}
            >
              Download Statement
            </Button>
          </div>
        )}

        {/* TRANSACTIONS */}
        {tab === "Transactions" && (
          <div>
            <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">Invoices</h3>
            <div className="overflow-x-auto mb-6">
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="bg-bg-subtle">
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Invoice #</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Due</th>
                    <th className="px-4 py-2 text-right text-xs font-medium uppercase tracking-wider text-text-secondary">Amount</th>
                    <th className="px-4 py-2 text-center text-xs font-medium uppercase tracking-wider text-text-secondary">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {contact.invoices.map((inv, i) => (
                    <tr
                      key={inv.id}
                      className={`border-b border-border h-11 cursor-pointer hover:bg-bg-overlay ${i % 2 === 0 ? "bg-bg-surface" : "bg-bg-subtle"}`}
                      onClick={() => navigate(`/invoices/sales/${inv.id}`)}
                    >
                      <td className="px-4 font-medium text-accent">{inv.invoice_number}</td>
                      <td className="px-4 text-text-secondary">{formatDate(inv.issue_date)}</td>
                      <td className="px-4 text-text-secondary">{formatDate(inv.due_date)}</td>
                      <td className="px-4 text-right font-mono">{fmt(inv.total)}</td>
                      <td className="px-4 text-center">
                        <Badge status={inv.status === "paid" ? "paid" : inv.status === "overdue" ? "overdue" : inv.status === "sent" ? "sent" : "draft"} />
                      </td>
                    </tr>
                  ))}
                  {contact.invoices.length === 0 && (
                    <tr><td colSpan={5} className="text-center py-8 text-text-muted">No invoices.</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">Payments</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="bg-bg-subtle">
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Mode</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Reference</th>
                    <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Invoice</th>
                    <th className="px-4 py-2 text-right text-xs font-medium uppercase tracking-wider text-text-secondary">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {contact.payments.map((pay, i) => (
                    <tr key={pay.id} className={`border-b border-border h-11 ${i % 2 === 0 ? "bg-bg-surface" : "bg-bg-subtle"}`}>
                      <td className="px-4 text-text-secondary">{formatDate(pay.payment_date)}</td>
                      <td className="px-4 capitalize">{pay.mode}</td>
                      <td className="px-4 font-mono text-xs">{pay.reference || "—"}</td>
                      <td className="px-4 text-accent">{pay.invoice_number || "—"}</td>
                      <td className="px-4 text-right font-mono font-semibold text-success">{fmt(pay.amount)}</td>
                    </tr>
                  ))}
                  {contact.payments.length === 0 && (
                    <tr><td colSpan={5} className="text-center py-8 text-text-muted">No payments recorded.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* LEDGER */}
        {tab === "Ledger" && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <p className="text-sm text-text-muted">Running balance ledger</p>
              <Button variant="secondary" size="sm" onClick={downloadCSV} disabled={ledger.length === 0}>
                Download CSV
              </Button>
            </div>

            {ledgerLoading ? (
              <div className="flex items-center justify-center h-32 text-text-muted animate-pulse">Loading ledger...</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr className="bg-bg-subtle">
                      <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Date</th>
                      <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Description</th>
                      <th className="px-4 py-2 text-right text-xs font-medium uppercase tracking-wider text-text-secondary">Debit</th>
                      <th className="px-4 py-2 text-right text-xs font-medium uppercase tracking-wider text-text-secondary">Credit</th>
                      <th className="px-4 py-2 text-right text-xs font-medium uppercase tracking-wider text-text-secondary">Balance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* Opening balance pinned */}
                    <tr className="bg-bg-overlay border-b border-border font-semibold">
                      <td className="px-4 py-2">—</td>
                      <td className="px-4 py-2">Opening Balance</td>
                      <td className="px-4 py-2 text-right font-mono">—</td>
                      <td className="px-4 py-2 text-right font-mono">—</td>
                      <td className="px-4 py-2 text-right font-mono">{fmt(0)}</td>
                    </tr>
                    {ledger.map((entry, i) => (
                      <tr key={i} className={`border-b border-border h-10 ${i % 2 === 0 ? "bg-bg-surface" : "bg-bg-subtle"}`}>
                        <td className="px-4 text-text-secondary whitespace-nowrap">{formatDate(entry.date)}</td>
                        <td className="px-4 text-text-base">{entry.description}</td>
                        <td className="px-4 text-right font-mono">{entry.debit > 0 ? fmt(entry.debit) : "—"}</td>
                        <td className="px-4 text-right font-mono text-success">{entry.credit > 0 ? fmt(entry.credit) : "—"}</td>
                        <td className={`px-4 text-right font-mono font-semibold ${entry.balance > 0 ? "text-warning" : "text-success"}`}>
                          {fmt(entry.balance)}
                        </td>
                      </tr>
                    ))}
                    {ledger.length === 0 && (
                      <tr><td colSpan={5} className="text-center py-8 text-text-muted">No ledger entries.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* NOTES */}
        {tab === "Notes" && (
          <div className="max-w-2xl">
            <p className="text-sm text-text-muted mb-2">Free-text notes about this contact. Saves when you click away.</p>
            <textarea
              className="w-full h-40 p-4 rounded-xl border border-border bg-bg-surface text-text-base text-sm resize-y focus:outline-none focus:ring-2 focus:ring-accent/50 transition-shadow"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              onBlur={saveNotes}
              placeholder="Add notes about this contact..."
            />
            {notesSaving && <p className="text-xs text-accent mt-1 animate-pulse">Saving...</p>}
          </div>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from '../api/client';
import { PageHeader } from "../components/layout/PageHeader";
import { Button } from "../components/ui/Button";
import { DataTable } from "../components/ui/DataTable";
import type { ColumnDef } from "../components/ui/DataTable";
import { RecordPaymentModal } from "../components/RecordPaymentModal";
import { useNavigate } from "react-router-dom";

export function PaymentsPage() {
  const navigate = useNavigate();
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchPayments = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/payments?page=${page}`);
      if (res.ok) {
        const data = await res.json();
        setPayments(data.payments || []);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { fetchPayments(); }, [fetchPayments]);

  const fmt = (n: number) => "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 0 });
  const formatDate = (d: string) => {
    if (!d) return "—";
    try { return new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }); }
    catch { return d; }
  };

  const columns: ColumnDef<any>[] = [
    { key: "payment_date", header: "Date", render: (r) => formatDate(r.payment_date) },
    { key: "client_name", header: "Client", render: (r) => <span className="font-medium">{r.client_name || "—"}</span> },
    { key: "invoice_number", header: "Linked Invoice", render: (r) => <span className="text-accent">{r.invoice_number || "—"}</span> },
    { key: "mode", header: "Mode", render: (r) => <span className="capitalize">{r.mode}</span> },
    { key: "reference", header: "Reference", render: (r) => <span className="font-mono text-xs text-text-muted">{r.reference || "—"}</span> },
    { key: "amount", header: "Amount", align: "right" as const, render: (r) => <span className="font-mono font-semibold text-success">{fmt(r.amount)}</span> },
  ];

  return (
    <div className="animate-fade-in flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <PageHeader title="Payments" />
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={() => navigate("/payments/reconciliation")}>
            Reconciliation
          </Button>
          <Button variant="primary" onClick={() => setModalOpen(true)}>
            Record Payment
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <DataTable
          columns={columns}
          data={payments}
          loading={loading}
          rowKey={(r) => r.id}
          emptyState={
            <div className="py-16 flex flex-col items-center justify-center text-text-muted">
              <p className="text-sm">No payments recorded yet.</p>
            </div>
          }
        />
      </div>

      {modalOpen && (
        <RecordPaymentModal 
          onClose={() => setModalOpen(false)} 
          onSuccess={() => { setModalOpen(false); fetchPayments(); }}
        />
      )}
    </div>
  );
}

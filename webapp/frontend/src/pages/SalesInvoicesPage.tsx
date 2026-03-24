import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiFetch } from '../api/client';
import { format } from "date-fns";
import { clsx } from "clsx";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Badge } from "../components/ui/Badge";
import { DataTable } from "../components/ui/DataTable";
import type { ColumnDef } from "../components/ui/DataTable";

interface InvoiceSummary {
  total_amount: number;
  paid_amount: number;
  outstanding_amount: number;
  count_by_status: Record<string, number>;
}

interface InvoiceListItem {
  id: number;
  invoice_number: string;
  client_name: string;
  issue_date: string;
  due_date: string;
  total: number;
  tax_amount: number;
  status: string;
}

export function SalesInvoicesPage() {
  const navigate = useNavigate();
  const [invoices, setInvoices] = useState<InvoiceListItem[]>([]);
  const [summary, setSummary] = useState<InvoiceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("All");
  const [search, setSearch] = useState<string>("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const q = new URLSearchParams();
      q.set("page", page.toString());
      if (statusFilter !== "All") q.set("status", statusFilter.toLowerCase());
      if (search) q.set("search", search);

      const res = await apiFetch(`/invoices/sales?${q.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setInvoices(data.items);
        setSummary(data.summary);
        setTotalPages(data.pages);
        setTotalItems(data.total);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Debounce search
    const timer = setTimeout(() => {
      fetchInvoices();
    }, 300);
    return () => clearTimeout(timer);
  }, [statusFilter, search, page]);

  const handleDuplicate = (id: number) => {
    console.log("Duplicate", id);
    // STUB
  };

  const statusColors: Record<string, "default"|"success"|"warning"|"danger"> = {
    draft: "default",
    sent: "warning",
    paid: "success",
    overdue: "danger",
    cancelled: "default"
  };

  const columns: ColumnDef<InvoiceListItem>[] = [
    {
      key: "invoice_number",
      header: "Invoice #",
      render: (row) => <span className="font-medium">{row.invoice_number}</span>
    },
    {
      key: "client_name",
      header: "Customer",
      render: (row) => row.client_name
    },
    {
      key: "issue_date",
      header: "Issue Date",
      render: (row) => format(new Date(row.issue_date), "dd MMM yyyy")
    },
    {
      key: "due_date",
      header: "Due Date",
      render: (row) => {
        const isPast = new Date(row.due_date) < new Date() && row.status !== 'paid' && row.status !== 'cancelled';
        return (
          <span className={isPast ? "text-text-danger font-medium" : ""}>
            {format(new Date(row.due_date), "dd MMM yyyy")}
          </span>
        );
      }
    },
    {
      key: "total",
      header: "Amount",
      align: 'right',
      render: (row) => `₹${row.total.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <Badge variant={statusColors[row.status] || "default"}>
          {row.status.toUpperCase()}
        </Badge>
      )
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => (
        <div className="flex justify-end pr-2" onClick={e => e.stopPropagation()}>
          <RowActionsMenu 
            invoice={row} 
            onRefresh={fetchInvoices}
          />
        </div>
      )
    }
  ];

  return (
    <div className="flex flex-col h-full bg-bg-base p-6 gap-6 overflow-y-auto">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Sales Invoices</h1>
          <p className="text-text-muted text-sm mt-1">Manage all outgoing invoices and payments.</p>
        </div>
        <Button onClick={() => navigate("/chat")} variant="primary">
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Invoice
        </Button>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap gap-4 items-center bg-bg-surface p-4 rounded-xl border border-border">
        <div className="w-64">
          <Input 
            placeholder="Search by customer or invoice #" 
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            icon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>}
          />
        </div>
        
        <div className="flex bg-bg-subtle p-1 rounded-lg border border-border">
          {["All", "Draft", "Sent", "Paid", "Overdue", "Cancelled"].map(s => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setPage(1); }}
              className={clsx(
                "px-4 py-1.5 text-sm font-medium rounded-md transition-colors",
                statusFilter === s ? "bg-bg-surface text-text-base shadow-sm" : "text-text-muted hover:text-text-base"
              )}
            >
              {s}
            </button>
          ))}
        </div>
        
        {(search || statusFilter !== "All") && (
          <button 
            onClick={() => { setSearch(""); setStatusFilter("All"); setPage(1); }}
            className="text-sm text-accent hover:underline ml-auto font-medium"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Summary Bar */}
      {summary && (
        <div className="flex flex-wrap gap-8 text-sm font-mono text-text-muted bg-bg-surface/50 p-3 rounded-lg border border-border/50">
          <div><span className="text-text-base font-medium">Showing:</span> {totalItems} invoices</div>
          <div><span className="text-text-base font-medium">Total:</span> ₹{summary.total_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
          <div className="text-text-success"><span className="text-text-base font-medium">Paid:</span> ₹{summary.paid_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
          <div className="text-text-danger"><span className="text-text-base font-medium">Outstanding:</span> ₹{summary.outstanding_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
        </div>
      )}

      {/* Data Table */}
      <div className="bg-bg-surface rounded-xl border border-border overflow-hidden flex-1 shadow-sm">
        <DataTable
          columns={columns}
          data={invoices}
          loading={loading}
          onRowClick={(row) => navigate(`/invoices/sales/${row.id}`)}
          emptyState={
            <div className="p-16 text-center text-text-muted flex flex-col items-center">
              <svg className="w-16 h-16 mb-4 text-border" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-[16px] font-medium text-text-base mb-2">No invoices found</p>
              <p className="mb-6 max-w-sm">There are no invoices matching your filters. Chat with HERMES to create your first invoice.</p>
              <Button onClick={() => navigate("/chat")} variant="primary">
                Open Chat &rarr;
              </Button>
            </div>
          }
        />
        
        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-bg-subtle">
            <span className="text-sm text-text-secondary">
              Showing {(page - 1) * 50 + 1}–{Math.min(page * 50, totalItems)} of {totalItems} invoices
            </span>
            <div className="flex gap-2">
              <Button 
                variant="secondary" 
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
              >
                &larr; Prev
              </Button>
              <div className="flex items-center gap-1 mx-2 text-sm text-text-muted">
                <span className="text-text-base font-medium">{page}</span> / {totalPages}
              </div>
              <Button 
                variant="secondary" 
                disabled={page === totalPages}
                onClick={() => setPage(p => p + 1)}
              >
                Next &rarr;
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Minimal row actions dropdown
function RowActionsMenu({ invoice, onRefresh }: { invoice: InvoiceListItem, onRefresh: () => void }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const downloadPdf = async () => {
    setOpen(false);
    window.location.href = `http://localhost:8000/api/invoices/sales/${invoice.id}/pdf`;
  };

  const markPaid = async () => {
    setOpen(false);
    await apiFetch(`/invoices/sales/${invoice.id}/mark-paid`, { method: "POST" });
    onRefresh();
  };

  const voidInvoice = async () => {
    setOpen(false);
    if (confirm("Are you sure you want to void this invoice?")) {
      await apiFetch(`/invoices/sales/${invoice.id}/void`, { method: "POST" });
      onRefresh();
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button 
        onClick={() => setOpen(!open)}
        className="p-1 rounded-md text-text-muted hover:text-text-base hover:bg-bg-subtle transition-colors"
      >
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
        </svg>
      </button>
      
      {open && (
        <div className="absolute right-0 top-full mt-1 w-48 bg-bg-surface rounded-xl shadow-lg border border-border py-1 z-50">
          <Link 
            to={`/invoices/sales/${invoice.id}`}
            className="block w-full text-left px-4 py-2 text-sm hover:bg-bg-subtle"
          >
            View Details
          </Link>
          <button 
            onClick={downloadPdf}
            className="block w-full text-left px-4 py-2 text-sm hover:bg-bg-subtle"
          >
            Download PDF
          </button>
          
          {invoice.status !== 'paid' && invoice.status !== 'cancelled' && (
            <button 
              onClick={markPaid}
              className="block w-full text-left px-4 py-2 text-sm hover:bg-bg-subtle text-text-success"
            >
              Mark as Paid
            </button>
          )}
          
          {invoice.status !== 'paid' && invoice.status !== 'cancelled' && (
            <button 
              onClick={voidInvoice}
              className="block w-full text-left px-4 py-2 text-sm hover:bg-bg-subtle text-text-danger"
            >
              Void Invoice
            </button>
          )}
        </div>
      )}
    </div>
  );
}

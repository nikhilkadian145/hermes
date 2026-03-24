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

interface BillSummary {
  total_amount: number;
  finalized_amount: number;
  pending_amount: number;
  count_by_status: Record<string, number>;
}

interface BillListItem {
  expense_id: number | null;
  upload_id: number | null;
  vendor: string;
  bill_number: string;
  date: string;
  total: number;
  status: string;
  filename: string | null;
  error_message: string | null;
  created_at: string;
}

export function PurchaseBillsPage() {
  const navigate = useNavigate();
  const [bills, setBills] = useState<BillListItem[]>([]);
  const [summary, setSummary] = useState<BillSummary | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("All");
  const [search, setSearch] = useState<string>("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const fetchBills = async (isBackground = false) => {
    if (!isBackground) setLoading(true);
    try {
      const q = new URLSearchParams();
      q.set("page", page.toString());
      if (statusFilter !== "All") q.set("status", statusFilter.toLowerCase());
      if (search) q.set("search", search);

      const res = await apiFetch(`/invoices/purchases?${q.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setBills(data.items);
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

  // Initial fetch and debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchBills();
    }, 300);
    return () => clearTimeout(timer);
  }, [statusFilter, search, page]);

  // Polling mechanism if any bills are actively processing
  useEffect(() => {
    const hasProcessing = bills.some(b => b.status === 'queued' || b.status === 'processing');
    if (!hasProcessing) return;
    
    const interval = setInterval(() => {
      fetchBills(true); // background refresh
    }, 5000);
    return () => clearInterval(interval);
  }, [bills, statusFilter, search, page]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'queued':
        return <Badge status="custom" label="QUEUED" className="bg-neutral-bg text-neutral" />;
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-accent-subtle text-accent border border-accent/20 animate-pulse">
            <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            PROCESSING
          </span>
        );
      case 'review_needed':
        return <Badge status="review" label="NEEDS REVIEW" />;
      case 'error':
        return <Badge status="error" />;
      case 'finalized':
      default:
        return <Badge status="finalized" />;
    }
  };

  const columns: ColumnDef<BillListItem>[] = [
    {
      key: "vendor",
      header: "Vendor",
      render: (row) => (
        <div className="flex flex-col">
          <span className="font-medium text-text-base">{row.vendor === 'Unknown Vendor' && row.filename ? row.filename : row.vendor}</span>
          {row.bill_number && row.bill_number !== 'N/A' && <span className="text-xs text-text-muted mt-0.5">#{row.bill_number}</span>}
        </div>
      )
    },
    {
      key: "date",
      header: "Date",
      render: (row) => format(new Date(row.date), "dd MMM yyyy")
    },
    {
      key: "total",
      header: "Amount",
      align: 'right',
      render: (row) => {
        if (row.status !== 'finalized' && row.total === 0) return <span className="text-text-muted">-</span>;
        return `₹${row.total.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
      }
    },
    {
      key: "status",
      header: "Status",
      render: (row) => getStatusBadge(row.status)
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (row) => (
        <div className="flex justify-end pr-2" onClick={e => e.stopPropagation()}>
          <RowActionsMenu 
            bill={row} 
            onRefresh={() => fetchBills()}
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
          <h1 className="text-2xl font-semibold tracking-tight">Purchase Bills</h1>
          <p className="text-text-muted text-sm mt-1">Manage vendor bills and track AI data extraction.</p>
        </div>
        <Button onClick={() => navigate("/upload")} variant="primary">
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Upload Bills
        </Button>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap gap-4 items-center bg-bg-surface p-4 rounded-xl border border-border">
        <div className="w-64">
          <Input 
            placeholder="Search vendor or bill #" 
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        
        <div className="flex bg-bg-subtle p-1 rounded-lg border border-border overflow-x-auto">
          {["All", "Needs Review", "Processing", "Finalized", "Error"].map(s => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setPage(1); }}
              className={clsx(
                "px-4 py-1.5 text-sm font-medium rounded-md transition-colors whitespace-nowrap",
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
            className="text-sm text-accent hover:underline ml-auto font-medium whitespace-nowrap"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Summary Bar */}
      {summary && (
        <div className="flex flex-wrap gap-8 text-sm font-mono text-text-muted bg-bg-surface/50 p-3 rounded-lg border border-border/50">
          <div><span className="text-text-base font-medium">Pending Review:</span> {summary.count_by_status['review_needed'] || 0}</div>
          <div><span className="text-text-base font-medium">Processing:</span> {(summary.count_by_status['queued'] || 0) + (summary.count_by_status['processing'] || 0)}</div>
          <div className="text-text-success"><span className="text-text-base font-medium">Finalized:</span> ₹{summary.finalized_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
        </div>
      )}

      {/* Data Table */}
      <div className="bg-bg-surface rounded-xl border border-border overflow-hidden flex-1 shadow-sm">
        <DataTable
          columns={columns}
          data={bills}
          loading={loading && !bills.length}
          onRowClick={(row) => {
            if (row.status === 'review_needed' || row.status === 'finalized') {
              if (row.expense_id) navigate(`/invoices/purchases/review/${row.expense_id}`);
            }
          }}
          emptyState={
            <div className="p-16 text-center text-text-muted flex flex-col items-center">
              <svg className="w-16 h-16 mb-4 text-border" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-[16px] font-medium text-text-base mb-2">No bills found</p>
              <p className="mb-6 max-w-sm">Upload your first vendor bill to let HERMES automatically extract the details.</p>
              <Button onClick={() => navigate("/upload")} variant="primary">
                Upload Bill &rarr;
              </Button>
            </div>
          }
        />
        
        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-bg-subtle">
            <span className="text-sm text-text-secondary">
              Showing {(page - 1) * 50 + 1}–{Math.min(page * 50, totalItems)} of {totalItems} bills
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
function RowActionsMenu({ bill, onRefresh }: { bill: BillListItem, onRefresh: () => void }) {
  const navigate = useNavigate();
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

  const handleAction = async (action: 'view' | 'reprocess') => {
    setOpen(false);
    if (action === 'view') {
      if (bill.expense_id) navigate(`/invoices/purchases/review/${bill.expense_id}`);
    } else if (action === 'reprocess') {
      if (bill.upload_id) {
        await apiFetch(`/upload/queue/${bill.upload_id}/reprocess`, { method: "POST" });
        onRefresh();
      }
    }
  };

  if (bill.status === 'queued' || bill.status === 'processing') {
    return <span className="text-text-muted text-sm px-4">Wait...</span>;
  }

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
        <div className="absolute right-0 top-full mt-1 w-40 bg-bg-surface rounded-xl shadow-lg border border-border py-1 z-50">
          {(bill.status === 'review_needed' || bill.status === 'finalized') && (
            <button 
              onClick={() => handleAction('view')}
              className={clsx(
                "block w-full text-left px-4 py-2 text-sm hover:bg-bg-subtle",
                bill.status === 'review_needed' && "text-text-warning font-medium"
              )}
            >
              {bill.status === 'review_needed' ? 'Review & Finalize' : 'View Detail'}
            </button>
          )}
          
          {bill.status === 'error' && (
            <button 
              onClick={() => handleAction('reprocess')}
              className="block w-full text-left px-4 py-2 text-sm hover:bg-bg-subtle"
            >
              Retry
            </button>
          )}
        </div>
      )}
    </div>
  );
}

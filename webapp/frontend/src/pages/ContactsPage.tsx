import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { PageHeader } from "../components/layout/PageHeader";
import { Input } from "../components/ui/Input";
import { Badge } from "../components/ui/Badge";
import { DataTable } from "../components/ui/DataTable";
import type { ColumnDef } from "../components/ui/DataTable";

interface Contact {
  id: number;
  name: string;
  phone: string;
  email: string;
  gstin: string;
  client_type: string;
  outstanding: number;
  total_transactions: number;
  overdue_count: number;
}

const TYPE_OPTIONS = [
  { key: "all", label: "All" },
  { key: "customer", label: "Customers" },
  { key: "vendor", label: "Vendors" },
];

export function ContactsPage() {
  const navigate = useNavigate();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [type, setType] = useState("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const searchRef = useRef<ReturnType<typeof setTimeout>>();

  const fetchContacts = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (type !== "all") params.set("type", type);
      if (search) params.set("search", search);
      params.set("page", String(page));

      const res = await apiFetch(`/contacts?${params}`);
      if (res.ok) {
        const data = await res.json();
        setContacts(data.contacts || []);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      console.error("Failed to fetch contacts", err);
    } finally {
      setLoading(false);
    }
  }, [type, search, page]);

  useEffect(() => { fetchContacts(); }, [fetchContacts]);

  const debouncedSearch = (val: string) => {
    if (searchRef.current) clearTimeout(searchRef.current);
    searchRef.current = setTimeout(() => { setSearch(val); setPage(1); }, 300);
  };

  const fmt = (n: number) => "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 0 });

  const columns: ColumnDef<Contact>[] = [
    {
      key: "name",
      header: "Name",
      render: (r) => (
        <div>
          <p className="font-medium text-text-base">{r.name}</p>
          {r.phone && <p className="text-xs text-text-muted">{r.phone}</p>}
        </div>
      ),
    },
    {
      key: "client_type",
      header: "Type",
      width: 110,
      render: (r) => (
        <Badge
          status={r.client_type === "customer" ? "paid" : "sent"}
          label={r.client_type === "customer" ? "CUSTOMER" : "VENDOR"}
        />
      ),
    },
    {
      key: "gstin",
      header: "GSTIN",
      width: 180,
      render: (r) => <span className="font-mono text-xs">{r.gstin || "—"}</span>,
    },
    {
      key: "outstanding",
      header: "Outstanding",
      align: "right" as const,
      width: 140,
      render: (r) => {
        const color =
          r.outstanding === 0
            ? "text-success"
            : r.overdue_count > 0
            ? "text-danger"
            : "text-warning";
        return <span className={`font-mono font-semibold ${color}`}>{fmt(r.outstanding)}</span>;
      },
    },
    {
      key: "total_transactions",
      header: "Transactions",
      align: "right" as const,
      width: 120,
    },
  ];

  return (
    <div className="animate-fade-in">
      <PageHeader title="Contacts" />

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3 mb-5">
        {/* Type Toggle Pills */}
        <div className="flex rounded-lg border border-border overflow-hidden">
          {TYPE_OPTIONS.map(opt => (
            <button
              key={opt.key}
              onClick={() => { setType(opt.key); setPage(1); }}
              className={`px-4 py-1.5 text-sm font-medium transition-colors
                ${type === opt.key
                  ? "bg-accent text-white"
                  : "bg-bg-surface text-text-secondary hover:bg-bg-overlay"
                }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <div className="flex-1 min-w-[200px] max-w-[360px]">
          <Input
            placeholder="Search name, GSTIN, phone..."
            onChange={(e) => debouncedSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={contacts}
        loading={loading}
        onRowClick={(row) => navigate(`/contacts/${row.id}`)}
        rowKey={(r) => r.id}
        emptyState={
          <div className="flex flex-col items-center py-12 text-text-muted">
            <svg className="w-12 h-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" /></svg>
            <p className="text-sm">No contacts found.</p>
          </div>
        }
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 mt-5">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 text-sm rounded-lg border border-border bg-bg-surface text-text-secondary hover:bg-bg-overlay disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-sm text-text-muted">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1.5 text-sm rounded-lg border border-border bg-bg-surface text-text-secondary hover:bg-bg-overlay disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

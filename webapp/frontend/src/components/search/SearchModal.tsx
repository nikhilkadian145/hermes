import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";

const API = "http://localhost:8000/api/search";

interface SearchResult {
  id: number;
  number?: string;
  name?: string;
  client_name?: string;
  amount?: number;
  status?: string;
  type?: string;
  gstin?: string;
  filename?: string;
  linked_to?: string;
  created_at?: string;
  source?: string;
}

interface SearchResults {
  invoices: SearchResult[];
  contacts: SearchResult[];
  documents: SearchResult[];
  reports: SearchResult[];
}

interface SearchModalProps {
  open: boolean;
  onClose: () => void;
}

const RECENT_KEY = "hermes_recent_searches";

const GROUPS: { key: keyof SearchResults; label: string; icon: string; getPath: (r: SearchResult) => string; getText: (r: SearchResult) => [string, string] }[] = [
  {
    key: "invoices", label: "INVOICES", icon: "📄",
    getPath: (r) => r.source === "purchases" ? `/invoices/purchases` : `/invoices/sales/${r.id}`,
    getText: (r) => [
      r.number || `#${r.id}`,
      `${r.client_name || ""}${r.amount ? ` · ₹${r.amount.toLocaleString("en-IN")}` : ""}${r.status ? ` · ${r.status}` : ""}`
    ],
  },
  {
    key: "contacts", label: "CONTACTS", icon: "👤",
    getPath: (r) => `/contacts/${r.id}`,
    getText: (r) => [r.name || `#${r.id}`, `${r.type || ""}${r.gstin ? ` · ${r.gstin}` : ""}`],
  },
  {
    key: "documents", label: "DOCUMENTS", icon: "📁",
    getPath: () => `/documents`,
    getText: (r) => [r.filename || `Document #${r.id}`, `${r.type || ""}${r.linked_to ? ` · ${r.linked_to}` : ""}`],
  },
  {
    key: "reports", label: "REPORTS", icon: "📊",
    getPath: () => `/reports`,
    getText: (r) => [r.name || `Report #${r.id}`, r.type || ""],
  },
];

export function SearchModal({ open, onClose }: SearchModalProps) {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Build flat list for keyboard nav
  const flatItems = results ? GROUPS.flatMap(g =>
    (results[g.key] || []).map(r => ({ group: g, result: r }))
  ) : [];

  const getRecent = (): string[] => {
    try { return JSON.parse(localStorage.getItem(RECENT_KEY) || "[]"); }
    catch { return []; }
  };

  const addRecent = (term: string) => {
    const recent = getRecent().filter(r => r !== term);
    recent.unshift(term);
    localStorage.setItem(RECENT_KEY, JSON.stringify(recent.slice(0, 5)));
  };

  const search = useCallback(async (q: string) => {
    if (!q.trim()) { setResults(null); return; }
    setLoading(true);
    try {
      const res = await apiFetch(`?q=${encodeURIComponent(q.trim())}`);
      if (res.ok) setResults(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  // Focus on open
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery("");
      setResults(null);
      setSelectedIndex(0);
    }
  }, [open]);

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => search(query), 200);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query, search]);

  // Reset selection on new results
  useEffect(() => { setSelectedIndex(0); }, [results]);

  const navigateTo = (path: string, term?: string) => {
    if (term) addRecent(term);
    navigate(path);
    onClose();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") { onClose(); return; }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex(i => Math.min(flatItems.length - 1, i + 1));
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex(i => Math.max(0, i - 1));
    }
    if (e.key === "Enter" && flatItems[selectedIndex]) {
      e.preventDefault();
      const item = flatItems[selectedIndex];
      navigateTo(item.group.getPath(item.result), query);
    }
  };

  // Global Cmd+K / Ctrl+K listener is handled in TopBar

  if (!open) return null;

  const recentSearches = getRecent();
  const hasResults = results && GROUPS.some(g => (results[g.key] || []).length > 0);
  const noResults = results && !hasResults && query.trim().length > 0;

  let flatIndex = 0;

  return (
    <div className="fixed inset-0 z-[400] flex items-start justify-center pt-[15vh] sm:pt-[20vh]" onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" />

      {/* Modal */}
      <div
        className="relative w-full max-w-[600px] mx-4 bg-bg-surface border border-border rounded-2xl shadow-2xl overflow-hidden animate-fade-in"
        onClick={e => e.stopPropagation()}
      >
        {/* Input */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-border">
          <svg className="w-5 h-5 text-text-muted shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search invoices, contacts, documents…"
            className="flex-1 bg-transparent text-lg text-text-base placeholder-text-muted outline-none"
          />
          <kbd className="hidden sm:inline-flex items-center px-1.5 py-0.5 text-[10px] font-mono text-text-muted bg-bg-subtle border border-border rounded">
            ESC
          </kbd>
        </div>

        {/* Results area */}
        <div className="max-h-[400px] overflow-y-auto">
          {loading && (
            <div className="px-5 py-6 text-center text-sm text-text-muted animate-pulse">Searching...</div>
          )}

          {!loading && !query.trim() && recentSearches.length > 0 && (
            <div className="p-3">
              <div className="px-3 py-1.5 text-[11px] font-semibold text-text-muted uppercase tracking-wider">Recent Searches</div>
              {recentSearches.map((term, i) => (
                <button
                  key={i}
                  onClick={() => { setQuery(term); search(term); }}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left hover:bg-bg-overlay transition-colors"
                >
                  <svg className="w-4 h-4 text-text-muted shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  <span className="text-sm text-text-secondary">{term}</span>
                </button>
              ))}
            </div>
          )}

          {!loading && !query.trim() && recentSearches.length === 0 && (
            <div className="px-5 py-8 text-center text-sm text-text-muted">
              Start typing to search across invoices, contacts, and documents.
            </div>
          )}

          {!loading && noResults && (
            <div className="px-5 py-8 text-center">
              <p className="text-sm text-text-muted">No results for &ldquo;<strong className="text-text-base">{query}</strong>&rdquo;</p>
            </div>
          )}

          {!loading && hasResults && (
            <div className="p-2">
              {GROUPS.map(group => {
                const items = results![group.key] || [];
                if (items.length === 0) return null;
                return (
                  <div key={group.key} className="mb-1">
                    <div className="px-3 py-1.5 text-[11px] font-semibold text-text-muted uppercase tracking-wider">
                      {group.label}
                    </div>
                    {items.map(r => {
                      const idx = flatIndex++;
                      const [primary, secondary] = group.getText(r);
                      return (
                        <button
                          key={`${group.key}-${r.id}`}
                          onClick={() => navigateTo(group.getPath(r), query)}
                          onMouseEnter={() => setSelectedIndex(idx)}
                          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                            idx === selectedIndex ? "bg-accent/10 text-accent" : "hover:bg-bg-overlay"
                          }`}
                        >
                          <span className="text-base shrink-0">{group.icon}</span>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium truncate ${idx === selectedIndex ? "text-accent" : "text-text-base"}`}>
                              {primary}
                            </p>
                            {secondary && (
                              <p className="text-xs text-text-muted truncate">{secondary}</p>
                            )}
                          </div>
                          {idx === selectedIndex && (
                            <kbd className="hidden sm:inline-flex text-[10px] font-mono text-text-muted px-1 bg-bg-subtle border border-border rounded">↵</kbd>
                          )}
                        </button>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-2.5 border-t border-border bg-bg-subtle flex items-center justify-between text-[11px] text-text-muted">
          <div className="flex items-center gap-3">
            <span><kbd className="px-1 bg-bg-base border border-border rounded font-mono">↑↓</kbd> Navigate</span>
            <span><kbd className="px-1 bg-bg-base border border-border rounded font-mono">↵</kbd> Open</span>
            <span><kbd className="px-1 bg-bg-base border border-border rounded font-mono">Esc</kbd> Close</span>
          </div>
        </div>
      </div>
    </div>
  );
}

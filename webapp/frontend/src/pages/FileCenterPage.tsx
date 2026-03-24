import { useState, useEffect, useCallback, useRef } from "react";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { PageHeader } from "../components/layout/PageHeader";
import { DocumentViewerDrawer } from "../components/DocumentViewerDrawer";

interface FileItem {
  id: string;
  filename: string;
  display_name: string;
  type: string;
  sub_type: string;
  linked_to: string;
  linked_id: number;
  created_at: string;
  file_size: number;
  file_size_display: string;
  path: string;
  extension: string;
}

const FILTER_TREE = [
  { key: null, label: "All Documents", depth: 0 },
  { key: "uploaded", label: "Uploaded Documents", depth: 0 },
  { key: "uploaded:Vendor Invoices", label: "Vendor Invoices", depth: 1 },
  { key: "uploaded:Others", label: "Others", depth: 1 },
  { key: "generated", label: "Generated Documents", depth: 0 },
  { key: "generated:Sales Invoices", label: "Sales Invoices (PDF)", depth: 1 },
  { key: "generated:Quotations", label: "Quotations", depth: 1 },
  { key: "reports", label: "Reports", depth: 0 },
  { key: "exports", label: "Exports", depth: 0 },
];

function getFileIcon(ext: string) {
  switch (ext) {
    case "pdf":
      return (
        <svg className="w-5 h-5 text-danger" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" />
          <path d="M14 2v6h6" />
          <text x="7" y="17" fontSize="6" fill="currentColor" stroke="none" fontWeight="bold">PDF</text>
        </svg>
      );
    case "jpg": case "jpeg": case "png": case "webp": case "gif":
      return (
        <svg className="w-5 h-5 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <path d="M21 15l-5-5L5 21" />
        </svg>
      );
    default:
      return (
        <svg className="w-5 h-5 text-text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" />
          <path d="M14 2v6h6" />
        </svg>
      );
  }
}

export function FileCenterPage() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [previewFile, setPreviewFile] = useState<FileItem | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const searchTimeout = useRef<ReturnType<typeof setTimeout>>();

  const fetchFiles = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (activeFilter) {
        const mainType = activeFilter.split(":")[0];
        params.set("type", mainType);
      }
      if (search) params.set("search", search);
      params.set("page", String(page));

      const res = await apiFetch(`/files?${params}`);
      if (res.ok) {
        const data = await res.json();
        let filtered = data.files || [];
        // Client-side sub_type filter
        if (activeFilter && activeFilter.includes(":")) {
          const subType = activeFilter.split(":")[1];
          filtered = filtered.filter((f: FileItem) => f.sub_type === subType);
        }
        setFiles(filtered);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      console.error("Failed to fetch files", err);
    } finally {
      setLoading(false);
    }
  }, [activeFilter, search, page]);

  useEffect(() => { fetchFiles(); }, [fetchFiles]);

  const debouncedSearch = (val: string) => {
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    searchTimeout.current = setTimeout(() => {
      setSearch(val);
      setPage(1);
    }, 300);
  };

  const toggleSelect = (id: string) => {
    setSelectedFiles(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleBulkDownload = async () => {
    const res = await apiFetch("/files/bulk-download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Array.from(selectedFiles)),
    });
    if (res.ok) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "hermes_documents.zip";
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const navigatePreview = (direction: 1 | -1) => {
    if (!previewFile) return;
    const idx = files.findIndex(f => f.id === previewFile.id);
    const next = idx + direction;
    if (next >= 0 && next < files.length) setPreviewFile(files[next]);
  };

  const formatDate = (d: string) => {
    if (!d) return "—";
    try { return new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }); }
    catch { return d; }
  };

  return (
    <div className="animate-[fade-in_300ms_ease] flex flex-col h-full">
      <PageHeader title="Documents" />

      <div className="flex flex-1 overflow-hidden gap-0">
        {/* Left Sidebar Filter Tree (desktop only) */}
        <aside className="hidden lg:flex flex-col w-[220px] border-r border-border bg-bg-surface p-3 gap-0.5 overflow-y-auto shrink-0">
          {FILTER_TREE.map(node => {
            const isActive = activeFilter === node.key;
            return (
              <button
                key={node.key ?? "all"}
                onClick={() => { setActiveFilter(node.key); setPage(1); }}
                className={`text-left w-full px-3 py-1.5 rounded-lg text-[13px] transition-colors duration-100
                  ${node.depth === 1 ? "pl-8" : "font-medium"}
                  ${isActive
                    ? "bg-accent-subtle text-accent"
                    : "text-text-secondary hover:bg-bg-overlay hover:text-text-base"
                  }`}
              >
                {node.depth === 1 && <span className="mr-1.5 text-text-muted opacity-50">└</span>}
                {node.label}
              </button>
            );
          })}
        </aside>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Controls Bar */}
          <div className="flex flex-wrap gap-3 items-center justify-between px-5 py-3 border-b border-border bg-bg-surface">
            {/* Mobile filter chips */}
            <div className="flex lg:hidden gap-2 overflow-x-auto w-full pb-2 scrollbar-hide">
              {FILTER_TREE.filter(n => n.depth === 0).map(node => (
                <button
                  key={node.key ?? "all"}
                  onClick={() => { setActiveFilter(node.key); setPage(1); }}
                  className={`shrink-0 px-3 py-1 rounded-full text-xs font-medium border transition-colors
                    ${activeFilter === node.key
                      ? "bg-accent text-white border-accent"
                      : "bg-bg-surface text-text-secondary border-border hover:border-accent/40"
                    }`}
                >
                  {node.label}
                </button>
              ))}
            </div>

            <div className="flex-1 min-w-[200px] max-w-[360px]">
              <Input
                placeholder="Search files..."
                onChange={(e) => debouncedSearch(e.target.value)}
              />
            </div>

            <div className="flex items-center gap-2">
              {/* View toggle */}
              <div className="flex rounded-lg border border-border overflow-hidden">
                <button
                  title="List view"
                  onClick={() => setViewMode("list")}
                  className={`p-2 transition-colors ${viewMode === "list" ? "bg-accent text-white" : "bg-bg-surface text-text-muted hover:text-text-base"}`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" /></svg>
                </button>
                <button
                  title="Grid view"
                  onClick={() => setViewMode("grid")}
                  className={`p-2 transition-colors ${viewMode === "grid" ? "bg-accent text-white" : "bg-bg-surface text-text-muted hover:text-text-base"}`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /></svg>
                </button>
              </div>

              {selectedFiles.size > 0 && (
                <Button variant="primary" size="sm" onClick={handleBulkDownload}>
                  Download ({selectedFiles.size})
                </Button>
              )}
            </div>
          </div>

          {/* File Content Area */}
          <div className="flex-1 overflow-y-auto p-5">
            {loading && (
              <div className="flex items-center justify-center h-40 text-text-muted text-sm animate-pulse">
                Loading documents...
              </div>
            )}

            {!loading && files.length === 0 && (
              <div className="flex flex-col items-center justify-center h-40 text-text-muted">
                <svg className="w-12 h-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1"><path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                <p className="text-sm">No documents found.</p>
              </div>
            )}

            {/* LIST VIEW */}
            {!loading && files.length > 0 && viewMode === "list" && (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-bg-subtle">
                      <th className="w-10 px-3 py-2 text-left">
                        <input
                          type="checkbox"
                          className="accent-accent"
                          checked={selectedFiles.size === files.length && files.length > 0}
                          onChange={() => {
                            if (selectedFiles.size === files.length) setSelectedFiles(new Set());
                            else setSelectedFiles(new Set(files.map(f => f.id)));
                          }}
                        />
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary">Filename</th>
                      <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary hidden md:table-cell">Linked To</th>
                      <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-secondary hidden sm:table-cell">Date</th>
                      <th className="px-3 py-2 text-right text-xs font-medium uppercase tracking-wider text-text-secondary hidden sm:table-cell">Size</th>
                      <th className="px-3 py-2 text-center text-xs font-medium uppercase tracking-wider text-text-secondary w-28">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {files.map((file, i) => (
                      <tr
                        key={file.id}
                        className={`border-b border-border h-12 transition-colors ${selectedFiles.has(file.id) ? "bg-accent-subtle" : i % 2 === 0 ? "bg-bg-surface" : "bg-bg-subtle"} hover:bg-bg-overlay`}
                      >
                        <td className="px-3">
                          <input type="checkbox" className="accent-accent" checked={selectedFiles.has(file.id)} onChange={() => toggleSelect(file.id)} />
                        </td>
                        <td className="px-3 py-2">
                          <div className="flex items-center gap-2.5 min-w-0">
                            {getFileIcon(file.extension)}
                            <div className="min-w-0">
                              <p className="text-sm font-medium text-text-base truncate">{file.display_name}</p>
                              <p className="text-xs text-text-muted truncate">{file.filename}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-3 py-2 text-sm text-text-secondary hidden md:table-cell">{file.linked_to}</td>
                        <td className="px-3 py-2 text-sm text-text-secondary hidden sm:table-cell whitespace-nowrap">{formatDate(file.created_at)}</td>
                        <td className="px-3 py-2 text-sm text-text-secondary text-right font-mono hidden sm:table-cell">{file.file_size_display}</td>
                        <td className="px-3 py-2 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <button
                              title="Preview"
                              onClick={() => setPreviewFile(file)}
                              className="p-1.5 rounded-md hover:bg-bg-overlay text-text-muted hover:text-accent transition-colors"
                            >
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                            </button>
                            <a
                              href={`http://localhost:8000/api/files/download/${file.id}`}
                              title="Download"
                              className="p-1.5 rounded-md hover:bg-bg-overlay text-text-muted hover:text-success transition-colors"
                            >
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                            </a>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* GRID VIEW */}
            {!loading && files.length > 0 && viewMode === "grid" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {files.map(file => (
                  <div
                    key={file.id}
                    className={`group relative rounded-xl border transition-all duration-150 cursor-pointer
                      ${selectedFiles.has(file.id) ? "border-accent bg-accent-subtle shadow-md" : "border-border bg-bg-surface hover:border-accent/40 hover:shadow-sm"}`}
                  >
                    {/* Select checkbox */}
                    <div className="absolute top-3 left-3 z-10">
                      <input type="checkbox" className="accent-accent" checked={selectedFiles.has(file.id)} onChange={() => toggleSelect(file.id)} />
                    </div>

                    {/* Card body */}
                    <div className="p-4 pt-10 flex flex-col items-center text-center" onClick={() => setPreviewFile(file)}>
                      <div className="w-12 h-12 flex items-center justify-center rounded-xl bg-bg-subtle mb-3">
                        {getFileIcon(file.extension)}
                      </div>
                      <p className="text-sm font-medium text-text-base line-clamp-2 leading-snug">{file.display_name}</p>
                      <p className="text-xs text-text-muted mt-1">{formatDate(file.created_at)} · {file.file_size_display}</p>
                    </div>

                    {/* Download overlay */}
                    <a
                      href={`http://localhost:8000/api/files/download/${file.id}`}
                      className="absolute top-3 right-3 p-1.5 rounded-lg bg-bg-surface/80 backdrop-blur opacity-0 group-hover:opacity-100 transition-opacity text-text-muted hover:text-success"
                      title="Download"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                    </a>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <Button variant="secondary" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
                <span className="text-sm text-text-muted">Page {page} of {totalPages}</span>
                <Button variant="secondary" size="sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Document Viewer Drawer */}
      {previewFile && (
        <DocumentViewerDrawer
          file={previewFile}
          onClose={() => setPreviewFile(null)}
          onNext={() => navigatePreview(1)}
          onPrev={() => navigatePreview(-1)}
        />
      )}
    </div>
  );
}

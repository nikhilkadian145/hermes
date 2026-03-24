import { useEffect, useRef } from "react";
import { Button } from "./ui/Button";

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

interface DocumentViewerDrawerProps {
  file: FileItem;
  onClose: () => void;
  onNext: () => void;
  onPrev: () => void;
}

export function DocumentViewerDrawer({ file, onClose, onNext, onPrev }: DocumentViewerDrawerProps) {
  const drawerRef = useRef<HTMLDivElement>(null);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowRight") onNext();
      if (e.key === "ArrowLeft") onPrev();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose, onNext, onPrev]);

  const previewUrl = `http://localhost:8000/api/files/preview/${file.id}`;
  const downloadUrl = `http://localhost:8000/api/files/download/${file.id}`;
  const isImage = ["jpg", "jpeg", "png", "webp", "gif", "tiff"].includes(file.extension);
  const isPdf = file.extension === "pdf";

  const formatDate = (d: string) => {
    if (!d) return "—";
    try { return new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }); }
    catch { return d; }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 z-40 animate-[fade-in_200ms_ease]"
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        ref={drawerRef}
        className="fixed right-0 top-0 h-full w-full sm:w-[520px] bg-bg-base border-l border-border shadow-2xl z-50 flex flex-col animate-[slide-in-right_250ms_ease]"
        style={{ animationFillMode: "forwards" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-bg-surface shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            {/* Nav arrows */}
            <div className="flex gap-1">
              <button
                onClick={onPrev}
                title="Previous file"
                className="p-1.5 rounded-md hover:bg-bg-overlay text-text-muted hover:text-text-base transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
              </button>
              <button
                onClick={onNext}
                title="Next file"
                className="p-1.5 rounded-md hover:bg-bg-overlay text-text-muted hover:text-text-base transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-text-base truncate">{file.display_name}</p>
              <p className="text-xs text-text-muted truncate">{file.filename}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <a href={downloadUrl} download>
              <Button variant="primary" size="sm">Download</Button>
            </a>
            <button
              onClick={onClose}
              title="Close preview"
              className="p-2 rounded-lg hover:bg-bg-overlay text-text-muted hover:text-text-base transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        </div>

        {/* Content: Document Preview */}
        <div className="flex-1 overflow-auto bg-[#e5e7eb] flex items-center justify-center p-4">
          {isPdf ? (
            <object
              data={previewUrl}
              type="application/pdf"
              className="w-full h-full rounded-lg"
            >
              <div className="text-center text-text-muted">
                <p className="mb-2">PDF preview not available.</p>
                <a href={downloadUrl} className="text-accent underline">Download instead</a>
              </div>
            </object>
          ) : isImage ? (
            <img
              src={previewUrl}
              alt={file.display_name}
              className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
            />
          ) : (
            <div className="text-center text-text-muted flex flex-col items-center gap-3">
              <svg className="w-16 h-16 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" /><path d="M14 2v6h6" /></svg>
              <p>Preview not available for this file type.</p>
              <a href={downloadUrl} className="text-accent underline">Download to view</a>
            </div>
          )}
        </div>

        {/* Footer: Metadata */}
        <div className="border-t border-border bg-bg-surface px-5 py-3 shrink-0">
          <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-sm">
            <div>
              <span className="text-text-muted text-xs uppercase tracking-wider">Linked To</span>
              <p className="text-text-base font-medium">{file.linked_to} #{file.linked_id}</p>
            </div>
            <div>
              <span className="text-text-muted text-xs uppercase tracking-wider">Type</span>
              <p className="text-text-base font-medium capitalize">{file.sub_type || file.type}</p>
            </div>
            <div>
              <span className="text-text-muted text-xs uppercase tracking-wider">Upload Date</span>
              <p className="text-text-base">{formatDate(file.created_at)}</p>
            </div>
            <div>
              <span className="text-text-muted text-xs uppercase tracking-wider">File Size</span>
              <p className="text-text-base font-mono">{file.file_size_display}</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { format } from "date-fns";
import { clsx } from "clsx";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";

interface QueueItem {
  id: number;
  filename: string;
  file_size: number;
  status: string;
  error_message: string | null;
  created_at: string;
  linked_bill_id: number | null;
}

export function UploadPage() {
  const navigate = useNavigate();
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchQueue = async () => {
    try {
      const res = await apiFetch("/upload/queue");
      if (res.ok) {
        const data = await res.json();
        setQueue(data.items || []);
      }
    } catch (err) {
      console.error("Failed to fetch queue", err);
    }
  };

  useEffect(() => {
    fetchQueue();
    // Poll the queue every 3 seconds to update statuses
    const interval = setInterval(fetchQueue, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async (files: FileList | File[]) => {
    if (files.length === 0) return;
    setUploading(true);
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    try {
      const res = await apiFetch("/upload/bills", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        await fetchQueue(); // Refresh immediately
      }
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setUploading(false);
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files);
    }
  };

  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleUpload(e.target.files);
    }
    // reset input so the same file can be uploaded again if needed
    if (fileInputRef.current) fileInputRef.current.value = "";
  };
  
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
      case 'review':
        return <Badge status="review" label="NEEDS REVIEW" />;
      case 'error':
        return <Badge status="error" />;
      case 'finalized':
        return <Badge status="finalized" />;
      default:
        return <Badge status="custom" label={status.toUpperCase()} />;
    }
  };

  const formatBytes = (bytes: number, decimals = 2) => {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  return (
    <div className="flex flex-col h-full bg-bg-base p-8 gap-8 overflow-y-auto max-w-5xl mx-auto w-full">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <button 
            onClick={() => navigate("/invoices/purchases")}
            className="text-text-muted hover:text-text-base text-sm mb-2 flex items-center transition-colors"
          >
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
            Back to Purchase Bills
          </button>
          <h1 className="text-3xl font-semibold tracking-tight">Upload Bills</h1>
          <p className="text-text-muted text-base mt-2">Upload invoices and receipts for automated AI extraction.</p>
        </div>
      </div>

      {/* Drag & Drop Zone */}
      <div 
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={clsx(
          "relative border-2 border-dashed rounded-2xl p-16 flex flex-col items-center justify-center text-center transition-all cursor-pointer overflow-hidden",
          isDragging 
            ? "border-accent bg-accent/5 scale-[1.02]" 
            : "border-border bg-bg-surface hover:border-text-muted hover:bg-bg-subtle",
          uploading && "opacity-50 pointer-events-none"
        )}
      >
        <input 
          type="file" 
          multiple 
          className="hidden" 
          ref={fileInputRef} 
          onChange={onFileInputChange}
          accept=".pdf,.png,.jpg,.jpeg,.tiff"
        />
        
        <div className="bg-bg-base p-4 rounded-full shadow-sm border border-border mb-6">
          <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        </div>
        
        <h3 className="text-xl font-medium text-text-base mb-2">
          {isDragging ? "Drop files here" : "Click or drag files to upload"}
        </h3>
        <p className="text-text-muted max-w-md">
          Supported formats: PDF, PNG, JPG, TIFF. Maximum file size: 10MB per file. 
          Multiple files can be selected.
        </p>
        
        {uploading && (
          <div className="absolute inset-0 flex items-center justify-center bg-bg-surface/50 backdrop-blur-sm">
            <div className="flex flex-col items-center">
              <svg className="animate-spin w-8 h-8 text-accent mb-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="font-medium text-text-base">Uploading...</span>
            </div>
          </div>
        )}
      </div>

      {/* Queue Table */}
      {queue.length > 0 && (
        <div className="bg-bg-surface rounded-xl border border-border overflow-hidden shadow-sm animate-fade-in">
          <div className="px-6 py-4 border-b border-border bg-bg-subtle flex justify-between items-center">
            <h3 className="font-medium text-text-base">Processing Queue</h3>
            <span className="text-xs font-mono text-text-muted">{queue.length} active items</span>
          </div>
          
          <div className="divide-y divide-border">
            {queue.map((item) => (
              <div key={item.id} className="p-4 px-6 flex items-center justify-between hover:bg-bg-subtle transition-colors">
                <div className="flex items-center gap-4 flex-1">
                  <div className="bg-bg-base p-2 rounded-lg border border-border flex-shrink-0">
                    {item.filename.toLowerCase().endsWith('.pdf') ? (
                      <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-1.162 17.5h-1.676v-8h1.676v8zm.838-9.5h-3.352v-1.5h3.352v1.5zm4.824 9.5h-1.676v-8h1.676v8zm.838-9.5h-3.352v-1.5h3.352v1.5z"/></svg>
                    ) : (
                      <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.103 0-2 .897-2 2v14c0 1.103.897 2 2 2h14c1.103 0 2-.897 2-2V5c0-1.103-.897-2-2-2zm0 16H5V5h14v14zm-5-7l-3 4-2-3-3 4h12l-4-5z"/></svg>
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-text-base truncate">{item.filename.split('/').pop()?.split('_').slice(1).join('_') || item.filename}</p>
                    <div className="text-xs text-text-muted mt-1 flex items-center gap-3">
                      <span>Added {format(new Date(item.created_at), "h:mm a")}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4 ml-4">
                  {getStatusBadge(item.status)}
                  
                  {item.status === 'review' && (
                    <Button 
                      onClick={() => navigate(`/invoices/purchases/review/${item.id}`)}
                      size="sm" 
                      variant="primary"
                    >
                      Review
                    </Button>
                  )}
                  
                  {item.status === 'error' && (
                    <div className="flex flex-col items-end gap-2">
                       <span className="text-xs text-danger max-w-[200px] truncate" title={item.error_message || "Unknown error"}>
                         {item.error_message || "Unknown error"}
                       </span>
                       <Button 
                         onClick={async () => {
                           await apiFetch(`/upload/queue/${item.id}/requeue`, { method: "POST" });
                           fetchQueue();
                         }}
                         size="sm" 
                         variant="secondary"
                       >
                         Retry
                       </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

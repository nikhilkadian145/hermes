import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";

const API = "http://localhost:8000/api";

interface ImportSection {
  key: string;
  title: string;
  description: string;
  icon: string;
  sampleUrl: string;
  importUrl: string;
  confirmUrl?: string;
}

const SECTIONS: ImportSection[] = [
  {
    key: "contacts",
    title: "Import Contacts",
    description: "Upload a CSV with vendor and customer contacts. Required columns: name, type, gstin, email, phone, address.",
    icon: "👤",
    sampleUrl: `${API}/import/contacts/sample.csv`,
    importUrl: `${API}/import/contacts`,
    confirmUrl: `${API}/import/contacts/confirm`,
  },
  {
    key: "opening-balances",
    title: "Import Opening Balances",
    description: "Upload a CSV with account codes and their opening debit/credit balances.",
    icon: "📊",
    sampleUrl: `${API}/import/opening-balances/sample.csv`,
    importUrl: `${API}/import/opening-balances`,
  },
  {
    key: "bank-statement",
    title: "Import Bank Statement",
    description: "Upload a CSV bank statement with date, description, reference, debit, credit, and balance columns.",
    icon: "🏦",
    sampleUrl: `${API}/import/bank-statement/sample.csv`,
    importUrl: `${API}/import/bank-statement`,
  },
];

type StepState = {
  step: number; // 0=idle, 1=uploaded/previewing, 2=importing, 3=done
  file: File | null;
  preview: any[] | null;
  result: any | null;
  loading: boolean;
  error: string;
};

const initialStep: StepState = { step: 0, file: null, preview: null, result: null, loading: false, error: "" };

export function ImportCenterPage() {
  const navigate = useNavigate();
  const [states, setStates] = useState<Record<string, StepState>>(
    Object.fromEntries(SECTIONS.map(s => [s.key, { ...initialStep }]))
  );
  const fileRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const update = (key: string, partial: Partial<StepState>) => {
    setStates(prev => ({ ...prev, [key]: { ...prev[key], ...partial } }));
  };

  const handleUpload = async (section: ImportSection, file: File) => {
    update(section.key, { file, loading: true, error: "" });
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(section.importUrl, { method: "POST", body: formData });
      if (res.ok) {
        const data = await res.json();
        update(section.key, { step: 1, preview: data.preview || [], result: data, loading: false });
      } else {
        update(section.key, { error: "Failed to parse file.", loading: false });
      }
    } catch (e) {
      update(section.key, { error: "Upload failed. Please try again.", loading: false });
    }
  };

  const handleConfirm = async (section: ImportSection) => {
    const state = states[section.key];
    if (!state.file || !section.confirmUrl) return;
    update(section.key, { step: 2, loading: true });
    const formData = new FormData();
    formData.append("file", state.file);
    try {
      const res = await fetch(section.confirmUrl, { method: "POST", body: formData });
      if (res.ok) {
        const data = await res.json();
        update(section.key, { step: 3, result: data, loading: false });
      } else {
        update(section.key, { error: "Import failed.", loading: false });
      }
    } catch (e) {
      update(section.key, { error: "Import failed. Please try again.", loading: false });
    }
  };

  const handleExport = async () => {
    try {
      const res = await apiFetch(`/export/data`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        window.open(`${API}/export/data/${data.job_id}/download`, "_blank");
      }
    } catch (e) { console.error(e); }
  };

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate("/settings")} className="p-2 -ml-2 text-text-muted hover:bg-bg-overlay hover:text-text-base rounded transition-colors" title="Back to Settings">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold font-display text-text-base">Import / Export Center</h1>
          <p className="text-sm text-text-muted mt-0.5">Import data from CSV files or export a full backup.</p>
        </div>
        <Button variant="secondary" onClick={handleExport}>
          Export Full Backup
        </Button>
      </div>

      {/* Import Sections */}
      <div className="space-y-6">
        {SECTIONS.map(section => {
          const state = states[section.key];
          return (
            <div key={section.key} className="bg-bg-surface border border-border rounded-xl overflow-hidden">
              {/* Section Header */}
              <div className="px-5 py-4 border-b border-border flex items-center gap-3">
                <span className="text-2xl">{section.icon}</span>
                <div className="flex-1">
                  <h3 className="font-semibold text-text-base">{section.title}</h3>
                  <p className="text-xs text-text-muted mt-0.5">{section.description}</p>
                </div>
                <a
                  href={section.sampleUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-accent hover:underline font-medium flex items-center gap-1"
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                  Download Template
                </a>
              </div>

              {/* Body */}
              <div className="px-5 py-5">
                {/* Step 0: Upload zone */}
                {state.step === 0 && (
                  <div
                    onClick={() => fileRefs.current[section.key]?.click()}
                    className="border-2 border-dashed border-border rounded-xl p-8 text-center cursor-pointer hover:border-accent/50 hover:bg-bg-subtle/50 transition-colors"
                  >
                    <input
                      ref={el => { fileRefs.current[section.key] = el; }}
                      type="file"
                      accept=".csv"
                      className="hidden"
                      title="Upload CSV file"
                      onChange={e => {
                        const f = e.target.files?.[0];
                        if (f) handleUpload(section, f);
                      }}
                    />
                    {state.loading ? (
                      <p className="text-sm text-text-muted animate-pulse">Parsing file...</p>
                    ) : (
                      <>
                        <svg className="w-10 h-10 mx-auto mb-3 text-text-muted/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                          <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <p className="text-sm font-medium text-text-base">Drop a CSV file here or click to browse</p>
                        <p className="text-xs text-text-muted mt-1">Maximum 5MB • CSV format only</p>
                      </>
                    )}
                    {state.error && <p className="text-xs text-danger mt-2">{state.error}</p>}
                  </div>
                )}

                {/* Step 1: Preview table */}
                {state.step === 1 && state.preview && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-sm text-text-secondary">
                        Preview — <span className="font-semibold text-green-500">{state.result?.valid || 0} valid</span>,{" "}
                        <span className="font-semibold text-danger">{state.result?.error_count || 0} errors</span> out of {state.result?.total || 0} rows
                      </p>
                      <Button variant="ghost" size="sm" onClick={() => update(section.key, { ...initialStep })}>
                        Upload Different File
                      </Button>
                    </div>
                    <div className="overflow-x-auto border border-border rounded-lg max-h-72">
                      <table className="w-full text-xs">
                        <thead className="bg-bg-subtle sticky top-0">
                          <tr>
                            <th className="px-3 py-2 text-left font-semibold text-text-muted w-10">Row</th>
                            <th className="px-3 py-2 text-left font-semibold text-text-muted w-10">✓</th>
                            {state.preview[0] && Object.keys(state.preview[0]).filter(k => !["row", "errors", "valid"].includes(k)).map(k => (
                              <th key={k} className="px-3 py-2 text-left font-semibold text-text-muted uppercase">{k}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                          {state.preview.map((row: any, i: number) => (
                            <tr key={i} className={`${row.valid ? "" : "bg-danger/5"}`}>
                              <td className="px-3 py-2 font-mono text-text-muted">{row.row}</td>
                              <td className="px-3 py-2">{row.valid ? <span className="text-green-500">✓</span> : <span className="text-danger" title={(row.errors || []).join(", ")}>✗</span>}</td>
                              {Object.keys(row).filter(k => !["row", "errors", "valid"].includes(k)).map(k => (
                                <td key={k} className="px-3 py-2 text-text-base">{row[k] || "—"}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {section.confirmUrl && (
                      <div className="flex justify-end mt-4">
                        <Button variant="primary" onClick={() => handleConfirm(section)} disabled={state.loading}>
                          {state.loading ? "Importing..." : `Import ${state.result?.valid || 0} valid rows, skip ${state.result?.error_count || 0} errors`}
                        </Button>
                      </div>
                    )}
                  </div>
                )}

                {/* Step 2: Importing */}
                {state.step === 2 && (
                  <div className="py-8 text-center text-text-muted animate-pulse">
                    <p className="text-sm font-medium">Importing data...</p>
                  </div>
                )}

                {/* Step 3: Done */}
                {state.step === 3 && state.result && (
                  <div className="py-6 text-center">
                    <div className="w-12 h-12 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-3">
                      <span className="text-green-500 text-xl">✓</span>
                    </div>
                    <p className="text-sm font-semibold text-text-base">Import Complete</p>
                    <p className="text-xs text-text-muted mt-1">
                      {state.result.imported} rows imported{state.result.error_count > 0 ? `, ${state.result.error_count} skipped with errors` : ""}.
                    </p>
                    <Button variant="ghost" size="sm" className="mt-4" onClick={() => update(section.key, { ...initialStep })}>
                      Import More
                    </Button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

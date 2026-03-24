import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

const API = "http://localhost:8000/api/settings";

const TABS = [
  { key: "profile", label: "Business Profile", icon: "🏢" },
  { key: "financial", label: "Financial Config", icon: "📊" },
  { key: "appearance", label: "Invoice Appearance", icon: "🎨" },
  { key: "notifications", label: "Notifications", icon: "🔔" },
  { key: "ai", label: "AI Configuration", icon: "🤖" },
  { key: "data", label: "Data Management", icon: "💾" },
];

const PROVIDERS = [
  { value: "openrouter", label: "OpenRouter" },
  { value: "anthropic", label: "Anthropic" },
  { value: "openai", label: "OpenAI" },
  { value: "gemini", label: "Google Gemini" },
  { value: "deepseek", label: "DeepSeek" },
  { value: "groq", label: "Groq" },
  { value: "ollama", label: "Ollama (local)" },
];

const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const PAYMENT_TERMS = ["Net 15", "Net 30", "Net 45", "Net 60", "Custom"];
const GST_RATES = [0, 5, 12, 18, 28];

const NOTIFICATION_TYPES = [
  { key: "payment_received", label: "Payment Received" },
  { key: "invoice_overdue", label: "Invoice Overdue" },
  { key: "bill_processed", label: "Bill Processed" },
  { key: "anomaly_detected", label: "Anomaly Detected" },
  { key: "report_ready", label: "Report Ready" },
  { key: "backup_complete", label: "Backup Complete" },
];

export function SettingsPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState("profile");
  const [settings, setSettings] = useState<any>({});
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  // Profile state
  const [profile, setProfile] = useState<any>({});
  // Financial state
  const [financial, setFinancial] = useState<any>({});
  // Appearance state
  const [appearance, setAppearance] = useState<any>({});
  // Notification prefs
  const [notifPrefs, setNotifPrefs] = useState<any>({});
  // Danger zone
  const [clearConfirm, setClearConfirm] = useState("");
  const [showClearModal, setShowClearModal] = useState(false);
  // AI config state
  const [aiConfig, setAiConfig] = useState<any>({
    provider_name: "", api_key: "", model: "",
    telegram_token: "", telegram_allow_from: "",
    api_key_display: "", telegram_token_set: false,
  });
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch("");
        if (res.ok) {
          const data = await res.json();
          setSettings(data);
          setProfile({
            business_name: data.business_name || "",
            address: data.address || "",
            city: data.city || "",
            state: data.state || "",
            pin: data.pin || "",
            gstin: data.gstin || "",
            pan: data.pan || "",
            email: data.email || "",
            phone: data.phone || "",
            industry: data.industry || "",
          });
          const fc = data.financial_config || {};
          setFinancial({
            fy_start_month: fc.fy_start_month || "April",
            default_payment_terms: fc.default_payment_terms || "Net 30",
            default_gst_rates: fc.default_gst_rates || "5,12,18,28",
            invoice_prefix: fc.invoice_prefix || "INV",
            invoice_separator: fc.invoice_separator || "-",
            invoice_start_number: fc.invoice_start_number || 1,
          });
          const ia = data.invoice_appearance || {};
          setAppearance({
            template: ia.template || "classic",
            accent_color: ia.accent_color || "#6366f1",
            footer_text: ia.footer_text || "",
            show_hsn: ia.show_hsn ?? true,
            show_unit_price: ia.show_unit_price ?? true,
            show_discount: ia.show_discount ?? false,
          });
          setNotifPrefs(data.notification_prefs || {});
        }
      } catch (e) { console.error(e); }
    })();
    // Load AI config
    (async () => {
      try {
        const res = await fetch(`${API}/config`);
        if (res.ok) {
          const data = await res.json();
          setAiConfig({
            provider_name: data.provider_name || "",
            api_key: "",
            api_key_display: data.api_key_display || "",
            model: data.model || "",
            telegram_token: "",
            telegram_token_set: data.telegram_token_set || false,
            telegram_allow_from: (data.telegram_allow_from || []).join(", "),
          });
        }
      } catch (e) { console.error(e); }
    })();
  }, []);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3000);
  };

  const saveProfile = async () => {
    setSaving(true);
    try {
      await apiFetch(`/profile`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(profile) });
      showToast("Profile saved!");
    } catch { showToast("Save failed"); }
    setSaving(false);
  };

  const saveFinancial = async () => {
    setSaving(true);
    try {
      await apiFetch(`/financial`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(financial) });
      showToast("Financial settings saved!");
    } catch { showToast("Save failed"); }
    setSaving(false);
  };

  const saveAppearance = async () => {
    setSaving(true);
    try {
      await apiFetch(`/invoice-appearance`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(appearance) });
      showToast("Appearance saved!");
    } catch { showToast("Save failed"); }
    setSaving(false);
  };

  const saveNotifications = async () => {
    setSaving(true);
    try {
      await apiFetch(`/notifications`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ prefs: notifPrefs }) });
      showToast("Notification preferences saved!");
    } catch { showToast("Save failed"); }
    setSaving(false);
  };

  const saveAiConfig = async () => {
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {};
      if (aiConfig.provider_name) payload.provider_name = aiConfig.provider_name;
      if (aiConfig.api_key) payload.api_key = aiConfig.api_key;
      if (aiConfig.model) payload.model = aiConfig.model;
      if (aiConfig.telegram_token && aiConfig.telegram_token !== "change") payload.telegram_token = aiConfig.telegram_token;
      if (aiConfig.telegram_allow_from) {
        payload.telegram_allow_from = aiConfig.telegram_allow_from
          .split(",").map((s: string) => {
            const n = Number(s.trim());
            return isNaN(n) ? s.trim() : n;
          }).filter(Boolean);
      }
      await fetch(`${API}/config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      showToast("AI configuration saved! Restart nanobot agent to apply.");
      // Refresh display
      const res = await fetch(`${API}/config`);
      if (res.ok) {
        const data = await res.json();
        setAiConfig((prev: Record<string, unknown>) => ({
          ...prev,
          api_key: "",
          api_key_display: data.api_key_display || "",
          telegram_token: "",
          telegram_token_set: data.telegram_token_set || false,
        }));
        setShowApiKey(false);
      }
    } catch { showToast("Save failed"); }
    setSaving(false);
  };

  const handleExport = async () => {
    try {
      const res = await apiFetch("/export/data", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        window.open(`http://localhost:8000/api/export/data/${data.job_id}/download`, "_blank");
      }
    } catch (e) { console.error(e); }
  };

  const handleClearQueue = async () => {
    if (clearConfirm !== "CLEAR") return;
    try {
      await apiFetch("/system/queue/requeue-all-failed", { method: "POST" });
      showToast("Queue cleared.");
    } catch { showToast("Failed to clear queue."); }
    setShowClearModal(false);
    setClearConfirm("");
  };

  const toggleGstRate = (rate: number) => {
    const current = (financial.default_gst_rates || "").split(",").map((r: string) => r.trim()).filter(Boolean);
    const rateStr = String(rate);
    const next = current.includes(rateStr) ? current.filter((r: string) => r !== rateStr) : [...current, rateStr];
    setFinancial({ ...financial, default_gst_rates: next.join(",") });
  };

  const invoicePreview = `${financial.invoice_prefix || "INV"}${financial.invoice_separator || "-"}${String(financial.invoice_start_number || 1).padStart(4, "0")}`;

  const pf = (key: string) => profile[key] || "";
  const setPf = (key: string, val: string) => setProfile({ ...profile, [key]: val });

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base overflow-y-auto pb-16">
      <div className="mb-6">
        <h1 className="text-xl font-bold font-display text-text-base">Settings</h1>
        <p className="text-sm text-text-muted mt-0.5">Manage your business configuration and preferences.</p>
      </div>

      <div className="flex gap-6 flex-1 min-h-0">
        {/* Left Nav */}
        <nav className="hidden md:flex flex-col w-[200px] shrink-0">
          {TABS.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm text-left transition-colors mb-1 ${
                tab === t.key ? "bg-accent/10 text-accent font-semibold" : "text-text-secondary hover:bg-bg-overlay hover:text-text-base"
              }`}
            >
              <span>{t.icon}</span>
              {t.label}
            </button>
          ))}
        </nav>

        {/* Mobile tabs */}
        <div className="md:hidden flex overflow-x-auto gap-1 mb-4 shrink-0">
          {TABS.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-3 py-2 text-xs font-semibold rounded-lg whitespace-nowrap transition-colors ${
                tab === t.key ? "bg-accent text-white" : "bg-bg-subtle text-text-muted"
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Business Profile */}
          {tab === "profile" && (
            <div className="bg-bg-surface border border-border rounded-xl p-6 max-w-2xl">
              <h2 className="text-lg font-bold text-text-base mb-5">Business Profile</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2"><Input label="Business Name" value={pf("business_name")} onChange={e => setPf("business_name", e.target.value)} /></div>
                <div className="md:col-span-2"><Input label="Address" value={pf("address")} onChange={e => setPf("address", e.target.value)} /></div>
                <Input label="City" value={pf("city")} onChange={e => setPf("city", e.target.value)} />
                <Input label="State" value={pf("state")} onChange={e => setPf("state", e.target.value)} />
                <Input label="PIN Code" value={pf("pin")} onChange={e => setPf("pin", e.target.value)} />
                <Input label="GSTIN" value={pf("gstin")} onChange={e => setPf("gstin", e.target.value)} />
                <Input label="PAN" value={pf("pan")} onChange={e => setPf("pan", e.target.value)} />
                <Input label="Contact Email" value={pf("email")} onChange={e => setPf("email", e.target.value)} />
                <Input label="Phone" value={pf("phone")} onChange={e => setPf("phone", e.target.value)} />
                <Input label="Industry" value={pf("industry")} onChange={e => setPf("industry", e.target.value)} />
              </div>
              <div className="flex justify-end mt-6">
                <Button variant="primary" onClick={saveProfile} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</Button>
              </div>
            </div>
          )}

          {/* Financial Config */}
          {tab === "financial" && (
            <div className="bg-bg-surface border border-border rounded-xl p-6 max-w-2xl">
              <h2 className="text-lg font-bold text-text-base mb-5">Financial Configuration</h2>
              <div className="space-y-5">
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Financial Year Start</label>
                  <select title="Financial year start month" className="h-10 px-3 bg-bg-base border border-border rounded-lg text-sm text-text-base w-full max-w-xs focus:ring-1 focus:ring-accent focus:outline-none" value={financial.fy_start_month} onChange={e => setFinancial({ ...financial, fy_start_month: e.target.value })}>
                    {MONTHS.map(m => <option key={m} value={m}>{m}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Default Payment Terms</label>
                  <select title="Default payment terms" className="h-10 px-3 bg-bg-base border border-border rounded-lg text-sm text-text-base w-full max-w-xs focus:ring-1 focus:ring-accent focus:outline-none" value={financial.default_payment_terms} onChange={e => setFinancial({ ...financial, default_payment_terms: e.target.value })}>
                    {PAYMENT_TERMS.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Default GST Rates</label>
                  <div className="flex flex-wrap gap-2">
                    {GST_RATES.map(rate => {
                      const active = (financial.default_gst_rates || "").split(",").map((r: string) => r.trim()).includes(String(rate));
                      return (
                        <button key={rate} onClick={() => toggleGstRate(rate)} className={`px-3 py-1.5 text-sm font-semibold rounded-full border transition-colors ${active ? "bg-accent text-white border-accent" : "bg-bg-base text-text-muted border-border hover:border-accent/50"}`}>
                          {rate}%
                        </button>
                      );
                    })}
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Invoice Number Format</label>
                  <div className="flex items-center gap-2 max-w-sm">
                    <Input label="" placeholder="INV" value={financial.invoice_prefix || ""} onChange={e => setFinancial({ ...financial, invoice_prefix: e.target.value })} />
                    <Input label="" placeholder="-" value={financial.invoice_separator || ""} onChange={e => setFinancial({ ...financial, invoice_separator: e.target.value })} />
                    <Input label="" type="number" placeholder="1" value={financial.invoice_start_number || ""} onChange={e => setFinancial({ ...financial, invoice_start_number: Number(e.target.value) })} />
                  </div>
                  <p className="text-xs text-text-muted mt-2">Preview: <span className="font-mono font-semibold text-accent">{invoicePreview}</span></p>
                </div>
              </div>
              <div className="flex justify-end mt-6">
                <Button variant="primary" onClick={saveFinancial} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</Button>
              </div>
            </div>
          )}

          {/* Invoice Appearance */}
          {tab === "appearance" && (
            <div className="bg-bg-surface border border-border rounded-xl p-6 max-w-2xl">
              <h2 className="text-lg font-bold text-text-base mb-5">Invoice Appearance</h2>
              <div className="space-y-5">
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-2">Template</label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { key: "classic", name: "Classic", desc: "Clean, traditional layout" },
                      { key: "modern", name: "Modern", desc: "Sleek with accent colors" },
                      { key: "minimal", name: "Minimal", desc: "Whitespace-focused" },
                    ].map(tmpl => (
                      <button
                        key={tmpl.key}
                        onClick={() => setAppearance({ ...appearance, template: tmpl.key })}
                        className={`p-4 rounded-xl border-2 text-left transition-all ${
                          appearance.template === tmpl.key ? "border-accent bg-accent/5" : "border-border hover:border-accent/30"
                        }`}
                      >
                        <div className={`w-full h-16 rounded-lg mb-2 ${tmpl.key === "classic" ? "bg-gradient-to-br from-gray-200 to-gray-300" : tmpl.key === "modern" ? "bg-gradient-to-br from-indigo-400 to-purple-500" : "bg-gradient-to-br from-gray-50 to-gray-100"}`} />
                        <p className="text-sm font-semibold text-text-base">{tmpl.name}</p>
                        <p className="text-xs text-text-muted">{tmpl.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Accent Color</label>
                  <div className="flex items-center gap-3">
                    <input type="color" value={appearance.accent_color || "#6366f1"} onChange={e => setAppearance({ ...appearance, accent_color: e.target.value })} title="Accent color" className="w-10 h-10 rounded-lg border border-border cursor-pointer" />
                    <span className="text-sm text-text-muted font-mono">{appearance.accent_color}</span>
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Footer Text</label>
                  <textarea
                    className="w-full h-20 px-3 py-2 bg-bg-base border border-border rounded-lg text-sm text-text-base resize-none focus:ring-1 focus:ring-accent focus:outline-none"
                    placeholder="Thank you for your business!"
                    value={appearance.footer_text || ""}
                    onChange={e => setAppearance({ ...appearance, footer_text: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-2">Column Visibility</label>
                  <div className="space-y-3">
                    {[
                      { key: "show_hsn", label: "HSN Code" },
                      { key: "show_unit_price", label: "Per-unit Price" },
                      { key: "show_discount", label: "Discount Column" },
                    ].map(col => (
                      <label key={col.key} className="flex items-center gap-3 cursor-pointer">
                        <div
                          onClick={() => setAppearance({ ...appearance, [col.key]: !appearance[col.key] })}
                          className={`w-10 h-6 rounded-full transition-colors relative cursor-pointer ${appearance[col.key] ? "bg-accent" : "bg-bg-subtle border border-border"}`}
                        >
                          <div className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${appearance[col.key] ? "translate-x-4" : "translate-x-0.5"}`} />
                        </div>
                        <span className="text-sm text-text-base">{col.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex justify-end mt-6">
                <Button variant="primary" onClick={saveAppearance} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</Button>
              </div>
            </div>
          )}

          {/* Notifications */}
          {tab === "notifications" && (
            <div className="bg-bg-surface border border-border rounded-xl p-6 max-w-2xl">
              <h2 className="text-lg font-bold text-text-base mb-5">Notification Preferences</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-[1fr_80px_80px] gap-2 items-center text-xs font-semibold text-text-muted uppercase px-1">
                  <span>Type</span><span className="text-center">In-App</span><span className="text-center">Email</span>
                </div>
                {NOTIFICATION_TYPES.map(nt => {
                  const prefs = notifPrefs[nt.key] || { in_app: true, email: false };
                  return (
                    <div key={nt.key} className="grid grid-cols-[1fr_80px_80px] gap-2 items-center px-1 py-2 border-b border-border last:border-0">
                      <span className="text-sm text-text-base">{nt.label}</span>
                      <div className="flex justify-center">
                        <div
                          onClick={() => setNotifPrefs({ ...notifPrefs, [nt.key]: { ...prefs, in_app: !prefs.in_app } })}
                          className={`w-9 h-5 rounded-full transition-colors relative cursor-pointer ${prefs.in_app ? "bg-accent" : "bg-bg-subtle border border-border"}`}
                        >
                          <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${prefs.in_app ? "translate-x-4" : "translate-x-0.5"}`} />
                        </div>
                      </div>
                      <div className="flex justify-center">
                        <div
                          onClick={() => setNotifPrefs({ ...notifPrefs, [nt.key]: { ...prefs, email: !prefs.email } })}
                          className={`w-9 h-5 rounded-full transition-colors relative cursor-pointer ${prefs.email ? "bg-accent" : "bg-bg-subtle border border-border"}`}
                        >
                          <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${prefs.email ? "translate-x-4" : "translate-x-0.5"}`} />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-5">
                <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Email Digest Frequency</label>
                <select title="Email digest frequency" className="h-10 px-3 bg-bg-base border border-border rounded-lg text-sm text-text-base w-full max-w-xs focus:ring-1 focus:ring-accent focus:outline-none" value={notifPrefs.digest_frequency || "daily"} onChange={e => setNotifPrefs({ ...notifPrefs, digest_frequency: e.target.value })}>
                  <option value="realtime">Real-time</option>
                  <option value="daily">Daily Summary</option>
                  <option value="weekly">Weekly Summary</option>
                </select>
              </div>
              <div className="flex justify-end mt-6">
                <Button variant="primary" onClick={saveNotifications} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</Button>
              </div>
            </div>
          )}

          {/* AI Configuration */}
          {tab === "ai" && (
            <div className="bg-bg-surface border border-border rounded-xl p-6 max-w-2xl">
              <h2 className="text-lg font-bold text-text-base mb-1">AI Configuration</h2>
              <p className="text-xs text-text-muted mb-5">Configure your LLM provider, model, and Telegram bot connection. Changes require an agent restart.</p>

              <div className="space-y-5">
                {/* Provider */}
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">LLM Provider</label>
                  <select
                    title="LLM provider"
                    className="h-10 px-3 bg-bg-base border border-border rounded-lg text-sm text-text-base w-full max-w-xs focus:ring-1 focus:ring-accent focus:outline-none"
                    value={aiConfig.provider_name}
                    onChange={e => setAiConfig({ ...aiConfig, provider_name: e.target.value })}
                  >
                    <option value="">Select provider...</option>
                    {PROVIDERS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                  </select>
                </div>

                {/* API Key */}
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">API Key</label>
                  {aiConfig.api_key_display && !showApiKey && (
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm text-text-secondary font-mono bg-bg-base px-3 py-1.5 rounded-lg border border-border">{aiConfig.api_key_display}</span>
                      <button onClick={() => setShowApiKey(true)} className="text-xs text-accent hover:underline">Change</button>
                    </div>
                  )}
                  {(showApiKey || !aiConfig.api_key_display) && (
                    <Input
                      label=""
                      type="password"
                      placeholder="sk-..."
                      value={aiConfig.api_key}
                      onChange={e => setAiConfig({ ...aiConfig, api_key: e.target.value })}
                    />
                  )}
                </div>

                {/* Model */}
                <div>
                  <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Model</label>
                  <Input
                    label=""
                    placeholder="anthropic/claude-sonnet-4-20250514"
                    value={aiConfig.model}
                    onChange={e => setAiConfig({ ...aiConfig, model: e.target.value })}
                  />
                  <p className="text-xs text-text-muted mt-1">Use provider prefix format, e.g. <code className="font-mono text-accent">anthropic/claude-sonnet-4-20250514</code> or <code className="font-mono text-accent">openai/gpt-4o</code></p>
                </div>

                {/* Divider */}
                <hr className="border-border" />

                {/* Telegram */}
                <div>
                  <h3 className="text-sm font-bold text-text-base mb-3">Telegram Bot</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Bot Token</label>
                      {aiConfig.telegram_token_set && !aiConfig.telegram_token && (
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm text-green-400 font-semibold">✓ Token configured</span>
                          <button onClick={() => setAiConfig({ ...aiConfig, telegram_token: "change" })} className="text-xs text-accent hover:underline">Change</button>
                        </div>
                      )}
                      {(!aiConfig.telegram_token_set || aiConfig.telegram_token) && (
                        <Input
                          label=""
                          type="password"
                          placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                          value={aiConfig.telegram_token === "change" ? "" : aiConfig.telegram_token}
                          onChange={e => setAiConfig({ ...aiConfig, telegram_token: e.target.value })}
                        />
                      )}
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-text-muted uppercase block mb-1.5">Allowed User IDs</label>
                      <Input
                        label=""
                        placeholder="123456789, 987654321"
                        value={aiConfig.telegram_allow_from}
                        onChange={e => setAiConfig({ ...aiConfig, telegram_allow_from: e.target.value })}
                      />
                      <p className="text-xs text-text-muted mt-1">Comma-separated Telegram user IDs allowed to message the bot.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mt-6">
                <p className="text-xs text-amber-400">⚡ Restart the nanobot agent after saving for changes to take effect.</p>
                <Button variant="primary" onClick={saveAiConfig} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</Button>
              </div>
            </div>
          )}

          {/* Data Management */}
          {tab === "data" && (
            <div className="space-y-6 max-w-2xl">
              <div className="bg-bg-surface border border-border rounded-xl p-6">
                <h2 className="text-lg font-bold text-text-base mb-4">Data Management</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3 border-b border-border">
                    <div>
                      <p className="text-sm font-medium text-text-base">Export All Data</p>
                      <p className="text-xs text-text-muted">Download a full JSON backup of all records.</p>
                    </div>
                    <Button variant="secondary" size="sm" onClick={handleExport}>Export</Button>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <div>
                      <p className="text-sm font-medium text-text-base">Import Data</p>
                      <p className="text-xs text-text-muted">Import contacts, opening balances, or bank statements from CSV.</p>
                    </div>
                    <Button variant="secondary" size="sm" onClick={() => navigate("/settings/import")}>Import Center</Button>
                  </div>
                </div>
              </div>

              {/* Danger Zone */}
              <div className="bg-bg-surface border border-danger/30 rounded-xl p-6">
                <h3 className="text-sm font-bold text-danger mb-3">⚠ Danger Zone</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-text-base">Clear Processing Queue</p>
                    <p className="text-xs text-text-muted">Requeue all failed items. This action requires confirmation.</p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setShowClearModal(true)} className="!text-danger !border-danger/30 hover:!bg-danger/5">
                    Clear Queue
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-green-500 text-white px-5 py-3 rounded-xl shadow-lg text-sm font-semibold animate-fade-in z-[500]">
          {toast}
        </div>
      )}

      {/* Clear Queue Modal */}
      {showClearModal && (
        <div className="fixed inset-0 z-[300] flex items-center justify-center bg-black/50">
          <div className="bg-bg-surface border border-border rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-fade-in">
            <h3 className="text-lg font-bold text-danger mb-2">Clear Processing Queue</h3>
            <p className="text-sm text-text-secondary mb-4">Type <strong className="font-mono">CLEAR</strong> to confirm.</p>
            <Input label="" placeholder='Type "CLEAR" to confirm' value={clearConfirm} onChange={e => setClearConfirm(e.target.value)} />
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="ghost" size="sm" onClick={() => { setShowClearModal(false); setClearConfirm(""); }}>Cancel</Button>
              <Button variant="primary" size="sm" onClick={handleClearQueue} disabled={clearConfirm !== "CLEAR"} className="!bg-danger">
                Confirm Clear
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

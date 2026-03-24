import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";

const API = "http://localhost:8000/api/onboarding";

const GST_RATES = [0, 5, 12, 18, 28];

export function OnboardingPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);

  // Step 2 data
  const [bizName, setBizName] = useState("");
  const [gstin, setGstin] = useState("");
  const [industry, setIndustry] = useState("");
  const [address, setAddress] = useState("");
  const [nameError, setNameError] = useState("");

  // Step 3 data
  const [fyMonth, setFyMonth] = useState("April");
  const [payTerms, setPayTerms] = useState("Net 30");
  const [gstRates, setGstRates] = useState<number[]>([5, 12, 18, 28]);

  // Step 4 data
  const [inviteEmail, setInviteEmail] = useState("");

  const completeStep = async (stepNum: number, data?: any) => {
    setSaving(true);
    try {
      await apiFetch(`/complete-step`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step: stepNum, data }),
      });
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  const goNext = () => setStep(s => s + 1);

  const handleStep2 = async () => {
    if (!bizName.trim()) { setNameError("Business name is required"); return; }
    setNameError("");
    await completeStep(2, { business_name: bizName, gstin, industry, address });
    goNext();
  };

  const handleStep3 = async () => {
    await completeStep(3, {
      fy_start_month: fyMonth,
      default_payment_terms: payTerms,
      default_gst_rates: gstRates.join(","),
    });
    goNext();
  };

  const handleStep4Skip = async () => {
    await completeStep(4);
    goNext();
  };

  const handleStep4Send = async () => {
    await completeStep(4, { accountant_email: inviteEmail });
    goNext();
  };

  const handleFinish = async (dest: string) => {
    await completeStep(5);
    navigate(dest);
  };

  const toggleRate = (rate: number) => {
    setGstRates(prev => prev.includes(rate) ? prev.filter(r => r !== rate) : [...prev, rate]);
  };

  const TOTAL_STEPS = 5;

  return (
    <div className="min-h-screen bg-bg-base flex flex-col items-center justify-center p-4">
      {/* Logo */}
      <div className="mb-6">
        <img src="/hermes_logo.png" alt="HERMES" className="h-14 object-contain" />
      </div>

      {/* Step Indicator */}
      <div className="flex items-center gap-0 mb-10">
        {Array.from({ length: TOTAL_STEPS }, (_, i) => {
          const num = i + 1;
          const done = num < step;
          const current = num === step;
          return (
            <div key={num} className="flex items-center">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                done ? "bg-green-500 text-white" : current ? "bg-accent text-white" : "bg-bg-subtle border border-border text-text-muted"
              }`}>
                {done ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><path d="M5 13l4 4L19 7" /></svg>
                ) : num}
              </div>
              {num < TOTAL_STEPS && (
                <div className={`w-8 md:w-12 h-0.5 ${done ? "bg-green-500" : "bg-border"}`} />
              )}
            </div>
          );
        })}
      </div>

      {/* Step Content */}
      <div className="w-full max-w-lg">
        {/* Step 1: Welcome */}
        {step === 1 && (
          <div className="text-center animate-fade-in">
            <h1 className="text-3xl md:text-4xl font-black font-display text-text-base mb-3">Welcome to HERMES.</h1>
            <p className="text-text-secondary text-lg mb-10">Let's set up your business in under 2 minutes.</p>
            <Button variant="primary" onClick={() => { completeStep(1); goNext(); }} className="!px-10 !py-3 !text-base">
              Get Started →
            </Button>
          </div>
        )}

        {/* Step 2: Business Profile */}
        {step === 2 && (
          <div className="bg-bg-surface border border-border rounded-2xl p-6 md:p-8 animate-fade-in">
            <h2 className="text-xl font-bold text-text-base mb-1">Business Profile</h2>
            <p className="text-sm text-text-muted mb-6">Tell us about your business.</p>
            <div className="space-y-4">
              <div>
                <Input label="Business Name *" value={bizName} onChange={e => { setBizName(e.target.value); setNameError(""); }} placeholder="Acme Technologies Pvt. Ltd." />
                {nameError && <p className="text-xs text-danger mt-1">{nameError}</p>}
              </div>
              <Input label="GSTIN" value={gstin} onChange={e => setGstin(e.target.value)} placeholder="22AAAAA0000A1Z5 (optional)" />
              <Input label="Industry" value={industry} onChange={e => setIndustry(e.target.value)} placeholder="e.g. Technology, Manufacturing" />
              <Input label="Address" value={address} onChange={e => setAddress(e.target.value)} placeholder="Full business address" />
            </div>
            <div className="flex items-center justify-between mt-6">
              <button onClick={() => { completeStep(2); goNext(); }} className="text-sm text-text-muted hover:text-text-base transition-colors">Skip for now</button>
              <Button variant="primary" onClick={handleStep2} disabled={saving}>{saving ? "Saving..." : "Continue →"}</Button>
            </div>
          </div>
        )}

        {/* Step 3: Financial Year */}
        {step === 3 && (
          <div className="bg-bg-surface border border-border rounded-2xl p-6 md:p-8 animate-fade-in">
            <h2 className="text-xl font-bold text-text-base mb-1">Financial Configuration</h2>
            <p className="text-sm text-text-muted mb-6">Set your defaults — you can change these later in Settings.</p>

            <div className="space-y-6">
              {/* FY Start */}
              <div>
                <label className="text-xs font-semibold text-text-muted uppercase block mb-2">Financial Year Starts In</label>
                <div className="grid grid-cols-2 gap-3">
                  {["April", "January"].map(m => (
                    <button key={m} onClick={() => setFyMonth(m)} className={`p-4 rounded-xl border-2 text-left transition-all ${fyMonth === m ? "border-accent bg-accent/5" : "border-border hover:border-accent/30"}`}>
                      <p className="font-semibold text-text-base">{m}</p>
                      <p className="text-xs text-text-muted mt-0.5">{m === "April" ? "Indian FY (Apr–Mar)" : "Calendar Year (Jan–Dec)"}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Payment Terms */}
              <div>
                <label className="text-xs font-semibold text-text-muted uppercase block mb-2">Default Payment Terms</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { val: "Net 15", title: "Net 15", desc: "Quick payment" },
                    { val: "Net 30", title: "Net 30", desc: "Standard" },
                    { val: "Net 45", title: "Net 45", desc: "Extended" },
                  ].map(t => (
                    <button key={t.val} onClick={() => setPayTerms(t.val)} className={`p-3 rounded-xl border-2 text-center transition-all ${payTerms === t.val ? "border-accent bg-accent/5" : "border-border hover:border-accent/30"}`}>
                      <p className="font-semibold text-text-base text-sm">{t.title}</p>
                      <p className="text-[11px] text-text-muted">{t.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* GST Rates */}
              <div>
                <label className="text-xs font-semibold text-text-muted uppercase block mb-2">Default GST Rates</label>
                <div className="flex flex-wrap gap-2">
                  {GST_RATES.map(rate => (
                    <button key={rate} onClick={() => toggleRate(rate)} className={`px-4 py-2 text-sm font-semibold rounded-full border transition-all ${gstRates.includes(rate) ? "bg-accent text-white border-accent" : "bg-bg-base text-text-muted border-border hover:border-accent/50"}`}>
                      {rate}%
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <Button variant="primary" onClick={handleStep3} disabled={saving}>{saving ? "Saving..." : "Continue →"}</Button>
            </div>
          </div>
        )}

        {/* Step 4: Invite Accountant */}
        {step === 4 && (
          <div className="bg-bg-surface border border-border rounded-2xl p-6 md:p-8 animate-fade-in text-center">
            <h2 className="text-xl font-bold text-text-base mb-1">Invite Your Accountant</h2>
            <p className="text-sm text-text-muted mb-6">If someone else manages your books, add them here.</p>
            <div className="max-w-sm mx-auto space-y-4">
              <Input label="Email Address" type="email" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="accountant@example.com" />
              <Button variant="secondary" onClick={handleStep4Send} disabled={!inviteEmail || saving} className="w-full">
                {saving ? "Sending..." : "Send Invite"}
              </Button>
            </div>
            <button onClick={handleStep4Skip} className="mt-6 text-sm text-text-secondary hover:text-accent font-medium transition-colors inline-flex items-center gap-1">
              Skip, I'll do this myself →
            </button>
          </div>
        )}

        {/* Step 5: Ready */}
        {step === 5 && (
          <div className="text-center animate-fade-in">
            {/* Checkmark animation */}
            <div className="w-20 h-20 rounded-full bg-green-500 flex items-center justify-center mx-auto mb-6 animate-scale-in">
              <svg className="w-10 h-10 text-white animate-draw-check" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-black font-display text-text-base mb-2">HERMES is ready.</h1>
            <p className="text-text-muted mb-8">Your workspace is set up. What would you like to do first?</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-md mx-auto">
              <button onClick={() => handleFinish("/upload")} className="p-5 bg-bg-surface border border-border rounded-xl hover:border-accent hover:shadow-md transition-all group">
                <div className="text-3xl mb-2">📄</div>
                <p className="font-semibold text-text-base group-hover:text-accent transition-colors">Upload your first document</p>
                <p className="text-xs text-text-muted mt-1">Start processing invoices</p>
              </button>
              <button onClick={() => handleFinish("/chat")} className="p-5 bg-bg-surface border border-border rounded-xl hover:border-accent hover:shadow-md transition-all group">
                <div className="text-3xl mb-2">💬</div>
                <p className="font-semibold text-text-base group-hover:text-accent transition-colors">Chat with HERMES</p>
                <p className="text-xs text-text-muted mt-1">Ask anything about your books</p>
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes scale-in {
          0% { transform: scale(0); opacity: 0; }
          60% { transform: scale(1.2); }
          100% { transform: scale(1); opacity: 1; }
        }
        @keyframes draw-check {
          0% { stroke-dashoffset: 30; opacity: 0; }
          40% { opacity: 1; }
          100% { stroke-dashoffset: 0; opacity: 1; }
        }
        .animate-scale-in { animation: scale-in 0.5s ease-out forwards; }
        .animate-draw-check {
          stroke-dasharray: 30;
          stroke-dashoffset: 30;
          animation: draw-check 0.6s 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Badge } from "../components/ui/Badge";
import { useNavigate } from "react-router-dom";

export function MappingRulesPage() {
  const navigate = useNavigate();
  const [rules, setRules] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Form
  const [showForm, setShowForm] = useState(false);
  const [condition, setCondition] = useState("contains");
  const [matchValue, setMatchValue] = useState("");
  const [accountId, setAccountId] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [rulesRes, accRes] = await Promise.all([
        apiFetch("/accounts/mapping-rules"),
        apiFetch("/accounts")
      ]);
      if (rulesRes.ok) {
        const data = await rulesRes.json();
        setRules(data.rules || []);
      }
      if (accRes.ok) {
        const data = await accRes.json();
        setAccounts(data.accounts || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountId) return;
    
    setSaving(true);
    try {
      await apiFetch("/accounts/mapping-rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          condition_type: condition,
          match_value: matchValue,
          map_to_account_id: parseInt(accountId)
        })
      });
      setShowForm(false);
      setMatchValue("");
      fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const toggleStatus = async (id: number, currentActive: number) => {
    try {
      await apiFetch(`/accounts/mapping-rules/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active: currentActive === 1 ? 0 : 1 })
      });
      fetchData();
    } catch(err) { console.error(err); }
  };

  const deleteRule = async (id: number) => {
    if (!window.confirm("Delete rule?")) return;
    try {
      await apiFetch(`/accounts/mapping-rules/${id}`, { method: "DELETE" });
      fetchData();
    } catch(err) { console.error(err); }
  };

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/accounts")} className="p-1.5 text-text-muted hover:bg-bg-overlay hover:text-text-base rounded transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15 19l-7-7 7-7" /></svg>
          </button>
          <div>
            <h1 className="text-xl font-bold font-display text-text-base">Mapping Rules</h1>
            <p className="text-sm text-text-muted">Auto-categorize bank statement entries.</p>
          </div>
        </div>
        <Button variant="primary" onClick={() => setShowForm(true)}>+ Add Rule</Button>
      </div>

      {showForm && (
        <div className="bg-bg-surface border border-border rounded-xl p-5 mb-6 animate-[fade-in_200ms_ease]">
          <h3 className="font-semibold text-text-base mb-4">Add Configuration Rule</h3>
          <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
            <div className="w-48">
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">When Description</label>
              <select className="w-full h-10 px-3 py-2 bg-bg-surface border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent" value={condition} onChange={e => setCondition(e.target.value)}>
                <option value="contains">Contains</option>
                <option value="exact_match">Exact Match</option>
                <option value="starts_with">Starts With</option>
              </select>
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">Match Value</label>
              <Input required placeholder="E.g., AWS, Zomato, Uber" value={matchValue} onChange={e => setMatchValue(e.target.value)} />
            </div>
            <div className="w-64">
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">Map to Account</label>
              <select className="w-full h-10 px-3 py-2 bg-bg-surface border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent" required value={accountId} onChange={e => setAccountId(e.target.value)}>
                <option value="" disabled>Select Account...</option>
                {accounts.filter(a => a.type === 'expense' || a.type === 'revenue' || a.type==='asset').map(a => (
                  <option key={a.id} value={a.id}>{a.code} - {a.name}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => setShowForm(false)} type="button">Cancel</Button>
              <Button variant="primary" type="submit" disabled={saving || !accountId}>{saving ? "Saving..." : "Save Rule"}</Button>
            </div>
          </form>
        </div>
      )}

      <div className="flex-1 overflow-x-auto bg-bg-surface border border-border rounded-xl">
        <table className="w-full text-sm">
          <thead className="bg-bg-subtle text-text-secondary">
            <tr>
              <th className="px-6 py-3 text-left font-semibold uppercase text-xs tracking-wider">Condition</th>
              <th className="px-6 py-3 text-left font-semibold uppercase text-xs tracking-wider">Match Value</th>
              <th className="px-6 py-3 text-left font-semibold uppercase text-xs tracking-wider">Maps To</th>
              <th className="px-6 py-3 text-center font-semibold uppercase text-xs tracking-wider">Status</th>
              <th className="px-6 py-3 text-right font-semibold uppercase text-xs tracking-wider">Options</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {rules.map((rule, idx) => (
              <tr key={rule.id} className="hover:bg-bg-overlay transition-colors">
                <td className="px-6 py-4 font-medium capitalize text-text-secondary">{rule.condition_type.replace('_', ' ')}</td>
                <td className="px-6 py-4 font-mono font-medium text-text-base">"{rule.match_value}"</td>
                <td className="px-6 py-4">
                  <span className="bg-accent-subtle/40 text-accent font-medium px-2 py-1 rounded text-xs">{rule.account_code} - {rule.account_name}</span>
                </td>
                <td className="px-6 py-4 text-center">
                  <Badge status={rule.active === 1 ? "paid" : "draft"} label={rule.active === 1 ? "ACTIVE" : "INACTIVE"} />
                </td>
                <td className="px-6 py-4 text-right flex gap-3 justify-end items-center h-full">
                  <Button variant="ghost" size="sm" onClick={() => toggleStatus(rule.id, rule.active)}>
                    {rule.active === 1 ? "Disable" : "Enable"}
                  </Button>
                  <button onClick={() => deleteRule(rule.id)} className="text-danger hover:text-danger/80 p-1">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </td>
              </tr>
            ))}
            {rules.length === 0 && !loading && (
              <tr><td colSpan={5} className="py-12 text-center text-text-muted">No mapping rules defined.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

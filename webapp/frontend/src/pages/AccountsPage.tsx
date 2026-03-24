import { useState, useEffect, useCallback } from "react";
import { apiFetch } from '../api/client';
import { PageHeader } from "../components/layout/PageHeader";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { useNavigate } from "react-router-dom";

interface Account {
  id: number;
  code: string;
  name: string;
  type: string;
  parent_id: number | null;
  active: number;
  balance: number;
  children?: Account[];
}

function buildTree(accounts: Account[]): Account[] {
  const map = new Map<number, Account>();
  const roots: Account[] = [];

  accounts.forEach(acc => {
    map.set(acc.id, { ...acc, children: [] });
  });

  accounts.forEach(acc => {
    const node = map.get(acc.id)!;
    if (node.parent_id === null) {
      roots.push(node);
    } else {
      const parent = map.get(node.parent_id);
      if (parent) {
        parent.children!.push(node);
      } else {
        roots.push(node); // Fallback
      }
    }
  });

  return roots;
}

interface AccountTreeNodeProps {
  node: Account;
  level: number;
  onAddSub: (parent_id: number) => void;
  onEdit: (account: Account) => void;
  onDeactivate: (id: number) => void;
}

function AccountTreeNode({ node, level, onAddSub, onEdit, onDeactivate }: AccountTreeNodeProps) {
  const [expanded, setExpanded] = useState(level < 1);
  const [hovered, setHovered] = useState(false);
  
  const hasChildren = node.children && node.children.length > 0;
  const paddingLeft = `${level * 1.5 + 1}rem`;

  return (
    <div className="w-full">
      <div 
        className="flex items-center justify-between border-b border-border hover:bg-bg-subtle transition-colors group h-12"
        style={{ paddingLeft, paddingRight: "1rem" }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <div className="flex items-center gap-3 w-1/2">
          {hasChildren ? (
            <button 
              onClick={() => setExpanded(!expanded)}
              className="w-5 h-5 flex items-center justify-center text-text-muted hover:text-text-base rounded transition-all"
            >
              <svg 
                className={`w-4 h-4 transition-transform duration-200 ${expanded ? 'rotate-90' : ''}`} 
                fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          ) : (
            <div className="w-5 h-5" /> // Spacer
          )}
          <span className="font-mono text-xs font-semibold text-text-secondary w-14">{node.code}</span>
          <span className={`font-medium ${level === 0 ? "text-text-base" : "text-text-secondary"}`}>
            {node.name}
          </span>
        </div>

        <div className="flex items-center gap-4 w-1/2 justify-end">
          {hovered && (
            <div className="flex items-center gap-1 opacity-100 animate-[fade-in_150ms_ease]">
              <button onClick={() => onAddSub(node.id)} className="p-1.5 text-text-muted hover:bg-bg-overlay rounded transition-colors" title="Add Sub-account">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M12 4v16m8-8H4" /></svg>
              </button>
              <button onClick={() => onEdit(node)} className="p-1.5 text-text-muted hover:text-accent hover:bg-bg-overlay rounded transition-colors" title="Edit Account">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
              </button>
              <button onClick={() => { if(window.confirm(`Deactivate ${node.name}?`)) onDeactivate(node.id) }} className="p-1.5 text-text-muted hover:text-danger hover:bg-danger/10 rounded transition-colors" title="Deactivate Account">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
              </button>
            </div>
          )}
          
          <Badge status="draft" label={node.type.toUpperCase()} />
          <span className="font-mono font-medium text-right w-28 text-text-base">
            {node.balance === 0 ? "—" : `₹${Math.abs(node.balance).toLocaleString("en-IN")}`}
          </span>
        </div>
      </div>
      
      {hasChildren && expanded && (
        <div className="flex flex-col animate-[fade-in_200ms_ease]">
          {node.children!.map(child => (
            <AccountTreeNode 
              key={child.id} 
              node={child} 
              level={level + 1} 
              onAddSub={onAddSub}
              onEdit={onEdit}
              onDeactivate={onDeactivate}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function AccountsPage() {
  const navigate = useNavigate();
  const [tree, setTree] = useState<Account[]>([]);
  const [flatAccounts, setFlatAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formCode, setFormCode] = useState("");
  const [formName, setFormName] = useState("");
  const [formType, setFormType] = useState("asset");
  const [formParent, setFormParent] = useState<string>("none");
  const [saving, setSaving] = useState(false);

  const fetchAccounts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch("/accounts");
      if (res.ok) {
        const data = await res.json();
        setFlatAccounts(data.accounts);
        setTree(buildTree(data.accounts));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAccounts(); }, [fetchAccounts]);

  const handleAdd = (parent_id: number | "none" = "none") => {
    setEditingId(null);
    setFormCode("");
    setFormName("");
    setFormType("asset");
    setFormParent(String(parent_id));
    setShowForm(true);
  };

  const handleEdit = (node: Account) => {
    setEditingId(node.id);
    setFormCode(node.code);
    setFormName(node.name);
    setFormType(node.type);
    setFormParent(node.parent_id !== null ? String(node.parent_id) : "none");
    setShowForm(true);
  };

  const handleDeactivate = async (id: number) => {
    try {
      await apiFetch(`/accounts/${id}`, { method: "DELETE" });
      fetchAccounts();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        code: formCode,
        name: formName,
        type: formType,
        parent_id: formParent === "none" ? null : parseInt(formParent)
      };

      if (editingId) {
        await apiFetch(`/accounts/${editingId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: formName, type: formType })
        });
      } else {
        await apiFetch("/accounts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      }
      setShowForm(false);
      fetchAccounts();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="animate-fade-in flex flex-col h-full bg-bg-base">
      <div className="flex items-center justify-between mb-6">
        <PageHeader title="Chart of Accounts" />
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={() => navigate("/accounts/mapping-rules")}>
            Mapping Rules
          </Button>
          <Button variant="primary" onClick={() => handleAdd("none")}>
            + Add Account
          </Button>
        </div>
      </div>

      {showForm && (
        <div className="bg-bg-surface border border-border rounded-xl p-5 mb-6 animate-[fade-in_200ms_ease]">
          <h3 className="font-semibold text-text-base mb-4">{editingId ? "Edit Account" : "Add New Account"}</h3>
          <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
            <div className="w-24">
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">Code</label>
              <Input required value={formCode} onChange={e => setFormCode(e.target.value)} disabled={!!editingId} />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">Name</label>
              <Input required value={formName} onChange={e => setFormName(e.target.value)} />
            </div>
            <div className="w-40">
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">Type</label>
              <select className="w-full h-10 px-3 py-2 bg-bg-surface border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent" value={formType} onChange={e => setFormType(e.target.value)}>
                <option value="asset">Asset</option>
                <option value="liability">Liability</option>
                <option value="equity">Equity</option>
                <option value="revenue">Revenue</option>
                <option value="expense">Expense</option>
              </select>
            </div>
            <div className="w-64">
              <label className="block text-xs font-medium text-text-secondary uppercase tracking-wider mb-1.5">Parent Account</label>
              <select className="w-full h-10 px-3 py-2 bg-bg-surface border border-border rounded-lg text-sm text-text-base focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent" value={formParent} onChange={e => setFormParent(e.target.value)} disabled={!!editingId}>
                <option value="none">— Top Level —</option>
                {flatAccounts.map(a => (
                  <option key={a.id} value={a.id}>{a.code} - {a.name}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-2 ml-auto">
              <Button variant="secondary" onClick={() => setShowForm(false)} type="button">Cancel</Button>
              <Button variant="primary" type="submit" disabled={saving}>{saving ? "Saving..." : "Save Account"}</Button>
            </div>
          </form>
        </div>
      )}

      <div className="flex-1 overflow-y-auto bg-bg-surface border border-border rounded-xl">
        {/* Table Header */}
        <div className="flex items-center justify-between border-b border-border bg-bg-subtle px-4 py-3 font-semibold text-xs text-text-secondary uppercase tracking-wider shrink-0 sticky top-0 z-10">
          <div className="w-1/2 px-2">Account</div>
          <div className="w-1/2 flex items-center justify-end">
            <span className="w-24 text-center">Type</span>
            <span className="w-28 text-right px-4">Balance</span>
          </div>
        </div>
        
        {/* Tree Content */}
        {loading ? (
          <div className="p-8 text-center text-text-muted animate-pulse">Loading Chart of Accounts...</div>
        ) : (
          <div className="pb-16">
            {tree.map(node => (
              <AccountTreeNode 
                key={node.id} 
                node={node} 
                level={0} 
                onAddSub={(p) => handleAdd(p)}
                onEdit={handleEdit}
                onDeactivate={handleDeactivate}
              />
            ))}
            {tree.length === 0 && <p className="p-8 text-center text-text-muted">No accounts found.</p>}
          </div>
        )}
      </div>
    </div>
  );
}

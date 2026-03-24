import { useState, useEffect, useCallback } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { apiFetch } from '../../api/client';
import { clsx } from 'clsx';
import type { Icon } from '@phosphor-icons/react';
import { 
  SquaresFour, ChatCircleText, UploadSimple, Receipt, 
  Users, CreditCard, ChartLineUp, Files, Warning, 
  TreeStructure, ShieldCheck, Gear, Heartbeat, CaretDown, CaretRight, CaretLeft
} from '@phosphor-icons/react';

interface SidebarProps {
  mobileOpen: boolean;
  onMobileClose: () => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

type NavSubItem = { label: string; path: string; };

type NavItemProp = {
  label: string;
  icon: Icon;
  path?: string;
  end?: boolean;
  subItems?: NavSubItem[];
};

type NavGroup = {
  group: string;
  items: NavItemProp[];
};

const NAV_ITEMS: NavGroup[] = [
  { group: 'OVERVIEW', items: [
    { label: 'Dashboard', path: '/', icon: SquaresFour, end: true },
  ]},
  { group: 'OPERATIONS', items: [
    { label: 'Chat with HERMES', path: '/chat', icon: ChatCircleText },
    { label: 'Upload Documents', path: '/upload', icon: UploadSimple },
  ]},
  { group: 'FINANCE', items: [
    { 
      label: 'Invoices', 
      icon: Receipt,
      subItems: [
        { label: 'Sales', path: '/invoices/sales' },
        { label: 'Purchases', path: '/invoices/purchases' },
      ]
    },
    { label: 'Contacts', path: '/contacts', icon: Users },
    { label: 'Payments', path: '/payments', icon: CreditCard },
  ]},
  { group: 'RECORDS', items: [
    { label: 'Reports', path: '/reports', icon: ChartLineUp },
    { label: 'Documents', path: '/documents', icon: Files },
    { label: 'Anomalies', path: '/anomalies', icon: Warning },
  ]},
  { group: 'ACCOUNTS', items: [
    { label: 'Chart of Accounts', path: '/accounts', icon: TreeStructure },
    { label: 'Audit Trail', path: '/audit', icon: ShieldCheck },
  ]},
  { group: 'SYSTEM', items: [
    { label: 'Settings', path: '/settings', icon: Gear },
    { label: 'System Health', path: '/system', icon: Heartbeat },
  ]},
];

export function Sidebar({ mobileOpen, onMobileClose, collapsed, onToggleCollapse }: SidebarProps) {
  const location = useLocation();
  const [invoicesOpen, setInvoicesOpen] = useState(() => {
    return location.pathname.startsWith('/invoices');
  });
  const [anomalyCount, setAnomalyCount] = useState(0);

  const fetchAnomalyCount = useCallback(async () => {
    try {
      const res = await apiFetch("/anomalies/count/unreviewed");
      if (res.ok) { const d = await res.json(); setAnomalyCount(d.count); }
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    apiFetch("/anomalies/count/unreviewed", { signal: controller.signal })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setAnomalyCount(d.count); })
      .catch(() => {});
    const t = setInterval(fetchAnomalyCount, 60000);
    return () => { controller.abort(); clearInterval(t); };
  }, [fetchAnomalyCount]);

  const navContent = (
    <div className="flex flex-col h-full overflow-y-auto overflow-x-hidden p-3 gap-6">
      {NAV_ITEMS.map((group) => (
        <div key={group.group} className="flex flex-col gap-1">
          {!collapsed && (
            <div className="px-3 mb-1 text-[11px] font-medium text-text-muted uppercase tracking-[0.05em] whitespace-nowrap">
              {group.group}
            </div>
          )}
          
          {group.items.map((item) => {
            const Icon = item.icon;
            if (item.subItems) {
              const isActive = location.pathname.startsWith('/invoices');
              return (
                <div key={item.label} className="flex flex-col">
                  <button
                    onClick={() => {
                      if (collapsed) onToggleCollapse();
                      setInvoicesOpen(!invoicesOpen);
                    }}
                    className={clsx(
                      "flex items-center gap-3 px-3 py-2 rounded-md transition-colors w-full text-left",
                      isActive ? "bg-accent-subtle text-accent border-l-2 border-l-accent" : "text-text-secondary hover:text-text-primary hover:bg-bg-overlay border-l-2 border-transparent"
                    )}
                    title={collapsed ? item.label : undefined}
                  >
                    <Icon size={20} weight={isActive ? "bold" : "regular"} className="shrink-0" />
                    {!collapsed && (
                      <>
                        <span className="flex-1 text-[14px] font-medium leading-[1.4] whitespace-nowrap">{item.label}</span>
                        {invoicesOpen ? <CaretDown size={14} className="shrink-0" /> : <CaretRight size={14} className="shrink-0" />}
                      </>
                    )}
                  </button>
                  
                  {!collapsed && invoicesOpen && (
                    <div className="flex flex-col gap-0.5 mt-1">
                      {item.subItems.map((sub) => (
                        <NavLink
                          key={sub.path}
                          to={sub.path}
                          onClick={() => window.innerWidth < 768 && onMobileClose()}
                          className={({ isActive }) => clsx(
                            "flex items-center pl-[44px] pr-3 py-1.5 rounded-md transition-colors text-[13px] whitespace-nowrap",
                            isActive ? "text-accent font-medium bg-accent-subtle" : "text-text-secondary hover:text-text-primary hover:bg-bg-overlay"
                          )}
                        >
                          {sub.label}
                        </NavLink>
                      ))}
                    </div>
                  )}
                </div>
              );
            }

            return (
              <NavLink
                key={item.path || item.label}
                to={item.path || '#'}
                end={item.end}
                onClick={() => window.innerWidth < 768 && onMobileClose()}
                title={collapsed ? item.label : undefined}
                className={({ isActive }) => clsx(
                  "flex items-center gap-3 px-3 py-2 rounded-md transition-colors border-l-2",
                  isActive 
                    ? "bg-accent-subtle text-accent border-l-accent font-medium" 
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-overlay border-l-transparent"
                )}
              >
                {({ isActive }) => (
                  <>
                    <Icon size={20} weight={isActive ? "bold" : "regular"} className="shrink-0" />
                    {!collapsed && (
                      <>
                        <span className="text-[14px] leading-[1.4] whitespace-nowrap flex-1">{item.label}</span>
                        {item.label === 'Anomalies' && anomalyCount > 0 && (
                          <span className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-danger text-white text-[11px] font-bold rounded-full">
                            {anomalyCount}
                          </span>
                        )}
                      </>
                    )}
                    {collapsed && item.label === 'Anomalies' && anomalyCount > 0 && (
                      <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-danger rounded-full border-2 border-bg-surface" />
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </div>
      ))}
    </div>
  );

  return (
    <>
      <div 
        className={clsx(
          "md:hidden fixed inset-0 bg-black/40 z-[190] transition-opacity duration-200",
          mobileOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={onMobileClose}
      />
      <aside 
        className={clsx(
          "fixed top-[52px] md:top-[56px] bottom-0 left-0 bg-bg-surface border-r border-border z-[200] flex flex-col transition-all duration-300",
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
        style={{ width: mobileOpen ? 280 : (collapsed ? 60 : 240) }}
      >
        <div className="flex-1 overflow-hidden hover:overflow-y-auto style-scrollbar">
          {navContent}
        </div>
        
        <div className="hidden md:flex p-3 border-t border-border shrink-0">
          <button 
            onClick={onToggleCollapse}
            className="flex items-center justify-center w-full py-2 hover:bg-bg-overlay rounded-md transition-colors text-text-secondary"
          >
            {collapsed ? <CaretRight size={16} /> : <CaretLeft size={16} />}
          </button>
        </div>
      </aside>
    </>
  );
}

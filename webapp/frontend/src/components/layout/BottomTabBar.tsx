import { NavLink } from 'react-router-dom';
import { clsx } from 'clsx';
import { SquaresFour, ChatCircleText, Receipt, ChartLineUp, List } from '@phosphor-icons/react';
import { BottomSheet } from '../ui/BottomSheet';
import { useState } from 'react';

export function BottomTabBar() {
  const [moreOpen, setMoreOpen] = useState(false);

  const tabs = [
    { label: 'Home', path: '/', icon: SquaresFour, exact: true },
    { label: 'Chat', path: '/chat', icon: ChatCircleText },
    { label: 'Invoices', path: '/invoices/sales', icon: Receipt },
    { label: 'Reports', path: '/reports', icon: ChartLineUp },
  ];

  return (
    <>
      <nav className="md:hidden fixed bottom-0 inset-x-0 h-[64px] bg-bg-surface border-t border-border z-[100] pb-[env(safe-area-inset-bottom)] flex">
        {tabs.map((tab) => (
          <NavLink
            key={tab.path}
            to={tab.path}
            end={tab.exact}
            className={({ isActive }) => clsx(
              "flex-1 flex flex-col items-center justify-center gap-1 transition-colors",
              isActive ? "text-accent" : "text-text-muted hover:text-text-secondary"
            )}
          >
            {({ isActive }) => (
              <>
                <tab.icon size={24} weight={isActive ? "fill" : "regular"} />
                <span className="text-[10px] font-medium">{tab.label}</span>
              </>
            )}
          </NavLink>
        ))}
        
        <button
          onClick={() => setMoreOpen(true)}
          className={clsx(
            "flex-1 flex flex-col items-center justify-center gap-1 transition-colors",
            moreOpen ? "text-accent" : "text-text-muted hover:text-text-secondary"
          )}
        >
          <List size={24} weight={moreOpen ? "fill" : "regular"} />
          <span className="text-[10px] font-medium">More</span>
        </button>
      </nav>

      <BottomSheet open={moreOpen} onClose={() => setMoreOpen(false)} title="Menu">
        <div className="flex flex-col gap-2">
          <NavLink to="/contacts" className="p-3 bg-bg-subtle rounded-md text-text-primary text-center font-medium" onClick={() => setMoreOpen(false)}>Contacts</NavLink>
          <NavLink to="/payments" className="p-3 bg-bg-subtle rounded-md text-text-primary text-center font-medium" onClick={() => setMoreOpen(false)}>Payments</NavLink>
          <NavLink to="/documents" className="p-3 bg-bg-subtle rounded-md text-text-primary text-center font-medium" onClick={() => setMoreOpen(false)}>Documents</NavLink>
          <NavLink to="/accounts" className="p-3 bg-bg-subtle rounded-md text-text-primary text-center font-medium" onClick={() => setMoreOpen(false)}>Accounts</NavLink>
          <NavLink to="/settings" className="p-3 bg-bg-subtle rounded-md text-text-primary text-center font-medium" onClick={() => setMoreOpen(false)}>Settings</NavLink>
        </div>
      </BottomSheet>
    </>
  );
}

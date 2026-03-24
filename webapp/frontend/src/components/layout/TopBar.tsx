import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { List, MagnifyingGlass, Bell, Sun, Moon } from '@phosphor-icons/react';
import { apiFetch } from '../../api/client';
import { useTheme } from '../../hooks/useTheme';
import { Tooltip } from '../ui/Tooltip';
import { NotificationPanel } from '../notifications/NotificationPanel';
import { SearchModal } from '../search/SearchModal';

export function TopBar({ onMenuClick }: { onMenuClick: () => void }) {
  const { theme, toggleTheme } = useTheme();
  const [panelOpen, setPanelOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchUnread = useCallback(async () => {
    try {
      const res = await apiFetch("/notifications/count/unread");
      if (res.ok) {
        const data = await res.json();
        setUnreadCount(data.count);
      }
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    apiFetch("/notifications/count/unread", { signal: controller.signal })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setUnreadCount(d.count); })
      .catch(() => {});
    const t = setInterval(fetchUnread, 30000);
    return () => { controller.abort(); clearInterval(t); };
  }, [fetchUnread]);

  // Cmd+K / Ctrl+K keyboard shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(prev => !prev);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  const handleCountChange = (delta: number) => {
    if (delta === 0) setUnreadCount(0); // mark all read
    else setUnreadCount(c => Math.max(0, c + delta)); // decrement by 1
  };

  const formatCount = (n: number) => n > 99 ? "99+" : String(n);

  return (
    <>
      <header className="fixed top-0 inset-x-0 h-[52px] md:h-[56px] bg-bg-surface border-b border-border z-[100] flex items-center px-4 md:px-6">
        <button 
          onClick={onMenuClick}
          className="md:hidden p-2 -ml-2 mr-2 text-text-secondary hover:text-text-primary transition-colors hover:bg-bg-overlay rounded-md"
          title="Toggle menu"
        >
          <List size={24} />
        </button>
        
        <Link 
          to="/" 
          className="flex items-center gap-2 hover:opacity-80 transition-opacity"
        >
          <img src="/hermes_logo.png" alt="" className="h-7 w-auto" />
          <span className="text-[18px] md:text-[20px] font-bold text-text-primary tracking-tight font-sans">HERMES</span>
        </Link>
        
        <div className="flex-1" />
        
        <div className="flex items-center gap-1 md:gap-2">
          <Tooltip content="Global Search (Cmd+K)" className="z-[110]">
            <button onClick={() => setSearchOpen(true)} className="w-9 h-9 flex items-center justify-center rounded-md text-text-secondary hover:text-text-primary hover:bg-bg-overlay transition-colors" title="Search">
              <MagnifyingGlass size={20} />
            </button>
          </Tooltip>
          
          <Tooltip content="Notifications" className="z-[110]">
            <button
              onClick={() => setPanelOpen(true)}
              className="w-9 h-9 flex items-center justify-center rounded-md text-text-secondary hover:text-text-primary hover:bg-bg-overlay transition-colors relative"
              title="Notifications"
            >
              <Bell size={20} />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center bg-danger text-white text-[10px] font-bold rounded-full px-1 ring-2 ring-bg-surface">
                  {formatCount(unreadCount)}
                </span>
              )}
            </button>
          </Tooltip>
          
          <Tooltip content="System: Healthy" className="z-[110]">
            <Link to="/system" className="w-9 h-9 flex items-center justify-center rounded-md hover:bg-bg-overlay transition-colors">
              <div className="w-2 h-2 rounded-full bg-success ring-4 ring-success-bg" />
            </Link>
          </Tooltip>

          <Tooltip content={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`} className="z-[110]">
            <button 
              onClick={toggleTheme}
              className="w-9 h-9 flex items-center justify-center rounded-md text-text-secondary hover:text-text-primary hover:bg-bg-overlay transition-colors"
              title="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </Tooltip>
        </div>
      </header>

      <NotificationPanel
        open={panelOpen}
        onClose={() => { setPanelOpen(false); fetchUnread(); }}
        onCountChange={handleCountChange}
      />

      <SearchModal open={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

const API = "http://localhost:8000/api/notifications";

const TABS = [
  { key: "all", label: "All" },
  { key: "unread", label: "Unread" },
  { key: "anomalies", label: "Anomalies" },
  { key: "system", label: "System" },
];

const TYPE_ICONS: Record<string, { icon: string; bg: string; color: string }> = {
  anomaly: { icon: "⚠", bg: "bg-warning/10", color: "text-warning" },
  system: { icon: "⚙", bg: "bg-accent/10", color: "text-accent" },
  invoice: { icon: "📄", bg: "bg-green-500/10", color: "text-green-500" },
  payment: { icon: "💳", bg: "bg-purple-500/10", color: "text-purple-500" },
  upload: { icon: "📤", bg: "bg-blue-500/10", color: "text-blue-500" },
  default: { icon: "🔔", bg: "bg-text-muted/10", color: "text-text-muted" },
};

interface NotificationPanelProps {
  open: boolean;
  onClose: () => void;
  onCountChange?: (count: number) => void;
}

export function NotificationPanel({ open, onClose, onCountChange }: NotificationPanelProps) {
  const navigate = useNavigate();
  const [tab, setTab] = useState("all");
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}?tab=${tab}`);
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.items || []);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [tab]);

  useEffect(() => {
    if (open) fetchNotifications();
  }, [open, fetchNotifications]);

  const markAllRead = async () => {
    try {
      await fetch(`${API}/mark-read`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ all: true }),
      });
      setNotifications(prev => prev.map(n => ({ ...n, is_read: 1 })));
      onCountChange?.(0);
    } catch (e) { console.error(e); }
  };

  const handleClick = async (n: any) => {
    // Mark as read
    if (!n.is_read) {
      try {
        await fetch(`${API}/mark-read`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ids: [n.id] }),
        });
        setNotifications(prev => prev.map(item => item.id === n.id ? { ...item, is_read: 1 } : item));
        onCountChange?.(-1); // decrement
      } catch (e) { console.error(e); }
    }

    // Navigate based on type
    if (n.link) {
      navigate(n.link);
    } else if (n.type === "anomaly") {
      navigate("/anomalies");
    } else if (n.type === "invoice") {
      navigate("/invoices/sales");
    } else if (n.type === "payment") {
      navigate("/payments");
    }
    onClose();
  };

  const getTypeStyle = (type: string) => TYPE_ICONS[type] || TYPE_ICONS.default;

  const timeAgo = (ts: string) => {
    if (!ts) return "";
    const diff = Date.now() - new Date(ts).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className={`fixed inset-0 bg-black/40 z-[250] transition-opacity duration-200 ${open ? "opacity-100" : "opacity-0 pointer-events-none"}`}
        onClick={onClose}
      />

      {/* Panel */}
      <aside
        className={`fixed top-0 right-0 bottom-0 w-full sm:w-[380px] bg-bg-surface border-l border-border z-[260] flex flex-col transition-transform duration-300 ease-out ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border shrink-0">
          <h2 className="text-lg font-bold font-display text-text-base">Notifications</h2>
          <div className="flex items-center gap-2">
            <button onClick={markAllRead} className="text-xs text-accent hover:underline font-medium">
              Mark all as read
            </button>
            <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-md text-text-muted hover:bg-bg-overlay hover:text-text-base transition-colors" title="Close">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border shrink-0">
          {TABS.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex-1 py-2.5 text-xs font-semibold text-center transition-colors ${
                tab === t.key
                  ? "text-accent border-b-2 border-accent"
                  : "text-text-muted hover:text-text-secondary"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center text-text-muted animate-pulse text-sm">Loading...</div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-4xl mb-3 opacity-30">🔔</div>
              <p className="text-sm font-medium text-text-base">No notifications</p>
              <p className="text-xs text-text-muted mt-1">You're all caught up!</p>
            </div>
          ) : (
            notifications.map(n => {
              const style = getTypeStyle(n.type);
              const isUnread = !n.is_read;
              return (
                <button
                  key={n.id}
                  onClick={() => handleClick(n)}
                  className={`w-full flex items-start gap-3 px-5 py-3.5 border-b border-border text-left transition-colors hover:bg-bg-overlay ${
                    isUnread ? "bg-bg-subtle" : "bg-bg-surface"
                  }`}
                >
                  {/* Unread dot */}
                  <div className="w-2 pt-3 shrink-0">
                    {isUnread && <div className="w-1.5 h-1.5 rounded-full bg-accent" />}
                  </div>

                  {/* Icon */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${style.bg}`}>
                    <span className="text-sm">{style.icon}</span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm leading-snug ${isUnread ? "font-semibold text-text-base" : "font-normal text-text-secondary"}`}>
                      {n.title || n.message || "Notification"}
                    </p>
                    {n.description && (
                      <p className="text-xs text-text-muted mt-0.5 truncate">{n.description}</p>
                    )}
                  </div>

                  {/* Time */}
                  <span className="text-[11px] text-text-muted whitespace-nowrap shrink-0 mt-0.5">
                    {timeAgo(n.created_at)}
                  </span>
                </button>
              );
            })
          )}
        </div>
      </aside>
    </>
  );
}

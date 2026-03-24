import { Card } from '../ui/Card';
import { formatRelativeTime } from '../../utils/format';
import { Link } from 'react-router-dom';
import { FileText, CurrencyInr, Warning, ArrowRight } from '@phosphor-icons/react';
import { Skeleton } from '../ui/Skeleton';
import { useApi } from '../../hooks/useApi';

interface ActivityItem {
  type: 'invoice_created' | 'payment_received' | 'expense_logged' | 'anomaly_detected';
  description: string;
  amount: number | null;
  timestamp: string;
  link_id: string;
  link_type: string;
}

const ICON_MAP = {
  invoice_created: { icon: FileText, color: 'text-accent', bg: 'bg-accent-subtle' },
  payment_received: { icon: CurrencyInr, color: 'text-success', bg: 'bg-success-subtle' },
  expense_logged: { icon: FileText, color: 'text-text-secondary', bg: 'bg-bg-overlay' },
  anomaly_detected: { icon: Warning, color: 'text-danger', bg: 'bg-danger-subtle' },
};

function parseMarkdown(text: string) {
  // Simple bold parser for **text**
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <span key={i} className="font-semibold text-text-primary">{part.slice(2, -2)}</span>;
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}

export function ActivityFeed() {
  const { data, loading } = useApi<ActivityItem[]>('/dashboard/activity?limit=20', {
    pollingIntervalMs: 30000,
  });
  const items = data || [];


  return (
    <Card className="flex flex-col h-full overflow-hidden" padding="none">
      <div className="p-4 border-b border-border font-medium text-[16px]">
        Recent Activity
      </div>
      
      <div className="flex-1 overflow-y-auto style-scrollbar p-2">
        {loading && items.length === 0 ? (
          Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex gap-3 p-3">
              <Skeleton width={32} height={32} className="rounded-full shrink-0" />
              <div className="flex-1 space-y-2">
                <Skeleton height={14} className="w-3/4" />
                <Skeleton height={12} className="w-1/4" />
              </div>
            </div>
          ))
        ) : items.length === 0 ? (
          <div className="p-6 text-center text-text-muted text-[14px]">
            No activity yet. Upload a document or start a conversation with HERMES.
          </div>
        ) : (
          items.map((item, idx) => {
            const Config = ICON_MAP[item.type];
            const Icon = Config?.icon || FileText;
            
            return (
              <Link
                key={idx}
                to={`/${item.link_type}s/${item.link_id}`}
                className="flex items-start gap-4 p-3 hover:bg-bg-overlay rounded-md transition-colors group"
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${Config?.bg || 'bg-bg-overlay'}`}>
                  <Icon size={16} className={Config?.color || 'text-text-secondary'} weight="bold" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="text-[14px] text-text-secondary leading-[1.4] pr-2">
                    {parseMarkdown(item.description)}
                  </div>
                  <div className="text-[12px] text-text-muted mt-1 font-medium">
                    {formatRelativeTime(item.timestamp)}
                  </div>
                </div>
              </Link>
            )
          })
        )}
      </div>

      <div className="p-3 border-t border-border bg-bg-surface">
        <Link to="/audit" className="flex items-center justify-center gap-1 text-[13px] font-medium text-accent hover:text-accent-hover transition-colors">
          View full audit trail <ArrowRight size={14} />
        </Link>
      </div>
    </Card>
  );
}

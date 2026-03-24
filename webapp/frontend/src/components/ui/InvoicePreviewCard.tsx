import { Link } from 'react-router-dom';
import { FileText, ArrowRight } from '@phosphor-icons/react';

interface InvoicePreviewCardProps {
  invoiceId: string;
  type?: 'invoice' | 'bill';
  amount?: string;
  contactName?: string;
}

export function InvoicePreviewCard({ invoiceId, type = 'invoice', amount, contactName }: InvoicePreviewCardProps) {
  const linkPath = type === 'invoice' ? `/sales/invoices/${invoiceId}` : `/purchases/bills/${invoiceId}`;
  
  return (
    <div className="mt-3 bg-bg-screen border border-border rounded-xl p-3 flex items-center justify-between max-w-sm hover:border-accent transition-colors">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-accent-subtle text-accent flex items-center justify-center shrink-0">
          <FileText size={20} weight="fill" />
        </div>
        <div>
          <div className="text-[14px] font-medium text-text-primary">
            {type === 'invoice' ? 'Invoice' : 'Bill'} #{invoiceId}
          </div>
          {(amount || contactName) && (
            <div className="text-[12px] text-text-muted mt-0.5">
              {contactName && <span className="mr-2">{contactName}</span>}
              {amount && <span className="font-medium text-text-secondary">{amount}</span>}
            </div>
          )}
        </div>
      </div>
      <Link to={linkPath} className="w-8 h-8 rounded-full hover:bg-bg-overlay flex items-center justify-center text-text-secondary hover:text-accent transition-colors">
        <ArrowRight size={16} />
      </Link>
    </div>
  );
}

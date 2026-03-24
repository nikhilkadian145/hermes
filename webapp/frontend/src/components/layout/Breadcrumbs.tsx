import { Link, useLocation } from 'react-router-dom';
import { CaretRight } from '@phosphor-icons/react';

export function Breadcrumbs() {
  const location = useLocation();
  const paths = location.pathname.split('/').filter(Boolean);
  
  if (paths.length === 0) return null;

  return (
    <nav className="flex items-center gap-2 mb-2">
      <Link to="/" className="text-[11px] text-text-muted hover:text-text-primary transition-colors uppercase tracking-[0.05em] font-medium">
        Overview
      </Link>
      {paths.map((path, idx) => {
        const routeTo = `/${paths.slice(0, idx + 1).join('/')}`;
        const isLast = idx === paths.length - 1;
        const label = path.charAt(0).toUpperCase() + path.slice(1);
        
        return (
          <div key={path} className="flex items-center gap-2">
            <CaretRight size={10} className="text-text-muted" weight="bold" />
            {isLast ? (
              <span className="text-[11px] font-medium text-text-secondary uppercase tracking-[0.05em]">{label}</span>
            ) : (
              <Link to={routeTo} className="text-[11px] text-text-muted hover:text-text-primary transition-colors uppercase tracking-[0.05em] font-medium">
                {label}
              </Link>
            )}
          </div>
        );
      })}
    </nav>
  );
}

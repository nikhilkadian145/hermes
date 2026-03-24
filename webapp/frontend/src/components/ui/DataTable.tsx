import { ReactNode } from "react";
import { clsx } from "clsx";
import { Button } from "./Button";
import { Skeleton } from "./Skeleton";

export interface ColumnDef<T> {
  key: keyof T | string;
  header: ReactNode;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  render?: (row: T) => ReactNode;
}

export interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  loading?: boolean;
  emptyState?: ReactNode;
  onRowClick?: (row: T) => void;
  selectable?: boolean;
  selectedRows?: Set<string | number>;
  onSelectChange?: (selected: Set<string | number>) => void;
  rowKey?: (row: T) => string | number;
}

export function DataTable<T>({
  columns,
  data,
  loading = false,
  emptyState,
  onRowClick,
  selectable = false,
  selectedRows = new Set(),
  onSelectChange,
  rowKey = (r: any) => r.id
}: DataTableProps<T>) {
  
  const handleSelectAll = () => {
    if (!onSelectChange) return;
    if (selectedRows.size === data.length && data.length > 0) {
      onSelectChange(new Set());
    } else {
      onSelectChange(new Set(data.map(rowKey)));
    }
  };

  const handleSelectOne = (e: React.MouseEvent, key: string | number) => {
    e.stopPropagation();
    if (!onSelectChange) return;
    const newSet = new Set(selectedRows);
    if (newSet.has(key)) newSet.delete(key);
    else newSet.add(key);
    onSelectChange(newSet);
  };

  return (
    <div className="overflow-x-auto w-full">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-bg-subtle">
            {selectable && (
              <th className="sticky left-0 bg-bg-subtle border-b border-border w-[40px] px-4 py-[10px] z-10 text-left">
                <input 
                  type="checkbox" 
                  checked={data.length > 0 && selectedRows.size === data.length}
                  onChange={handleSelectAll}
                  className="accent-accent" 
                />
              </th>
            )}
            {columns.map((col, i) => (
              <th 
                key={col.key as string}
                className={clsx(
                  "sticky top-0 bg-bg-subtle text-[12px] font-medium uppercase tracking-[0.05em] text-text-secondary border-b border-border px-4 py-[10px]",
                  col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left',
                  i === 0 && !selectable ? "left-0 z-10" : "z-0"
                )}
                style={{ width: col.width }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading && data.length === 0 && Array.from({ length: 8 }).map((_, i) => (
            <tr key={`skel-${i}`} className="h-[48px] border-b border-border bg-bg-surface">
              {selectable && <td className="px-4"><Skeleton width={16} height={16} /></td>}
              {columns.map((col, j) => (
                <td key={j} className="px-4">
                  <Skeleton width="80%" height={14} className={col.align === 'right' ? 'ml-auto' : ''} />
                </td>
              ))}
            </tr>
          ))}
          
          {!loading && data.length === 0 && (
            <tr>
              <td colSpan={columns.length + (selectable ? 1 : 0)}>
                {emptyState || (
                  <div className="p-16 text-center text-text-muted flex flex-col items-center">
                    <p className="text-[14px] font-medium">No results found.</p>
                  </div>
                )}
              </td>
            </tr>
          )}

          {data.map((row, i) => {
            const key = rowKey(row);
            const isSelected = selectedRows.has(key);
            return (
              <tr
                key={key}
                onClick={() => onRowClick?.(row)}
                className={clsx(
                  "h-[52px] md:h-[48px] border-b border-border transition-colors duration-75",
                  isSelected ? "bg-accent-subtle border-l-2 border-l-accent" : (i % 2 === 1 ? "bg-bg-subtle" : "bg-bg-surface"),
                  onRowClick && !isSelected && "hover:bg-bg-overlay cursor-pointer"
                )}
              >
                {selectable && (
                  <td className="px-4 sticky left-0 z-0 bg-inherit" onClick={e => e.stopPropagation()}>
                    <input 
                      type="checkbox" 
                      checked={isSelected}
                      onChange={(e) => handleSelectOne(e as any, key)}
                      className="accent-accent"
                    />
                  </td>
                )}
                {columns.map((col, j) => (
                  <td 
                    key={col.key as string} 
                    className={clsx(
                      "px-4 text-[13px]",
                      col.align === 'right' ? 'text-right font-mono' : col.align === 'center' ? 'text-center' : 'text-left',
                      j === 0 && !selectable ? "sticky left-0 bg-inherit z-0" : ""
                    )}
                  >
                    {col.render ? col.render(row) : (row[col.key as keyof T] as ReactNode)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

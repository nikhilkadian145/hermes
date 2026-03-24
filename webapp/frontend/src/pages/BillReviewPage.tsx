import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from '../api/client';
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Badge } from "../components/ui/Badge";

interface ExpenseItem {
  id?: number;
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
  hsn_code: string;
  gst_rate: number;
  cgst_amount: number;
  sgst_amount: number;
  igst_amount: number;
}

interface BillData {
  id: number;
  vendor: string;
  vendor_gstin: string;
  bill_number: string;
  date: string;
  category: string;
  amount: number;
  cgst_amount: number;
  sgst_amount: number;
  igst_amount: number;
  receipt_path: string;
  items: ExpenseItem[];
  upload: {
    status: string;
    filename: string;
  } | null;
}

export function BillReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [bill, setBill] = useState<BillData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form State
  const [vendor, setVendor] = useState("");
  const [gstin, setGstin] = useState("");
  const [billNumber, setBillNumber] = useState("");
  const [date, setDate] = useState("");
  const [category, setCategory] = useState("purchases");
  const [items, setItems] = useState<ExpenseItem[]>([]);
  const [cgst, setCgst] = useState(0);
  const [sgst, setSgst] = useState(0);
  const [igst, setIgst] = useState(0);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    async function fetchBill() {
      try {
        const res = await apiFetch(`/upload/queue/${id}`);
        if (res.ok) {
          const item = await res.json();
          const ocr = item.ocr_result || {};
          
          setBill({
            ...ocr,
            upload: { status: item.status, filename: item.filename, id: item.id }
          } as any);
          
          setVendor(ocr.vendor || "");
          setGstin(ocr.vendor_gstin || ocr.gstin || "");
          setBillNumber(ocr.bill_number || ocr.invoice_number || "");
          setDate(ocr.date || ocr.bill_date || "");
          setCategory(ocr.category || "purchases");
          setItems(ocr.items || []);
          setCgst(ocr.cgst_amount || ocr.cgst || 0);
          setSgst(ocr.sgst_amount || ocr.sgst || 0);
          setIgst(ocr.igst_amount || ocr.igst || 0);
          setTotal(ocr.amount || ocr.total || 0);
        }
      } catch (err) {
        console.error("Failed to load queue item", err);
      } finally {
        setLoading(false);
      }
    }
    fetchBill();
  }, [id]);

  // Derive document URL
  const originalFileUrl = `/api/invoices/purchases/review/${id}/original`;
  
  // Decide if it's an image or PDF based on stored filename or header config
  const filename = bill?.receipt_path || bill?.upload?.filename || "";
  const isImage = /\.(jpg|jpeg|png|webp|gif|tiff)$/i.test(filename);
  
  const handleFinalize = async () => {
    setSaving(true);
    try {
      const payload = {
        vendor,
        vendor_gstin: gstin,
        bill_number: billNumber,
        bill_date: date,
        category,
        amount: total,
        cgst: cgst,
        sgst: sgst,
        igst: igst,
        items
      };
      
      const res = await apiFetch(`/upload/queue/${id}/finalize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        navigate("/invoices/purchases");
      } else {
        alert("Failed to finalize bill.");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred.");
    } finally {
      setSaving(false);
    }
  };

  const handleItemChange = (index: number, field: keyof ExpenseItem, value: any) => {
    const newItems = [...items];
    (newItems[index] as any)[field] = value;
    
    // Auto calculate amount
    if (field === 'quantity' || field === 'unit_price') {
      newItems[index].amount = newItems[index].quantity * newItems[index].unit_price;
    }
    
    setItems(newItems);
  };

  const addItem = () => {
    setItems([...items, {
      description: "",
      quantity: 1,
      unit_price: 0,
      amount: 0,
      hsn_code: "",
      gst_rate: 0,
      cgst_amount: 0,
      sgst_amount: 0,
      igst_amount: 0
    }]);
  };
  
  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };
  
  const recalculateTotals = () => {
    const newCgst = items.reduce((sum, item) => sum + (Number(item.cgst_amount) || 0), 0);
    const newSgst = items.reduce((sum, item) => sum + (Number(item.sgst_amount) || 0), 0);
    const newIgst = items.reduce((sum, item) => sum + (Number(item.igst_amount) || 0), 0);
    const subtotal = items.reduce((sum, item) => sum + (Number(item.amount) || 0), 0);
    
    setCgst(newCgst);
    setSgst(newSgst);
    setIgst(newIgst);
    setTotal(subtotal + newCgst + newSgst + newIgst);
  };

  if (loading) return <div className="p-8 text-text-muted">Loading Bill Data...</div>;
  if (!bill) return <div className="p-8 text-danger">Bill not found</div>;

  return (
    <div className="flex h-full bg-bg-base overflow-hidden relative">
      <div className="absolute top-4 left-4 z-50">
        <Button onClick={() => navigate("/invoices/purchases")} variant="secondary" size="sm" className="bg-bg-surface shadow-sm">
          &larr; Back
        </Button>
      </div>

      {/* Left Panel: Document Viewer (60%) */}
      <div className="w-[60%] h-full border-r border-border bg-bg-surface flex flex-col p-4 pt-16">
        <div className="flex-1 rounded-xl overflow-hidden border border-border bg-[#e5e7eb] flex justify-center items-center shadow-inner relative">
          {isImage ? (
            <img 
              src={originalFileUrl} 
              alt="Original Document" 
              className="max-w-full max-h-full object-contain cursor-zoom-in"
            />
          ) : (
            <object 
              data={originalFileUrl} 
              type="application/pdf" 
              className="w-full h-full"
            >
              <div className="flex flex-col items-center justify-center h-full text-text-muted">
                <p>PDF viewer not available.</p>
                <a href={originalFileUrl} download className="text-accent underline mt-2">Download Document</a>
              </div>
            </object>
          )}
        </div>
      </div>

      {/* Right Panel: Data Extraction & Verification Form (40%) */}
      <div className="w-[40%] h-full flex flex-col pt-16 bg-bg-base overflow-y-auto">
        <div className="px-6 pb-6 flex-1 flex flex-col gap-8">
          
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight text-text-base">Review Details</h2>
              <p className="text-text-muted text-sm mt-1">Verify AI extracted data against document</p>
            </div>
            {bill.upload?.status === 'review' && <Badge status="review" label="NEEDS REVIEW" />}
            {bill.upload?.status === 'finalized' && <Badge status="finalized" />}
          </div>

          {/* Vendor Details */}
          <section className="space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-text-muted border-b border-border pb-2">Vendor Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 relative group">
                 <label className="text-xs font-medium text-text-muted mb-1 block">Vendor Name</label>
                 <Input value={vendor} onChange={e => setVendor(e.target.value)} />
                 <span className="absolute right-3 top-8 w-2 h-2 rounded-full bg-success"></span>
              </div>
              <div className="relative">
                 <label className="text-xs font-medium text-text-muted mb-1 block">GSTIN</label>
                 <Input value={gstin} onChange={e => setGstin(e.target.value)} />
              </div>
              <div className="relative">
                 <label className="text-xs font-medium text-text-muted mb-1 block">Expense Category</label>
                 <select 
                   value={category} 
                   onChange={e => setCategory(e.target.value)}
                   className="w-full h-10 px-3 rounded-lg border border-border bg-bg-surface text-sm text-text-base focus:outline-none focus:ring-2 focus:ring-accent/50 transition-shadow"
                 >
                   <option value="purchases">Purchases (COGS)</option>
                   <option value="software">Software / IT</option>
                   <option value="rent">Rent / Leases</option>
                   <option value="travel">Travel / Meals</option>
                   <option value="other">Other Expenses</option>
                 </select>
              </div>
            </div>
          </section>

          {/* Invoice Details */}
          <section className="space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-text-muted border-b border-border pb-2">Invoice Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="relative">
                 <label className="text-xs font-medium text-text-muted mb-1 block">Invoice Number</label>
                 <Input value={billNumber} onChange={e => setBillNumber(e.target.value)} />
              </div>
              <div className="relative">
                 <label className="text-xs font-medium text-text-muted mb-1 block">Invoice Date</label>
                 <Input type="date" value={date} onChange={e => setDate(e.target.value)} />
              </div>
            </div>
          </section>

          {/* Line Items */}
          <section className="space-y-4 flex-1">
            <div className="flex justify-between items-end border-b border-border pb-2">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-text-muted">Line Items</h3>
              <button onClick={addItem} className="text-xs font-medium text-accent hover:underline">+ Add Row</button>
            </div>
            
            <div className="overflow-x-auto pb-4">
              <div className="min-w-[600px] flex flex-col gap-2">
                <div className="grid grid-cols-12 gap-2 px-2 text-xs font-medium text-text-muted uppercase">
                  <div className="col-span-4">Description</div>
                  <div className="col-span-2">HSN</div>
                  <div className="col-span-1">Qty</div>
                  <div className="col-span-2">Rate</div>
                  <div className="col-span-2 text-right">Amount</div>
                  <div className="col-span-1 text-center"></div>
                </div>

                {items.map((item, i) => (
                  <div key={i} className="grid grid-cols-12 gap-2 items-start bg-bg-surface border border-border p-2 rounded-lg relative group">
                     {/* Confidence Indicator line */}
                     <div className="absolute left-0 top-0 bottom-0 w-1 bg-success rounded-l-lg opacity-50"></div>
                     <div className="col-span-4 pl-1">
                       <Input value={item.description} onChange={e => handleItemChange(i, 'description', e.target.value)} placeholder="Item desc" className="h-8 text-sm px-2" />
                     </div>
                     <div className="col-span-2">
                       <Input value={item.hsn_code || ''} onChange={e => handleItemChange(i, 'hsn_code', e.target.value)} placeholder="HSN" className="h-8 text-sm px-2" />
                     </div>
                     <div className="col-span-1">
                       <Input type="number" value={item.quantity} onChange={e => handleItemChange(i, 'quantity', parseFloat(e.target.value))} className="h-8 text-sm px-2" />
                     </div>
                     <div className="col-span-2">
                       <Input type="number" value={item.unit_price} onChange={e => handleItemChange(i, 'unit_price', parseFloat(e.target.value))} className="h-8 text-sm px-2" />
                     </div>
                     <div className="col-span-2 flex items-center justify-end h-8 px-2 font-mono text-sm bg-bg-subtle rounded text-text-base border border-border whitespace-nowrap overflow-hidden text-ellipsis">
                       ₹{item.amount.toLocaleString()}
                     </div>
                     <div className="col-span-1 flex items-center justify-center h-8">
                       <button onClick={() => removeItem(i)} className="text-text-muted hover:text-danger opacity-0 group-hover:opacity-100 transition-opacity">
                         <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                       </button>
                     </div>
                     
                     {/* Tax sub-row */}
                     <div className="col-span-12 mt-1 flex gap-2 justify-end pr-10 items-center">
                        <span className="text-xs text-text-muted">GST %:</span>
                        <input type="number" className="w-12 h-6 text-xs bg-bg-subtle border border-border rounded px-1" value={item.gst_rate || 0} onChange={e => handleItemChange(i, 'gst_rate', parseFloat(e.target.value))} />
                        
                        <span className="text-xs text-text-muted ml-2">CGST:</span>
                        <input type="number" className="w-16 h-6 text-xs bg-bg-subtle border border-border rounded px-1" value={item.cgst_amount || 0} onChange={e => handleItemChange(i, 'cgst_amount', parseFloat(e.target.value))} />
                        
                        <span className="text-xs text-text-muted ml-2">SGST:</span>
                        <input type="number" className="w-16 h-6 text-xs bg-bg-subtle border border-border rounded px-1" value={item.sgst_amount || 0} onChange={e => handleItemChange(i, 'sgst_amount', parseFloat(e.target.value))} />
                        
                        <span className="text-xs text-text-muted ml-2">IGST:</span>
                        <input type="number" className="w-16 h-6 text-xs bg-bg-subtle border border-border rounded px-1" value={item.igst_amount || 0} onChange={e => handleItemChange(i, 'igst_amount', parseFloat(e.target.value))} />
                     </div>
                  </div>
                ))}
                {items.length === 0 && (
                  <div className="text-center py-4 text-text-muted text-sm border border-dashed border-border rounded-lg">No line items. Add one above.</div>
                )}
              </div>
            </div>
          </section>

          {/* Subtotals & Taxes */}
          <section className="bg-bg-surface p-4 rounded-xl border border-border space-y-2 mt-auto">
            <div className="flex justify-between items-center pb-2 border-b border-border/50">
              <span className="text-sm text-text-muted font-medium">Sub-Totals</span>
              <button onClick={recalculateTotals} className="text-xs text-accent hover:underline flex items-center">
                <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                Calc from Items
              </button>
            </div>
            
            <div className="flex justify-between items-center text-sm">
              <span className="text-text-muted">CGST</span>
              <div className="w-32"><Input type="number" value={cgst} onChange={e => setCgst(parseFloat(e.target.value))} className="h-8 text-right" /></div>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-text-muted">SGST</span>
              <div className="w-32"><Input type="number" value={sgst} onChange={e => setSgst(parseFloat(e.target.value))} className="h-8 text-right" /></div>
            </div>
            <div className="flex justify-between items-center text-sm pb-2 border-b border-border border-dashed">
              <span className="text-text-muted">IGST</span>
              <div className="w-32"><Input type="number" value={igst} onChange={e => setIgst(parseFloat(e.target.value))} className="h-8 text-right" /></div>
            </div>
            <div className="flex justify-between items-center text-lg font-semibold pt-1">
              <span className="text-text-base">Grand Total</span>
              <div className="w-40"><Input type="number" value={total} onChange={e => setTotal(parseFloat(e.target.value))} className="h-10 text-right font-bold text-accent bg-accent-subtle" /></div>
            </div>
          </section>

        </div>

        {/* Floating Actions Footer */}
        <div className="sticky bottom-0 bg-bg-surface border-t border-border p-4 px-6 flex justify-end gap-3 shadow-lg z-10 w-full">
            <Button variant="secondary" onClick={() => navigate("/invoices/purchases")}>
              Discard Changes
            </Button>
            {bill.upload?.status === 'review' && (
              <Button variant="danger" onClick={async () => {
                // simple mark error
                if(bill.upload?.id) {
                    await apiFetch(`/upload/queue/${bill.upload.id}/requeue`, { method: "POST" });
                    navigate("/invoices/purchases");
                }
              }}>
                Reject Document
              </Button>
            )}
            <Button variant="primary" onClick={handleFinalize} disabled={saving}>
              {saving ? "Saving..." : (bill.upload?.status === 'review' ? "Confirm & Finalize" : "Save Changes")}
            </Button>
        </div>
      </div>
    </div>
  );
}

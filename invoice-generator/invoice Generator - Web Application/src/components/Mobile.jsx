import React, { useState, useRef, useEffect, useCallback } from 'react';
import { loadInvoices, loadSettings, saveExpenses, loadExpenses, saveInvoice, bumpCounter, nextInvNum } from '../utils/storage';
import { fc, today, dueDate, isOverdue, calcTotals } from '../utils/helpers';
import { Modal, Toast, Field, SectionTitle } from '../components/UI';

// ════════════════════════════════════════════════════════════════════════════
// CAMERA RECEIPT SCANNER
// ════════════════════════════════════════════════════════════════════════════
export function ReceiptScanner({ settings, onClose, onSaved }) {
  const videoRef    = useRef(null);
  const canvasRef   = useRef(null);
  const streamRef   = useRef(null);
  const fileInputRef= useRef(null);

  const [step,     setStep]     = useState('capture'); // capture | review | edit | done
  const [photo,    setPhoto]    = useState(null);       // base64
  const [scanning, setScanning] = useState(false);
  const [result,   setResult]   = useState(null);       // parsed receipt data
  const [toast,    setToast]    = useState('');
  const [error,    setError]    = useState('');

  // Form state (editable after scan)
  const [desc,    setDesc]    = useState('');
  const [amount,  setAmount]  = useState('');
  const [cat,     setCat]     = useState('General');
  const [date,    setDate]    = useState(today());
  const sym = settings.currency_symbol || '£';

  const CATS = ['General','Software','Travel','Equipment','Marketing','Office','Professional Services','Food & Drink','Other'];

  // Start camera
  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  async function startCamera() {
    setError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch (e) {
      setError(`Camera unavailable: ${e.message}. Use "Choose File" instead.`);
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach(t => t.stop());
  }

  function capturePhoto() {
    const video  = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    canvas.width  = video.videoWidth  || 640;
    canvas.height = video.videoHeight || 480;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
    setPhoto(dataUrl);
    stopCamera();
    setStep('review');
  }

  function handleFileInput(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => {
      setPhoto(ev.target.result);
      stopCamera();
      setStep('review');
    };
    reader.readAsDataURL(file);
  }

  async function analyseReceipt() {
    if (!photo) return;
    setScanning(true);
    try {
      // Call Anthropic API with vision to extract receipt data
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 400,
          messages: [{
            role: 'user',
            content: [
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: 'image/jpeg',
                  data: photo.split(',')[1],
                },
              },
              {
                type: 'text',
                text: 'Extract receipt data. Respond ONLY with valid JSON, no markdown, no explanation:\n{"description":"merchant or item name","amount":0.00,"category":"one of: Food & Drink, Travel, Equipment, Software, Office, Marketing, Professional Services, General","date":"DD/MM/YYYY or empty string"}\nIf amount unclear use 0. Category must be exactly one of those options.'
              }
            ]
          }]
        })
      });

      const data = await response.json();
      const text = data.content?.[0]?.text || '{}';
      const clean = text.replace(/```json|```/g, '').trim();
      const parsed = JSON.parse(clean);

      setDesc(parsed.description   || '');
      setAmount(String(parsed.amount || ''));
      setCat(parsed.category || 'General');
      setDate(parsed.date || today());
      setResult(parsed);
      setStep('edit');
    } catch (e) {
      // Fallback: just go to edit with empty fields
      setStep('edit');
      setToast('Could not read receipt — fill in manually');
    } finally {
      setScanning(false);
    }
  }

  function saveExpense() {
    if (!desc.trim() || !amount) { setToast('⚠️ Fill in description and amount'); return; }
    const expenses = loadExpenses();
    expenses.push({ description: desc.trim(), amount: parseFloat(amount), category: cat, date, receipt: photo });
    saveExpenses(expenses);
    setToast('✅ Expense saved!');
    setTimeout(() => { onSaved && onSaved(); onClose(); }, 1000);
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#000', zIndex: 500, display: 'flex', flexDirection: 'column' }}>
      {/* Top bar */}
      <div style={{ background: 'rgba(0,0,0,0.8)', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12, paddingTop: 'calc(12px + env(safe-area-inset-top))' }}>
        <button onClick={() => { stopCamera(); onClose(); }} style={{ background: 'none', color: '#fff', fontSize: '1rem', fontWeight: 600, border: 'none', cursor: 'pointer' }}>✕</button>
        <span style={{ color: '#fff', fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '1.1rem', flex: 1 }}>
          {step === 'capture' ? '📷 Scan Receipt' : step === 'review' ? 'Review Photo' : step === 'edit' ? '✏️ Confirm Details' : 'Saved'}
        </span>
        {step === 'capture' && (
          <button onClick={() => fileInputRef.current?.click()} style={{ background: 'rgba(255,255,255,0.15)', color: '#fff', border: 'none', borderRadius: 8, padding: '6px 12px', fontSize: '0.82rem', cursor: 'pointer' }}>
            Gallery
          </button>
        )}
      </div>

      <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFileInput} />
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Capture step */}
      {step === 'capture' && (
        <div style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column' }}>
          {error ? (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 24, textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>📁</div>
              <div style={{ color: '#9ca3af', fontSize: '0.87rem', marginBottom: 20, lineHeight: 1.5 }}>{error}</div>
              <button onClick={() => fileInputRef.current?.click()} style={{ background: '#00e676', color: '#000', border: 'none', borderRadius: 10, padding: '12px 28px', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer' }}>
                Choose Photo
              </button>
            </div>
          ) : (
            <>
              <video ref={videoRef} autoPlay playsInline muted style={{ flex: 1, objectFit: 'cover', width: '100%' }} />
              {/* Viewfinder overlay */}
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
                <div style={{ width: '80%', maxWidth: 320, height: 200, border: '2px solid #00e676', borderRadius: 12, boxShadow: '0 0 0 9999px rgba(0,0,0,0.4)' }} />
                <div style={{ color: '#9ca3af', fontSize: '0.78rem', marginTop: 14, textAlign: 'center' }}>Position receipt within the frame</div>
              </div>
              {/* Capture button */}
              <div style={{ padding: '24px 0 calc(24px + env(safe-area-inset-bottom))', display: 'flex', justifyContent: 'center', background: 'rgba(0,0,0,0.6)' }}>
                <button onClick={capturePhoto} style={{
                  width: 72, height: 72, borderRadius: '50%',
                  border: '4px solid #00e676', background: 'rgba(0,230,118,0.2)',
                  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <div style={{ width: 52, height: 52, borderRadius: '50%', background: '#00e676' }} />
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Review step */}
      {step === 'review' && photo && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#111' }}>
            <img src={photo} alt="Receipt" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
          </div>
          <div style={{ padding: '16px 20px calc(16px + env(safe-area-inset-bottom))', background: '#0b0e14', display: 'flex', gap: 12 }}>
            <button onClick={() => { setPhoto(null); setStep('capture'); startCamera(); }}
              style={{ flex: 1, background: '#1a2030', color: '#9ca3af', border: '1px solid #1f2937', borderRadius: 10, padding: '12px', fontWeight: 600, cursor: 'pointer' }}>
              Retake
            </button>
            <button onClick={analyseReceipt} disabled={scanning}
              style={{ flex: 2, background: '#00e676', color: '#000', border: 'none', borderRadius: 10, padding: '12px', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer' }}>
              {scanning ? '🔍 Reading receipt...' : '✨ Scan Receipt'}
            </button>
          </div>
        </div>
      )}

      {/* Edit step */}
      {step === 'edit' && (
        <div style={{ flex: 1, overflowY: 'auto', background: '#0b0e14', padding: '16px 16px calc(20px + env(safe-area-inset-bottom))' }}>
          {result && (
            <div style={{ background: '#0d1a0d', border: '1px solid #00e67640', borderRadius: 10, padding: '10px 14px', marginBottom: 16, fontSize: '0.83rem', color: '#00e676' }}>
              ✨ Receipt scanned — review and confirm details below
            </div>
          )}

          {photo && (
            <div style={{ marginBottom: 16, borderRadius: 10, overflow: 'hidden', maxHeight: 140 }}>
              <img src={photo} alt="Receipt" style={{ width: '100%', objectFit: 'cover' }} />
            </div>
          )}

          <Field label="Description">
            <input value={desc} onChange={e => setDesc(e.target.value)} placeholder="e.g. Screwfix — screws and fixings" />
          </Field>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <Field label={`Amount (${sym})`}>
              <input type="number" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} placeholder="0.00" />
            </Field>
            <Field label="Date">
              <input value={date} onChange={e => setDate(e.target.value)} placeholder="DD/MM/YYYY" />
            </Field>
          </div>
          <Field label="Category">
            <select value={cat} onChange={e => setCat(e.target.value)}>
              {CATS.map(c => <option key={c}>{c}</option>)}
            </select>
          </Field>

          <button onClick={saveExpense} style={{ width: '100%', background: '#00e676', color: '#000', border: 'none', borderRadius: 10, padding: '13px', fontFamily: 'DM Sans, sans-serif', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', marginTop: 8 }}>
            💾 Save Expense
          </button>
        </div>
      )}

      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// SHARE SHEET
// ════════════════════════════════════════════════════════════════════════════
export async function shareInvoicePDF(inv, settings) {
  // Generate PDF blob first
  const { jsPDF } = await import('jspdf');
  await import('jspdf-autotable');

  const doc    = new jsPDF({ unit: 'mm', format: 'a4' });
  const sym    = settings.currency_symbol || '£';
  const accent = settings.theme_accent || '#00e676';
  const fmtM   = n => `${sym}${parseFloat(n || 0).toFixed(2)}`;

  doc.setFillColor(11, 14, 20);
  doc.rect(0, 0, 210, 40, 'F');
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(22);
  doc.setTextColor(0, 230, 118);
  doc.text('INVOICE', 14, 20);
  doc.setFontSize(10);
  doc.setTextColor(200, 200, 200);
  doc.text(inv.number || '', 14, 28);
  doc.setTextColor(150, 150, 150);
  doc.text(`Date: ${inv.date || ''}   Due: ${inv.due_date || ''}`, 14, 34);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.setTextColor(200, 200, 200);
  let ry = 14;
  [settings.company_name, settings.company_address?.split('\n')[0], settings.company_email].filter(Boolean).forEach(l => {
    doc.text(l, 196, ry, { align: 'right' }); ry += 5;
  });

  doc.setFillColor(19, 23, 32);
  doc.rect(0, 42, 210, 24, 'F');
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(7);
  doc.setTextColor(0, 230, 118);
  doc.text('BILL TO', 14, 50);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  doc.setTextColor(232, 234, 240);
  doc.text(inv.client_name || '', 14, 57);
  if (inv.client_address) { doc.setFontSize(8); doc.setTextColor(156, 163, 175); doc.text(inv.client_address.split('\n')[0], 14, 63); }

  const rows = (inv.items || []).filter(i => i.desc || parseFloat(i.price)).map(i => [
    i.desc || '', parseFloat(i.qty || 1).toFixed(0), fmtM(i.price), i.taxable ? `${settings.tax_rate || 20}%` : '0%',
    fmtM((parseFloat(i.qty || 1)) * (parseFloat(i.price || 0))),
  ]);

  doc.autoTable({
    startY: 72, head: [['Description','Qty','Unit Price','Tax','Amount']],
    body: rows,
    styles: { fillColor: [19,23,32], textColor: [200,200,200], fontSize: 9, cellPadding: 4 },
    headStyles: { fillColor: [11,14,20], textColor: [0,230,118], fontStyle: 'bold', fontSize: 8 },
    alternateRowStyles: { fillColor: [26,32,48] },
    columnStyles: { 0: { cellWidth: 'auto' }, 1: { halign: 'center', cellWidth: 14 }, 2: { halign: 'right', cellWidth: 26 }, 3: { halign: 'center', cellWidth: 14 }, 4: { halign: 'right', cellWidth: 26 } },
    margin: { left: 14, right: 14 }, theme: 'plain',
  });

  let ty = doc.lastAutoTable.finalY + 10;
  [['Subtotal', fmtM(inv.subtotal)], [`${settings.tax_label || 'VAT'}`, fmtM(inv.tax)], ['TOTAL DUE', fmtM(inv.total)]].forEach(([l, v], i) => {
    const bold = i === 2;
    if (bold) { doc.setDrawColor(0, 230, 118); doc.line(130, ty - 1, 196, ty - 1); }
    doc.setFont('helvetica', bold ? 'bold' : 'normal');
    doc.setFontSize(bold ? 11 : 9);
    doc.setTextColor(...(bold ? [0, 230, 118] : [156, 163, 175]));
    doc.text(l, 130, ty);
    doc.setTextColor(...(bold ? [0, 230, 118] : [200, 200, 200]));
    doc.text(v, 196, ty, { align: 'right' });
    ty += bold ? 8 : 6;
  });

  if (settings.bank_account) {
    doc.setFont('helvetica', 'bold'); doc.setFontSize(7); doc.setTextColor(0, 230, 118);
    doc.text('PAYMENT DETAILS', 14, ty + 6);
    doc.setFont('helvetica', 'normal'); doc.setFontSize(8); doc.setTextColor(156, 163, 175);
    doc.text(`Bank: ${settings.bank_name || ''}  Sort: ${settings.bank_sort_code || ''}  Account: ${settings.bank_account}`, 14, ty + 12);
  }

  doc.setFont('helvetica', 'normal'); doc.setFontSize(7); doc.setTextColor(75, 85, 99);
  doc.text('Generated with Invoice Generator — letustech.uk', 105, 290, { align: 'center' });

  const filename = `${inv.number}_${(inv.client_name || 'invoice').replace(/\s+/g, '_')}.pdf`;
  const blob = doc.output('blob');

  // Try native share sheet first (mobile)
  if (navigator.share && navigator.canShare) {
    try {
      const file = new File([blob], filename, { type: 'application/pdf' });
      if (navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: `Invoice ${inv.number}`,
          text: `Invoice ${inv.number} for ${inv.client_name} — ${settings.currency_symbol}${parseFloat(inv.total || 0).toFixed(2)}`,
          files: [file],
        });
        return { success: true, method: 'share' };
      }
    } catch (e) {
      if (e.name !== 'AbortError') console.warn('Share failed:', e);
    }
  }

  // Fallback: download
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
  return { success: true, method: 'download' };
}

// ════════════════════════════════════════════════════════════════════════════
// QUICK INVOICE — one screen, 60 seconds
// ════════════════════════════════════════════════════════════════════════════
export function QuickInvoice({ settings, setPage, onSaved }) {
  const clients = (() => { try { return JSON.parse(localStorage.getItem('ig_clients') || '[]'); } catch { return []; } })();
  const sym     = settings.currency_symbol || '£';
  const fmt     = settings.date_format || 'DD/MM/YYYY';

  const [client,  setClient]  = useState('');
  const [email,   setEmail]   = useState('');
  const [desc,    setDesc]    = useState('');
  const [amount,  setAmount]  = useState('');
  const [qty,     setQty]     = useState('1');
  const [tax,     setTax]     = useState(true);
  const [sending, setSending] = useState(false);
  const [toast,   setToast]   = useState('');

  function loadClient(name) {
    const c = clients.find(c => c.name === name);
    if (c) { setClient(c.name); setEmail(c.email || ''); }
  }

  const lineTotal = (parseFloat(qty) || 1) * (parseFloat(amount) || 0);
  const taxAmt    = tax ? lineTotal * ((parseFloat(settings.tax_rate) || 20) / 100) : 0;
  const grandTotal = lineTotal + taxAmt;

  async function sendInvoice() {
    if (!client.trim() || !desc.trim() || !amount) {
      setToast('⚠️ Fill in client, description and amount'); return;
    }
    setSending(true);
    const num = nextInvNum(settings);
    const inv = {
      number: num, status: 'Unpaid',
      date: today(fmt), due_date: dueDate(settings.payment_terms || 30, fmt),
      client_name: client, client_email: email,
      client_address: '', client_phone: '', po: '', discount: '0',
      notes: settings.default_notes?.replace('{terms}', settings.payment_terms) || '',
      items: [{ desc, qty: parseFloat(qty), price: parseFloat(amount), taxable: tax }],
      subtotal: lineTotal, tax: taxAmt, total: grandTotal,
      currency_symbol: sym, invoice_template: 'Professional',
      filepath: '', paid_date: '', last_reminder: '', amount_paid: '0',
    };
    saveInvoice(inv);
    bumpCounter(settings);

    const result = await shareInvoicePDF(inv, settings);
    setSending(false);
    setToast(result.method === 'share' ? '✅ Invoice shared!' : '✅ Invoice saved & downloaded');
    setTimeout(() => { onSaved && onSaved(); setPage('invoices'); }, 1500);
  }

  return (
    <div className="page" style={{ paddingTop: 0 }}>
      <div className="top-bar">
        <button className="back-btn" onClick={() => setPage('dashboard')}>‹ Back</button>
        <div className="top-bar-title">⚡ Quick Invoice</div>
      </div>

      <div style={{ padding: '16px 16px 120px' }}>
        <div style={{ background: '#0d1a0d', border: '1px solid var(--accent)', borderRadius: 10, padding: '10px 14px', marginBottom: 16, fontSize: '0.82rem', color: 'var(--accent)' }}>
          ⚡ Send an invoice in under 60 seconds
        </div>

        {/* Client */}
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header"><div className="card-label">Who are you invoicing?</div></div>
          <div className="card-body">
            {clients.length > 0 && (
              <Field label="Load from address book">
                <select value="" onChange={e => loadClient(e.target.value)}>
                  <option value="">— Quick load —</option>
                  {clients.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
                </select>
              </Field>
            )}
            <Field label="Client Name *">
              <input value={client} onChange={e => setClient(e.target.value)} placeholder="e.g. Tom Connor" autoFocus />
            </Field>
            <Field label="Email (for sharing)">
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="client@email.com" />
            </Field>
          </div>
        </div>

        {/* What for */}
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header"><div className="card-label">What are you charging for?</div></div>
          <div className="card-body">
            <Field label="Description *">
              <input value={desc} onChange={e => setDesc(e.target.value)} placeholder="e.g. Plumbing repair — 3 hours" />
            </Field>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <Field label={`Unit Price (${sym}) *`}>
                <input type="number" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} placeholder="0.00" />
              </Field>
              <Field label="Quantity">
                <input type="number" step="0.5" min="0.5" value={qty} onChange={e => setQty(e.target.value)} />
              </Field>
            </div>
            <label style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0', cursor: 'pointer', fontSize: '0.88rem', color: 'var(--text-med)' }}>
              <input type="checkbox" checked={tax} onChange={e => setTax(e.target.checked)} />
              Add {settings.tax_label || 'VAT'} ({settings.tax_rate || 20}%)
            </label>
          </div>
        </div>

        {/* Live total */}
        {grandTotal > 0 && (
          <div style={{ background: '#0d1a0d', border: '1px solid var(--accent)', borderRadius: 12, padding: '16px 20px', marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: 2 }}>Total to charge</div>
              {tax && <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>{fc(lineTotal, sym)} + {fc(taxAmt, sym)} {settings.tax_label || 'VAT'}</div>}
            </div>
            <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.6rem', color: 'var(--accent)' }}>
              {fc(grandTotal, sym)}
            </div>
          </div>
        )}

        <button onClick={sendInvoice} disabled={sending} style={{
          width: '100%', background: 'var(--accent)', color: '#000',
          border: 'none', borderRadius: 12, padding: '15px',
          fontFamily: 'DM Sans, sans-serif', fontWeight: 700, fontSize: '1rem',
          cursor: sending ? 'default' : 'pointer', opacity: sending ? 0.7 : 1,
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        }}>
          {sending ? '⏳ Generating...' : '📤 Send Invoice'}
        </button>

        <button onClick={() => setPage('new')} style={{
          width: '100%', marginTop: 10, background: 'none',
          border: '1px solid var(--border)', borderRadius: 10, padding: '11px',
          color: 'var(--text-dim)', fontSize: '0.85rem', cursor: 'pointer',
        }}>
          Need more options? → Full invoice form
        </button>
      </div>

      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// PAYMENT STATUS NOTIFICATION BANNER
// ════════════════════════════════════════════════════════════════════════════
export function NotificationBanner({ settings, setPage, setEditInvoice }) {
  const [dismissed, setDismissed] = useState(() => {
    // Only show once per day
    const key = 'ig_banner_dismissed';
    const last = localStorage.getItem(key);
    if (!last) return false;
    const lastDate = new Date(last).toDateString();
    return lastDate === new Date().toDateString();
  });

  const fmt = settings.date_format || 'DD/MM/YYYY';
  const sym = settings.currency_symbol || '£';

  const { overdue, dueSoon } = React.useMemo(() => {
    const invoices = loadInvoices();
    const overdue  = invoices.filter(h =>
      (h.status === 'Unpaid' || h.status === 'Overdue') && isOverdue(h.due_date, fmt)
    );
    // Due within 7 days
    const dueSoon  = invoices.filter(h => {
      if (h.status !== 'Unpaid') return false;
      const d = h.due_date ? new Date(h.due_date.split('/').reverse().join('-')) : null;
      if (!d) return false;
      const days = Math.ceil((d - new Date()) / (1000 * 60 * 60 * 24));
      return days >= 0 && days <= 7;
    });
    return { overdue, dueSoon };
  }, [fmt]);

  function dismiss() {
    localStorage.setItem('ig_banner_dismissed', new Date().toISOString());
    setDismissed(true);
  }

  if (dismissed || (overdue.length === 0 && dueSoon.length === 0)) return null;

  const totalOverdue = overdue.reduce((s, h) => s + (parseFloat(h.total) || 0), 0);

  return (
    <div style={{
      background: overdue.length > 0 ? '#1a0808' : '#0d1a0d',
      border: `1px solid ${overdue.length > 0 ? '#ef444450' : '#00e67650'}`,
      borderRadius: 12, padding: '12px 16px',
      marginBottom: 12, display: 'flex', gap: 12, alignItems: 'flex-start',
    }}>
      <div style={{ fontSize: '1.2rem', marginTop: 1 }}>
        {overdue.length > 0 ? '🔴' : '🟡'}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        {overdue.length > 0 && (
          <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#ef4444', marginBottom: 2 }}>
            {overdue.length} overdue invoice{overdue.length !== 1 ? 's' : ''} — {fc(totalOverdue, sym)} outstanding
          </div>
        )}
        {dueSoon.length > 0 && (
          <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f59e0b', marginBottom: 2 }}>
            {dueSoon.length} invoice{dueSoon.length !== 1 ? 's' : ''} due within 7 days
          </div>
        )}
        <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
          {overdue.length > 0 && (
            <button onClick={() => setPage('reminders')} style={{
              background: '#ef4444', color: '#fff', border: 'none',
              borderRadius: 6, padding: '5px 12px', fontSize: '0.78rem',
              fontWeight: 700, cursor: 'pointer',
            }}>
              View Reminders
            </button>
          )}
          {dueSoon.length > 0 && (
            <button onClick={() => setPage('invoices')} style={{
              background: '#f59e0b22', color: '#f59e0b', border: '1px solid #f59e0b40',
              borderRadius: 6, padding: '5px 12px', fontSize: '0.78rem',
              fontWeight: 600, cursor: 'pointer',
            }}>
              View Invoices
            </button>
          )}
        </div>
      </div>
      <button onClick={dismiss} style={{ background: 'none', color: '#6b7280', border: 'none', fontSize: '1rem', cursor: 'pointer', padding: 0, flexShrink: 0 }}>
        ✕
      </button>
    </div>
  );
}

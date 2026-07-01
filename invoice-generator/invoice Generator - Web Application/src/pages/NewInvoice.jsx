import React, { useState, useEffect } from 'react';
import { loadClients, loadInvoices, saveInvoice, bumpCounter, nextInvNum } from '../utils/storage';
import { fc, today, dueDate, calcTotals } from '../utils/helpers';
import { Field, Input, Select, Textarea, Modal, Toast } from '../components/UI';
import { InvoicePreview, PartialPaymentModal } from './Features';
import { EmailModal } from '../components/Email';

const blankItem = () => ({ id: Date.now() + Math.random(), desc: '', qty: 1, price: '', taxable: true });

export default function NewInvoice({ settings, setPage, prefill, onSaved }) {
  const clients = loadClients();
  const sym     = settings.currency_symbol || '£';
  const fmt     = settings.date_format || 'DD/MM/YYYY';

  const [number,   setNumber]   = useState(prefill?.number || nextInvNum(settings));
  const [status,   setStatus]   = useState(prefill?.status || 'Unpaid');
  const [invDate,  setInvDate]  = useState(prefill?.date || today(fmt));
  const [dueD,     setDueD]     = useState(prefill?.due_date || dueDate(settings.payment_terms, fmt));
  const [client,   setClient]   = useState(prefill?.client_name || '');
  const [email,    setEmail]    = useState(prefill?.client_email || '');
  const [phone,    setPhone]    = useState(prefill?.client_phone || '');
  const [address,  setAddress]  = useState(prefill?.client_address || '');
  const [po,       setPo]       = useState(prefill?.po || '');
  const [discount, setDiscount] = useState(prefill?.discount || '0');
  const [notes,    setNotes]    = useState(prefill?.notes || settings.default_notes?.replace('{terms}', settings.payment_terms) || '');
  const [items,    setItems]    = useState(prefill?.items?.length
    ? prefill.items.map(i => ({
        id:       Date.now() + Math.random(),
        desc:     i.desc || i.description || '',   // handle both PWA and desktop app field names
        qty:      i.qty  !== undefined ? i.qty  : 1,
        price:    i.price !== undefined ? i.price : (i.unit_price || ''),
        taxable:  i.taxable !== undefined ? i.taxable : true,
      }))
    : [blankItem(), blankItem()]);

  const [clientModal, setClientModal] = useState(false);
  const [toast,       setToast]       = useState('');
  const [saving,      setSaving]      = useState(false);
  const [preview,     setPreview]     = useState(false);
  const [emailModal,  setEmailModal]  = useState(false);
  const [partialModal,setPartialModal] = useState(false);
  const [amountPaid,  setAmountPaid]   = useState(prefill?.amount_paid || '0');

  const isEdit = !!prefill;

  // Load client from address book
  function loadClientFromBook(name) {
    const c = clients.find(c => c.name === name);
    if (!c) return;
    setClient(c.name);
    setEmail(c.email || '');
    setPhone(c.phone || '');
    setAddress(c.address || '');
  }

  // Line item helpers
  function updateItem(id, field, val) {
    setItems(items.map(i => i.id === id ? { ...i, [field]: val } : i));
  }
  function removeItem(id) { setItems(items.filter(i => i.id !== id)); }
  function addItem() { setItems([...items, blankItem()]); }

  // Totals
  const { subtotal, tax, discount: discAmt, grand } = calcTotals(
    items.map(i => ({ qty: i.qty, price: i.price, taxable: i.taxable })),
    parseFloat(settings.tax_rate) || 20,
    parseFloat(discount) || 0
  );

  function collect() {
    return {
      number, status, date: invDate, due_date: dueD,
      client_name: client, client_email: email,
      client_phone: phone, client_address: address,
      po, discount, notes,
      items: items.filter(i => i.desc || parseFloat(i.price)),
      total: grand,
      subtotal, tax,
      currency_symbol: sym,
      invoice_template: settings.invoice_template || 'Professional',
      filepath: prefill?.filepath || '',
      paid_date: prefill?.paid_date || '',
      amount_paid: amountPaid,
      last_reminder: prefill?.last_reminder || '',
    };
  }

  function saveDraft() {
    if (!client.trim()) { setToast('⚠️ Enter a client name'); return; }
    const inv = collect();
    // Check duplicate
    const existing = loadInvoices().find(h => h.number === number);
    if (existing && !isEdit) {
      if (!window.confirm(`Invoice ${number} already exists (${existing.client_name}). Replace it?`)) return;
    }
    saveInvoice({ ...inv, status: isEdit ? inv.status : 'Draft' });
    if (!isEdit) bumpCounter(settings);
    setToast(`✅ ${isEdit ? 'Updated' : 'Saved as draft'}`);
    setTimeout(() => { onSaved && onSaved(); setPage('invoices'); }, 1000);
  }

  function exportInvoice() {
    if (!client.trim()) { setToast('⚠️ Enter a client name'); return; }
    setSaving(true);
    const inv = collect();
    const existing = loadInvoices().find(h => h.number === number);
    if (existing && !isEdit) {
      if (!window.confirm(`Invoice ${number} already exists. Replace it?`)) { setSaving(false); return; }
    }
    saveInvoice(inv);
    if (!isEdit) bumpCounter(settings);
    generatePDF(inv, settings);
    setToast('✅ PDF downloaded');
    setTimeout(() => { setSaving(false); onSaved && onSaved(); setPage('invoices'); }, 1200);
  }

  return (
    <div className="page" style={{ paddingTop: 0 }}>
      {/* Top bar */}
      <div className="top-bar">
        <button className="back-btn" onClick={() => setPage(isEdit ? 'invoices' : 'invoices')}>
          ‹ {isEdit ? 'Cancel' : 'Cancel'}
        </button>
        <div className="top-bar-title">{isEdit ? `Edit ${number}` : 'New Invoice'}</div>
        <button className="btn btn-ghost btn-sm" onClick={() => setEmailModal(true)} style={{ marginRight: 6 }}>📧</button>
        <button className="btn btn-primary btn-sm" onClick={exportInvoice} disabled={saving}>
          {saving ? '…' : '⬇ PDF'}
        </button>
      </div>

      <div style={{ padding: '16px 16px 120px' }}>
        {/* Invoice meta */}
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header"><div className="card-label">Invoice Details</div></div>
          <div className="card-body">
            <div className="field-row">
              <Field label="Invoice #">
                <input value={number} onChange={e => setNumber(e.target.value)} />
              </Field>
              <Field label="Status">
                <select value={status} onChange={e => setStatus(e.target.value)}>
                  {['Draft','Unpaid','Paid','Overdue'].map(s => <option key={s}>{s}</option>)}
                </select>
              </Field>
            </div>
            <div className="field-row">
              <Field label="Invoice Date">
                <input type="text" value={invDate} onChange={e => setInvDate(e.target.value)} placeholder="DD/MM/YYYY" />
              </Field>
              <Field label="Due Date">
                <input type="text" value={dueD} onChange={e => setDueD(e.target.value)} placeholder="DD/MM/YYYY" />
              </Field>
            </div>
            <Field label="PO / Reference">
              <input value={po} onChange={e => setPo(e.target.value)} placeholder="Optional" />
            </Field>
          </div>
        </div>

        {/* Client details */}
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div className="card-label">Client Details</div>
            {clients.length > 0 && (
              <button className="btn btn-ghost btn-sm" onClick={() => setClientModal(true)}>
                Load ›
              </button>
            )}
          </div>
          <div className="card-body">
            <Field label="Client / Company Name">
              <input value={client} onChange={e => setClient(e.target.value)} placeholder="e.g. Acme Ltd" />
            </Field>
            <div className="field-row">
              <Field label="Email">
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="client@email.com" />
              </Field>
              <Field label="Phone">
                <input type="tel" value={phone} onChange={e => setPhone(e.target.value)} placeholder="07700 000000" />
              </Field>
            </div>
            <Field label="Billing Address">
              <textarea rows={2} value={address} onChange={e => setAddress(e.target.value)} placeholder="1 High Street&#10;Liverpool, L1 1AA" />
            </Field>
          </div>
        </div>

        {/* Line items */}
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div className="card-label">Line Items</div>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent)' }}>
              Total: {fc(grand, sym)}
            </span>
          </div>
          <div className="card-body" style={{ padding: '8px 16px' }}>
            {/* Header */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 70px 80px 60px 24px', gap: 6, padding: '4px 0 8px' }}>
              {['Description','Qty','Price','Tax',''].map(h => (
                <span key={h} style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</span>
              ))}
            </div>
            {items.map(item => (
              <div key={item.id} style={{ display: 'grid', gridTemplateColumns: '1fr 70px 80px 60px 24px', gap: 6, marginBottom: 8, alignItems: 'center' }}>
                <input
                  style={{ background: 'var(--bg-hover)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', padding: '7px 8px', fontSize: '0.85rem', width: '100%' }}
                  placeholder="Description"
                  value={item.desc}
                  onChange={e => updateItem(item.id, 'desc', e.target.value)}
                />
                <input
                  style={{ background: 'var(--bg-hover)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', padding: '7px 6px', fontSize: '0.85rem', width: '100%', textAlign: 'center' }}
                  type="number" min="0" step="0.01"
                  value={item.qty}
                  onChange={e => updateItem(item.id, 'qty', e.target.value)}
                />
                <input
                  style={{ background: 'var(--bg-hover)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', padding: '7px 6px', fontSize: '0.85rem', width: '100%', textAlign: 'right' }}
                  type="number" min="0" step="0.01"
                  placeholder="0.00"
                  value={item.price}
                  onChange={e => updateItem(item.id, 'price', e.target.value)}
                />
                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 3, fontSize: '0.75rem', color: 'var(--text-dim)', cursor: 'pointer' }}>
                  <input type="checkbox" checked={item.taxable} onChange={e => updateItem(item.id, 'taxable', e.target.checked)} />
                  {settings.tax_label || 'VAT'}
                </label>
                <button onClick={() => removeItem(item.id)} style={{ background: 'none', color: 'var(--text-dim)', fontSize: '1rem', padding: 0, cursor: 'pointer' }}>✕</button>
              </div>
            ))}
            <button className="btn btn-ghost btn-sm" style={{ marginTop: 4 }} onClick={addItem}>＋ Add Line</button>
          </div>

          {/* Totals */}
          <div style={{ padding: '0 16px 16px' }}>
            <div className="divider" />
            <div className="field-row" style={{ marginBottom: 8 }}>
              <Field label="Discount %">
                <input type="number" min="0" max="100" value={discount} onChange={e => setDiscount(e.target.value)} />
              </Field>
              <div />
            </div>
            <div className="totals-block">
              <div className="total-row"><span>Subtotal</span><span>{fc(subtotal, sym)}</span></div>
              {discAmt > 0 && <div className="total-row"><span>Discount</span><span>-{fc(discAmt, sym)}</span></div>}
              <div className="total-row"><span>{settings.tax_label || 'VAT'} ({settings.tax_rate || 20}%)</span><span>{fc(tax, sym)}</span></div>
              <div className="total-row grand">
                <span>Total Due</span>
                <span className="total-amount">{fc(grand, sym)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header"><div className="card-label">Notes & Terms</div></div>
          <div className="card-body">
            <Textarea rows={3} value={notes} onChange={e => setNotes(e.target.value)} placeholder="Thank you for your business." />
          </div>
        </div>

        {/* Partial payment row */}
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="card-label">Partial Payment</div>
            {parseFloat(amountPaid) > 0 && (
              <span style={{ fontSize: '0.8rem', color: 'var(--gold)', fontWeight: 600 }}>
                Paid: {fc(parseFloat(amountPaid), sym)} · Balance: {fc(Math.max(0, grand - parseFloat(amountPaid)), sym)}
              </span>
            )}
          </div>
          <div className="card-body" style={{ paddingTop: 8 }}>
            <button className="btn btn-ghost btn-sm" onClick={() => setPartialModal(true)}>
              💛 Record Payment
            </button>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
          <button className="btn btn-ghost" style={{ flex: 1 }} onClick={saveDraft}>
            💾 {isEdit ? 'Save' : 'Save Draft'}
          </button>
          <button className="btn btn-primary" style={{ flex: 2 }} onClick={exportInvoice}>
            ⬇ Export PDF
          </button>
        </div>
      </div>

      {preview && (
        <InvoicePreview
          inv={{ ...collect(), subtotal, tax, total: grand }}
          settings={settings}
          onClose={() => setPreview(false)}
          onExport={() => { setPreview(false); exportInvoice(); }}
        />
      )}

      {partialModal && (
        <PartialPaymentModal
          inv={{ ...collect(), total: grand, amount_paid: amountPaid }}
          settings={settings}
          onSave={amt => {
            setAmountPaid(String(amt));
            setPartialModal(false);
          }}
          onClose={() => setPartialModal(false)}
        />
      )}

      {emailModal && (
        <EmailModal
          inv={{ ...collect(), subtotal, tax, total: grand }}
          settings={settings}
          onClose={() => setEmailModal(false)}
          onSent={(dest) => { setEmailModal(false); if (dest === 'settings') setPage('settings'); }}
        />
      )}

      {/* Client picker modal */}
      {clientModal && (
        <Modal title="Load Client" onClose={() => setClientModal(false)}>
          {clients.map(c => (
            <div key={c.name} className="action-row" onClick={() => { loadClientFromBook(c.name); setClientModal(false); }}>
              <div className="action-row-icon">👤</div>
              <div className="action-row-text">
                <div className="action-row-label">{c.name}</div>
                <div className="action-row-sub">{c.email}</div>
              </div>
            </div>
          ))}
        </Modal>
      )}

      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

// ── jsPDF generation ──────────────────────────────────────────────────────
function generatePDF(inv, settings) {
  import('jspdf').then(({ jsPDF }) => {
    import('jspdf-autotable').then(() => {
      const doc = new jsPDF({ unit: 'mm', format: 'a4' });
      const sym = settings.currency_symbol || '£';
      const accent = settings.theme_accent || '#00e676';

      const fmtMoney = n => `${sym}${parseFloat(n || 0).toFixed(2)}`;

      // Header
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

      // Company info right
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(200, 200, 200);
      const co = [
        settings.company_name,
        settings.company_address,
        settings.company_email,
        settings.vat_number ? `VAT: ${settings.vat_number}` : null,
      ].filter(Boolean);
      let ry = 14;
      co.forEach(line => {
        line.split('\n').forEach(l => {
          doc.text(l, 196, ry, { align: 'right' });
          ry += 5;
        });
      });

      // Client box
      doc.setFillColor(19, 23, 32);
      doc.rect(0, 42, 210, 28, 'F');
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(7);
      doc.setTextColor(0, 230, 118);
      doc.text('BILL TO', 14, 50);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      doc.setTextColor(232, 234, 240);
      doc.text(inv.client_name || '', 14, 57);
      doc.setFontSize(8);
      doc.setTextColor(156, 163, 175);
      if (inv.client_address) doc.text(inv.client_address.split('\n')[0], 14, 63);

      // Line items table
      const rows = (inv.items || []).filter(i => i.desc || parseFloat(i.price)).map(i => [
        i.desc || '',
        parseFloat(i.qty || 1).toFixed(0),
        fmtMoney(i.price),
        i.taxable ? `${settings.tax_rate || 20}%` : '0%',
        fmtMoney((parseFloat(i.qty || 1)) * (parseFloat(i.price || 0))),
      ]);

      doc.autoTable({
        startY: 76,
        head: [['Description', 'Qty', 'Unit Price', 'Tax', 'Amount']],
        body: rows,
        styles: { fillColor: [19,23,32], textColor: [200,200,200], fontSize: 9, cellPadding: 4 },
        headStyles: { fillColor: [11,14,20], textColor: [0,230,118], fontStyle: 'bold', fontSize: 8 },
        alternateRowStyles: { fillColor: [26,32,48] },
        columnStyles: { 0: { cellWidth: 'auto' }, 1: { halign: 'center', cellWidth: 16 }, 2: { halign: 'right', cellWidth: 26 }, 3: { halign: 'center', cellWidth: 16 }, 4: { halign: 'right', cellWidth: 26 } },
        margin: { left: 14, right: 14 },
        theme: 'plain',
      });

      const y = doc.lastAutoTable.finalY + 8;

      // Totals
      const totals = [
        ['Subtotal', fmtMoney(inv.subtotal)],
        [`${settings.tax_label || 'VAT'} (${settings.tax_rate || 20}%)`, fmtMoney(inv.tax)],
        ['TOTAL DUE', fmtMoney(inv.total)],
      ];
      let ty = y;
      totals.forEach(([label, val], i) => {
        const isBold = i === totals.length - 1;
        if (isBold) {
          doc.setDrawColor(0, 230, 118);
          doc.line(130, ty - 1, 196, ty - 1);
        }
        doc.setFont('helvetica', isBold ? 'bold' : 'normal');
        doc.setFontSize(isBold ? 11 : 9);
        doc.setTextColor(isBold ? 0 : 156, isBold ? 230 : 163, isBold ? 118 : 175);
        if (!isBold) doc.setTextColor(156, 163, 175);
        doc.text(label, 130, ty);
        doc.setTextColor(isBold ? 0 : 200, isBold ? 230 : 200, isBold ? 118 : 200);
        doc.text(val, 196, ty, { align: 'right' });
        ty += isBold ? 8 : 6;
      });

      // Bank details
      if (settings.bank_account) {
        const by = ty + 6;
        doc.setFont('helvetica', 'bold'); doc.setFontSize(8); doc.setTextColor(0, 230, 118);
        doc.text('PAYMENT DETAILS', 14, by);
        doc.setFont('helvetica', 'normal'); doc.setFontSize(8); doc.setTextColor(156, 163, 175);
        doc.text(`Bank: ${settings.bank_name || ''}   Sort: ${settings.bank_sort_code || ''}   Account: ${settings.bank_account}`, 14, by + 5);
      }

      // Notes
      if (inv.notes) {
        const ny = ty + 20;
        doc.setFont('helvetica', 'normal'); doc.setFontSize(8); doc.setTextColor(107, 114, 128);
        doc.text(inv.notes, 14, ny, { maxWidth: 180 });
      }

      // Footer
      doc.setFont('helvetica', 'normal'); doc.setFontSize(7); doc.setTextColor(75, 85, 99);
      doc.text('Generated with Invoice Generator — letustech.uk', 105, 290, { align: 'center' });

      const filename = `${inv.number}_${(inv.client_name || 'invoice').replace(/\s+/g, '_')}.pdf`;
      doc.save(filename);
    });
  });
}

import React, { useState, useMemo, useRef, useEffect } from 'react';
import {
  loadInvoices, saveInvoices, saveInvoice, bumpCounter, nextInvNum,
  loadClients, loadExpenses, loadSettings, loadRecurring, saveRecurring,
} from '../utils/storage';
import {
  fc, today, dueDate, formatDate, parseDate, isOverdue,
  statusColor, statusBg, calcTotals, daysBetween,
} from '../utils/helpers';
import { StatusBadge, Modal, Confirm, Toast, EmptyState, Field, SectionTitle, ActionRow } from '../components/UI';

// ════════════════════════════════════════════════════════════════════════════
// 1. OVERDUE REMINDERS
// ════════════════════════════════════════════════════════════════════════════
export function Reminders({ settings, setPage, setEditInvoice }) {
  const sym  = settings.currency_symbol || '£';
  const fmt  = settings.date_format || 'DD/MM/YYYY';
  const [toast, setToast] = useState('');

  const overdue = useMemo(() => {
    return loadInvoices()
      .filter(h => h.status === 'Unpaid' || h.status === 'Overdue')
      .filter(h => isOverdue(h.due_date, fmt))
      .map(h => ({
        ...h,
        daysOver: daysBetween(h.due_date, today(fmt), fmt) || 0,
      }))
      .sort((a, b) => b.daysOver - a.daysOver);
  }, [fmt]);

  function copyReminder(inv) {
    const text =
      `Hi ${inv.client_name},\n\n` +
      `This is a friendly reminder that invoice ${inv.number} for ${fc(inv.total, sym)} ` +
      `was due on ${inv.due_date} and is now ${inv.daysOver} days overdue.\n\n` +
      `Please arrange payment at your earliest convenience.\n\n` +
      `Kind regards,\n${settings.company_name || 'Your business'}`;
    navigator.clipboard?.writeText(text).then(() => setToast('📋 Copied to clipboard'));
  }

  function markPaid(inv) {
    const list = loadInvoices().map(h =>
      h.number === inv.number ? { ...h, status: 'Paid', paid_date: today(fmt) } : h
    );
    saveInvoices(list);
    setToast('✅ Marked as paid');
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Reminders</h1>
          <div className="page-subtitle">Chase overdue invoices</div>
        </div>
        {overdue.length > 0 && (
          <span style={{ background: 'var(--red)', color: '#fff', borderRadius: 20, padding: '3px 10px', fontSize: '0.8rem', fontWeight: 700 }}>
            {overdue.length}
          </span>
        )}
      </div>

      {overdue.length === 0 ? (
        <EmptyState icon="✅" title="All clear!" message="No overdue invoices right now. Stay on top of payments and this page stays empty." />
      ) : (
        <>
          <div className="card" style={{ marginBottom: 12, background: '#1a0808', borderColor: '#ef444440' }}>
            <div style={{ padding: '12px 16px', fontSize: '0.85rem', color: '#ef4444' }}>
              ⚠️ {overdue.length} overdue invoice{overdue.length !== 1 ? 's' : ''} — total {fc(overdue.reduce((s, h) => s + (parseFloat(h.total) || 0), 0), sym)} outstanding
            </div>
          </div>

          {overdue.map(inv => (
            <div key={inv.number} className="card" style={{ marginBottom: 10 }}>
              <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem' }}>{inv.number}</div>
                    <div style={{ color: 'var(--text-med)', fontSize: '0.85rem', marginTop: 2 }}>{inv.client_name}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, color: 'var(--red)' }}>{fc(inv.total, sym)}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--red)', marginTop: 2 }}>{inv.daysOver}d overdue</div>
                  </div>
                </div>
                <div style={{ marginTop: 8, fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                  Due: {inv.due_date} · {inv.client_email || 'No email on file'}
                </div>
              </div>
              <div style={{ padding: '10px 16px', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {inv.client_email && (
                  <a href={`mailto:${inv.client_email}?subject=Payment%20Reminder%20—%20Invoice%20${inv.number}&body=Hi%20${encodeURIComponent(inv.client_name)}%2C%0A%0AThis%20is%20a%20reminder%20that%20invoice%20${inv.number}%20for%20${fc(inv.total, sym)}%20was%20due%20on%20${inv.due_date}.%0A%0APlease%20arrange%20payment%20at%20your%20earliest%20convenience.%0A%0AKind%20regards%2C%0A${encodeURIComponent(settings.company_name || '')}`}
                    className="btn btn-primary btn-sm" style={{ textDecoration: 'none' }}>
                    📧 Email
                  </a>
                )}
                <button className="btn btn-ghost btn-sm" onClick={() => copyReminder(inv)}>📋 Copy Message</button>
                <button className="btn btn-ghost btn-sm" onClick={() => markPaid(inv)}>✓ Mark Paid</button>
                <button className="btn btn-ghost btn-sm" onClick={() => { setEditInvoice(inv); setPage('new'); }}>✏️ Edit</button>
              </div>
            </div>
          ))}
        </>
      )}
      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// 2. RECURRING INVOICES
// ════════════════════════════════════════════════════════════════════════════
export function Recurring({ settings, setPage }) {
  const [schedules, setSchedules] = useState(loadRecurring);
  const [showAdd,   setShowAdd]   = useState(false);
  const [toast,     setToast]     = useState('');
  const fmt = settings.date_format || 'DD/MM/YYYY';
  const sym = settings.currency_symbol || '£';

  const due = useMemo(() => schedules.filter(s => {
    if (!s.next_date) return false;
    const d = parseDate(s.next_date, fmt);
    return d && d <= new Date();
  }), [schedules, fmt]);

  function generateDrafts() {
    let count = 0;
    const updated = schedules.map(s => {
      if (!s.next_date) return s;
      const d = parseDate(s.next_date, fmt);
      if (!d || d > new Date()) return s;
      const num = nextInvNum(settings);
      saveInvoice({
        number: num, status: 'Draft', date: today(fmt),
        due_date: dueDate(settings.payment_terms || 30, fmt),
        client_name: s.client, client_email: s.email,
        client_address: s.address, po: '', discount: '0',
        notes: settings.default_notes?.replace('{terms}', settings.payment_terms) || '',
        items: [{ desc: s.description, qty: 1, price: s.amount, taxable: true }],
        total: parseFloat(s.amount) * (1 + (parseFloat(settings.tax_rate) || 20) / 100),
        currency_symbol: sym, invoice_template: 'Professional',
        filepath: '', paid_date: '', last_reminder: '',
      });
      bumpCounter(settings);
      count++;
      // Advance next_date
      const next = new Date(d);
      if (s.frequency === 'Weekly')      next.setDate(next.getDate() + 7);
      else if (s.frequency === 'Monthly')   next.setMonth(next.getMonth() + 1);
      else if (s.frequency === 'Quarterly') next.setMonth(next.getMonth() + 3);
      else if (s.frequency === 'Annually')  next.setFullYear(next.getFullYear() + 1);
      return { ...s, next_date: formatDate(next, fmt) };
    });
    saveRecurring(updated);
    setSchedules(updated);
    setToast(`✅ Generated ${count} draft${count !== 1 ? 's' : ''}`);
    setTimeout(() => setPage('invoices'), 1500);
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Recurring</h1>
          <div className="page-subtitle">Retainers & regular clients</div>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowAdd(true)}>＋</button>
      </div>

      {due.length > 0 && (
        <div className="card" style={{ marginBottom: 12, background: '#0d1a0d', borderColor: 'var(--accent)' }}>
          <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 700, color: 'var(--accent)', fontSize: '0.9rem' }}>⚡ {due.length} invoice{due.length !== 1 ? 's' : ''} due</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: 2 }}>Ready to generate as drafts</div>
            </div>
            <button className="btn btn-primary btn-sm" onClick={generateDrafts}>Generate</button>
          </div>
        </div>
      )}

      {schedules.length === 0
        ? <EmptyState icon="🔁" title="No schedules" message="Set up recurring schedules for regular clients — retainers, maintenance contracts, subscriptions." action={() => setShowAdd(true)} actionLabel="Add Schedule" />
        : <div className="card">
            {schedules.map((s, i) => (
              <div key={i} className="inv-row">
                <div className="inv-row-left">
                  <div className="inv-row-num">{s.client}</div>
                  <div className="inv-row-client">{s.frequency} · {s.description}</div>
                </div>
                <div className="inv-row-right">
                  <div style={{ fontWeight: 700, color: 'var(--accent)', fontSize: '0.9rem' }}>{fc(s.amount, sym)}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: 2 }}>Next: {s.next_date}</div>
                </div>
              </div>
            ))}
          </div>
      }

      {showAdd && (
        <AddRecurringModal settings={settings}
          onSave={s => { const list = [...schedules, s]; saveRecurring(list); setSchedules(list); setShowAdd(false); setToast('✅ Schedule added'); }}
          onClose={() => setShowAdd(false)}
        />
      )}
      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

function AddRecurringModal({ settings, onSave, onClose }) {
  const fmt = settings.date_format || 'DD/MM/YYYY';
  const clients = loadClients();
  const [client, setClient] = useState('');
  const [desc,   setDesc]   = useState('');
  const [amount, setAmount] = useState('');
  const [freq,   setFreq]   = useState('Monthly');
  const [start,  setStart]  = useState(today(fmt));
  return (
    <Modal title="Add Recurring Schedule" onClose={onClose}
      actions={<>
        <button className="btn btn-ghost" style={{ flex: 1 }} onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => {
          if (!client || !amount) return;
          const c = clients.find(x => x.name === client) || {};
          onSave({ client, email: c.email || '', address: c.address || '', description: desc, amount: parseFloat(amount), frequency: freq, next_date: start, active: true });
        }}>Save</button>
      </>}>
      <Field label="Client">
        {clients.length > 0
          ? <select value={client} onChange={e => setClient(e.target.value)}>
              <option value="">— Select client —</option>
              {clients.map(c => <option key={c.name}>{c.name}</option>)}
            </select>
          : <input value={client} onChange={e => setClient(e.target.value)} placeholder="Client name" />
        }
      </Field>
      <Field label="Description"><input value={desc} onChange={e => setDesc(e.target.value)} placeholder="e.g. Monthly retainer" /></Field>
      <div className="field-row">
        <Field label="Amount"><input type="number" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} placeholder="0.00" /></Field>
        <Field label="Frequency">
          <select value={freq} onChange={e => setFreq(e.target.value)}>
            {['Weekly','Monthly','Quarterly','Annually'].map(f => <option key={f}>{f}</option>)}
          </select>
        </Field>
      </div>
      <Field label="First Due Date"><input value={start} onChange={e => setStart(e.target.value)} placeholder="DD/MM/YYYY" /></Field>
    </Modal>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// 3. CLIENT DETAIL / PAYMENT HISTORY
// ════════════════════════════════════════════════════════════════════════════
export function ClientDetail({ client, settings, setPage, setEditInvoice }) {
  const sym      = settings.currency_symbol || '£';
  const fmt      = settings.date_format || 'DD/MM/YYYY';
  const invoices = loadInvoices().filter(h =>
    (h.client_name || '').toLowerCase() === client.name.toLowerCase()
  );
  const paid   = invoices.filter(h => h.status === 'Paid');
  const unpaid = invoices.filter(h => h.status !== 'Paid' && h.status !== 'Draft');
  const total  = invoices.reduce((s, h) => s + (parseFloat(h.total) || 0), 0);
  const outstanding = unpaid.reduce((s, h) => s + (parseFloat(h.total) || 0), 0);
  const avgDays = (() => {
    const deltas = paid.filter(h => h.paid_date && h.date).map(h => daysBetween(h.date, h.paid_date, fmt)).filter(d => d > 0);
    return deltas.length ? Math.round(deltas.reduce((a, b) => a + b, 0) / deltas.length) : null;
  })();

  return (
    <div className="page" style={{ paddingTop: 0 }}>
      <div className="top-bar">
        <button className="back-btn" onClick={() => setPage('clients')}>‹ Clients</button>
        <div className="top-bar-title">{client.name}</div>
        <button className="btn btn-primary btn-sm" onClick={() => { setEditInvoice({ client_name: client.name, client_email: client.email, client_phone: client.phone, client_address: client.address }); setPage('new'); }}>＋ Invoice</button>
      </div>
      <div style={{ padding: '16px 16px 120px' }}>
        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, marginBottom: 16 }}>
          {[
            { label: 'Total Billed', value: fc(total, sym), color: 'var(--text)' },
            { label: 'Outstanding', value: fc(outstanding, sym), color: outstanding > 0 ? 'var(--gold)' : 'var(--text-dim)' },
            { label: 'Avg Days', value: avgDays !== null ? `${avgDays}d` : '—', color: avgDays === null ? 'var(--text-dim)' : avgDays <= 14 ? 'var(--accent)' : avgDays <= 30 ? 'var(--gold)' : 'var(--red)' },
          ].map(s => (
            <div key={s.label} className="stat-card">
              <div className="stat-label">{s.label}</div>
              <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.1rem', marginTop: 4, color: s.color }}>{s.value}</div>
            </div>
          ))}
        </div>

        {/* Contact */}
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header"><div className="card-label">Contact</div></div>
          <div className="card-body">
            {[['Email', client.email], ['Phone', client.phone], ['Address', client.address]].map(([l, v]) => v ? (
              <div key={l} style={{ display: 'flex', gap: 12, marginBottom: 8 }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', width: 52, flexShrink: 0, paddingTop: 1 }}>{l}</span>
                <span style={{ fontSize: '0.9rem', color: 'var(--text)', wordBreak: 'break-all' }}>{v}</span>
              </div>
            ) : null)}
          </div>
        </div>

        {/* Invoice history */}
        <SectionTitle>Invoice History ({invoices.length})</SectionTitle>
        <div className="card">
          {invoices.length === 0
            ? <div style={{ padding: 20, textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.87rem' }}>No invoices yet</div>
            : invoices.map(inv => (
              <div key={inv.number} className="inv-row" style={{ cursor: 'pointer' }}
                onClick={() => { setEditInvoice(inv); setPage('new'); }}>
                <div className="inv-row-left">
                  <div className="inv-row-num">{inv.number}</div>
                  <div className="inv-row-client">{inv.date}{inv.paid_date ? ` · Paid ${inv.paid_date}` : ''}</div>
                </div>
                <div className="inv-row-right">
                  <div style={{ fontWeight: 700, color: statusColor(inv.status) }}>{fc(inv.total, sym)}</div>
                  <StatusBadge status={inv.status} />
                </div>
              </div>
            ))
          }
        </div>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// 4. INVOICE PREVIEW
// ════════════════════════════════════════════════════════════════════════════
export function InvoicePreview({ inv, settings, onClose, onExport }) {
  const sym = settings.currency_symbol || '£';
  const accent = settings.theme_accent || '#00e676';

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'var(--bg)', zIndex: 300, overflowY: 'auto' }}>
      <div className="top-bar">
        <button className="back-btn" onClick={onClose}>✕ Close</button>
        <div className="top-bar-title">Preview</div>
        <button className="btn btn-primary btn-sm" onClick={onExport}>⬇ Export</button>
      </div>

      {/* PDF-like preview */}
      <div style={{ maxWidth: 600, margin: '16px auto', padding: '0 16px 100px' }}>
        <div style={{ background: '#fff', borderRadius: 12, overflow: 'hidden', boxShadow: '0 8px 40px rgba(0,0,0,0.3)', color: '#111' }}>
          {/* Header */}
          <div style={{ background: '#0b0e14', padding: '24px 24px 20px', display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <div style={{ color: accent, fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.6rem', letterSpacing: '-0.5px' }}>INVOICE</div>
              <div style={{ color: '#9ca3af', fontSize: '0.85rem', marginTop: 4 }}>{inv.number}</div>
              <div style={{ color: '#6b7280', fontSize: '0.78rem', marginTop: 2 }}>Date: {inv.date} · Due: {inv.due_date}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ color: '#e8eaf0', fontWeight: 700, fontSize: '0.9rem' }}>{settings.company_name}</div>
              <div style={{ color: '#9ca3af', fontSize: '0.75rem', marginTop: 4, maxWidth: 160 }}>{settings.company_address?.split('\n')[0]}</div>
              {settings.vat_number && <div style={{ color: '#6b7280', fontSize: '0.72rem', marginTop: 2 }}>VAT: {settings.vat_number}</div>}
            </div>
          </div>

          {/* Bill to */}
          <div style={{ background: '#f8fafc', padding: '16px 24px', borderBottom: '1px solid #e5e7eb' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: accent, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6 }}>Bill To</div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{inv.client_name}</div>
            {inv.client_address && <div style={{ color: '#6b7280', fontSize: '0.8rem', marginTop: 2 }}>{inv.client_address.split('\n')[0]}</div>}
            {inv.client_email && <div style={{ color: '#6b7280', fontSize: '0.8rem', marginTop: 1 }}>{inv.client_email}</div>}
          </div>

          {/* Line items */}
          <div style={{ padding: '0 24px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #f0f0f0' }}>
                  {['Description','Qty','Price','Amount'].map(h => (
                    <th key={h} style={{ padding: '12px 0 8px', textAlign: h === 'Description' ? 'left' : 'right', color: accent, fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(inv.items || []).filter(i => i.desc).map((item, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #f5f5f5' }}>
                    <td style={{ padding: '10px 0', color: '#111' }}>{item.desc}</td>
                    <td style={{ padding: '10px 0', textAlign: 'right', color: '#6b7280' }}>{item.qty}</td>
                    <td style={{ padding: '10px 0', textAlign: 'right', color: '#6b7280' }}>{fc(item.price, sym)}</td>
                    <td style={{ padding: '10px 0', textAlign: 'right', fontWeight: 600 }}>{fc((parseFloat(item.qty)||1)*(parseFloat(item.price)||0), sym)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Totals */}
          <div style={{ padding: '12px 24px 20px', borderTop: '1px solid #e5e7eb' }}>
            {[
              ['Subtotal', fc(inv.subtotal || 0, sym)],
              [`${settings.tax_label || 'VAT'} (${settings.tax_rate || 20}%)`, fc(inv.tax || 0, sym)],
            ].map(([l, v]) => (
              <div key={l} style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0', fontSize: '0.85rem', color: '#6b7280' }}>
                <span>{l}</span><span>{v}</span>
              </div>
            ))}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: `2px solid ${accent}`, marginTop: 8, paddingTop: 10 }}>
              <span style={{ fontWeight: 700, fontSize: '1rem' }}>Total Due</span>
              <span style={{ fontWeight: 800, fontSize: '1.1rem', color: accent, fontFamily: 'Syne, sans-serif' }}>{fc(inv.total || 0, sym)}</span>
            </div>
          </div>

          {/* Bank / notes */}
          {(settings.bank_account || inv.notes) && (
            <div style={{ background: '#f8fafc', padding: '14px 24px', fontSize: '0.8rem', color: '#6b7280', borderTop: '1px solid #e5e7eb' }}>
              {settings.bank_account && <div style={{ marginBottom: 4 }}>Bank: {settings.bank_name} · Sort: {settings.bank_sort_code} · Account: {settings.bank_account}</div>}
              {inv.notes && <div>{inv.notes}</div>}
            </div>
          )}

          <div style={{ textAlign: 'center', padding: '10px', fontSize: '0.72rem', color: '#d1d5db', background: '#f8fafc', borderTop: '1px solid #f0f0f0' }}>
            Generated with Invoice Generator — letustech.uk
          </div>
        </div>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// 5. GLOBAL SEARCH
// ════════════════════════════════════════════════════════════════════════════
export function GlobalSearch({ settings, setPage, setEditInvoice, onClose }) {
  const [q, setQ]         = useState('');
  const [results, setRes] = useState([]);
  const inputRef          = useRef(null);
  const sym               = settings.currency_symbol || '£';

  useEffect(() => { inputRef.current?.focus(); }, []);

  useEffect(() => {
    if (!q.trim()) { setRes([]); return; }
    const query = q.toLowerCase();
    const invs  = loadInvoices().filter(h =>
      (h.number || '').toLowerCase().includes(query) ||
      (h.client_name || '').toLowerCase().includes(query) ||
      (h.status || '').toLowerCase().includes(query)
    ).slice(0, 6).map(h => ({ type: 'invoice', data: h, label: h.number, sub: `${h.client_name} · ${fc(h.total, sym)}`, badge: h.status }));

    const cls   = loadClients().filter(c =>
      (c.name || '').toLowerCase().includes(query) ||
      (c.email || '').toLowerCase().includes(query)
    ).slice(0, 3).map(c => ({ type: 'client', data: c, label: c.name, sub: c.email, badge: null }));

    setRes([...invs, ...cls]);
  }, [q, sym]);

  function open(r) {
    onClose();
    if (r.type === 'invoice') { setEditInvoice(r.data); setPage('new'); }
    else setPage('clients');
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', zIndex: 400, display: 'flex', flexDirection: 'column', paddingTop: 'env(safe-area-inset-top)' }}>
      <div style={{ background: 'var(--bg-card)', borderBottom: '1px solid var(--border)', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: '1.1rem' }}>🔍</span>
        <input
          ref={inputRef}
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Search invoices, clients..."
          style={{ flex: 1, background: 'none', border: 'none', outline: 'none', color: 'var(--text)', fontSize: '1rem', fontFamily: 'DM Sans, sans-serif' }}
        />
        <button onClick={onClose} style={{ background: 'none', color: 'var(--text-dim)', fontSize: '0.85rem', fontWeight: 600, padding: '4px 8px', border: '1px solid var(--border)', borderRadius: 6, cursor: 'pointer' }}>Esc</button>
      </div>

      <div style={{ background: 'var(--bg-card)', flex: 1, overflowY: 'auto' }}>
        {q && results.length === 0 && (
          <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.9rem' }}>No results for "{q}"</div>
        )}
        {!q && (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.87rem' }}>Type to search invoices and clients</div>
        )}
        {results.map((r, i) => (
          <div key={i} onClick={() => open(r)} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', borderBottom: '1px solid var(--border)', cursor: 'pointer' }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: r.type === 'invoice' ? 'var(--accent)22' : 'var(--blue)22', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', flexShrink: 0 }}>
              {r.type === 'invoice' ? '📄' : '👤'}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>{r.label}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: 1 }}>{r.sub}</div>
            </div>
            {r.badge && <StatusBadge status={r.badge} />}
          </div>
        ))}
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// 6. PARTIAL PAYMENTS (modal used from invoice list / edit)
// ════════════════════════════════════════════════════════════════════════════
export function PartialPaymentModal({ inv, settings, onSave, onClose }) {
  const sym   = settings.currency_symbol || '£';
  const total = parseFloat(inv.total) || 0;
  const alreadyPaid = parseFloat(inv.amount_paid) || 0;
  const [paid, setPaid] = useState(alreadyPaid > 0 ? String(alreadyPaid) : '');

  const balance = Math.max(0, total - (parseFloat(paid) || 0));
  const isFullyPaid = balance <= 0;

  return (
    <Modal title="Record Payment" onClose={onClose}
      actions={<>
        <button className="btn btn-ghost" style={{ flex: 1 }} onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => onSave(parseFloat(paid) || 0)}>Save</button>
      </>}>

      <div style={{ background: 'var(--bg-hover)', borderRadius: 10, padding: '12px 16px', marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>Invoice Total</span>
          <span style={{ fontWeight: 700 }}>{fc(total, sym)}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>Balance After Payment</span>
          <span style={{ fontWeight: 700, color: isFullyPaid ? 'var(--accent)' : 'var(--gold)' }}>{fc(balance, sym)}</span>
        </div>
      </div>

      <Field label={`Amount Paid (${sym})`}>
        <input type="number" step="0.01" min="0" max={total}
          value={paid} onChange={e => setPaid(e.target.value)}
          placeholder={`0.00 — ${fc(total, sym)} for full payment`}
        />
      </Field>

      {isFullyPaid && paid && (
        <div style={{ background: '#0d1a0d', border: '1px solid var(--accent)', borderRadius: 8, padding: '10px 14px', fontSize: '0.85rem', color: 'var(--accent)', marginTop: 8 }}>
          ✅ This will mark the invoice as fully Paid.
        </div>
      )}
      {!isFullyPaid && parseFloat(paid) > 0 && (
        <div style={{ background: '#1a1000', border: '1px solid var(--gold)', borderRadius: 8, padding: '10px 14px', fontSize: '0.85rem', color: 'var(--gold)', marginTop: 8 }}>
          💛 Partial payment — balance of {fc(balance, sym)} will remain outstanding.
        </div>
      )}
    </Modal>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// 7. EXPENSE CATEGORIES CHART (replaces basic expenses list header)
// ════════════════════════════════════════════════════════════════════════════
export function ExpenseCategoryChart({ expenses, sym }) {
  const cats = useMemo(() => {
    const map = {};
    expenses.forEach(e => {
      const cat = e.category || 'General';
      map[cat] = (map[cat] || 0) + (parseFloat(e.amount) || 0);
    });
    return Object.entries(map).sort((a, b) => b[1] - a[1]);
  }, [expenses]);

  const total = cats.reduce((s, [, v]) => s + v, 0);
  const COLORS = ['#00e676','#3b82f6','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#ec4899','#84cc16'];

  if (cats.length === 0) return null;

  return (
    <div className="card" style={{ marginBottom: 16 }}>
      <div className="card-header"><div className="card-label">By Category</div></div>
      <div className="card-body">
        {/* Bar chart */}
        <div style={{ height: 8, borderRadius: 4, overflow: 'hidden', display: 'flex', marginBottom: 16 }}>
          {cats.map(([cat, val], i) => (
            <div key={cat} style={{ width: `${(val/total)*100}%`, background: COLORS[i % COLORS.length] }} />
          ))}
        </div>
        {/* Legend */}
        {cats.map(([cat, val], i) => (
          <div key={cat} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '5px 0', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 10, height: 10, borderRadius: 2, background: COLORS[i % COLORS.length], flexShrink: 0 }} />
              <span style={{ color: 'var(--text-med)' }}>{cat}</span>
            </div>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>{Math.round((val/total)*100)}%</span>
              <span style={{ fontWeight: 600, color: 'var(--red)' }}>-{fc(val, sym)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// 8. LATE FEE CALCULATOR (standalone tool / also used inline)
// ════════════════════════════════════════════════════════════════════════════
export function LateFeeCalculator({ settings }) {
  const sym = settings.currency_symbol || '£';
  const [invTotal,   setInvTotal]   = useState('');
  const [daysOverdue, setDaysOverdue] = useState('');
  const [feeType,    setFeeType]    = useState('Percentage');
  const [feeAmt,     setFeeAmt]     = useState('2');

  const fee = useMemo(() => {
    const total = parseFloat(invTotal) || 0;
    const days  = parseInt(daysOverdue) || 0;
    const amt   = parseFloat(feeAmt) || 0;
    if (!total || !days) return 0;
    return feeType === 'Percentage' ? Math.round(total * (amt / 100) * 100) / 100 : amt;
  }, [invTotal, daysOverdue, feeType, feeAmt]);

  const statutory = useMemo(() => {
    const total = parseFloat(invTotal) || 0;
    const days  = parseInt(daysOverdue) || 0;
    if (!total || !days) return { interest: 0, compensation: 0 };
    // UK Late Payment Act: 8% + Bank of England base rate (approx 5.25%)
    const rate    = 0.1325;
    const interest = Math.round(total * rate * (days / 365) * 100) / 100;
    const comp     = total < 1000 ? 40 : total < 10000 ? 70 : 100;
    return { interest, compensation: comp };
  }, [invTotal, daysOverdue]);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Late Fee Calculator</h1>
          <div className="page-subtitle">UK Late Payment Act</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-header"><div className="card-label">Your Late Fee</div></div>
        <div className="card-body">
          <div className="field-row">
            <Field label={`Invoice Total (${sym})`}>
              <input type="number" step="0.01" value={invTotal} onChange={e => setInvTotal(e.target.value)} placeholder="0.00" />
            </Field>
            <Field label="Days Overdue">
              <input type="number" value={daysOverdue} onChange={e => setDaysOverdue(e.target.value)} placeholder="0" />
            </Field>
          </div>
          <div className="field-row">
            <Field label="Fee Type">
              <select value={feeType} onChange={e => setFeeType(e.target.value)}>
                <option>Percentage</option>
                <option>Fixed Amount</option>
              </select>
            </Field>
            <Field label={feeType === 'Percentage' ? 'Rate (%)' : `Amount (${sym})`}>
              <input type="number" step="0.01" value={feeAmt} onChange={e => setFeeAmt(e.target.value)} />
            </Field>
          </div>
        </div>
        {fee > 0 && (
          <div style={{ padding: '14px 16px', background: '#0d1a0d', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-med)', fontWeight: 600 }}>Your late fee</span>
            <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.3rem', color: 'var(--accent)' }}>{fc(fee, sym)}</span>
          </div>
        )}
      </div>

      {(statutory.interest > 0 || statutory.compensation > 0) && (
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-header"><div className="card-label">UK Statutory Entitlement (Late Payment Act 1998)</div></div>
          <div className="card-body">
            {[
              ['Statutory Interest (13.25%/yr)', fc(statutory.interest, sym)],
              ['Fixed Compensation', fc(statutory.compensation, sym)],
              ['Total Entitlement', fc(statutory.interest + statutory.compensation, sym)],
            ].map(([l, v], i) => (
              <div key={l} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: i < 2 ? '1px solid var(--border)' : 'none', fontSize: '0.87rem' }}>
                <span style={{ color: 'var(--text-med)' }}>{l}</span>
                <span style={{ fontWeight: i === 2 ? 700 : 500, color: i === 2 ? 'var(--gold)' : 'var(--text)' }}>{v}</span>
              </div>
            ))}
          </div>
          <div style={{ padding: '10px 16px', fontSize: '0.75rem', color: 'var(--text-dim)', borderTop: '1px solid var(--border)' }}>
            UK businesses can claim statutory interest on late B2B payments under the Late Payment of Commercial Debts Act 1998.
          </div>
        </div>
      )}
    </div>
  );
}

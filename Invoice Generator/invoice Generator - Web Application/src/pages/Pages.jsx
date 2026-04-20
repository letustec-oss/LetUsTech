import React, { useState, useMemo } from 'react';
import {
  loadInvoices, saveInvoices, loadClients, saveClients,
  loadExpenses, saveExpenses, loadSettings, saveSettings,
  exportAllData, importAllData, DEFAULT_SETTINGS,
} from '../utils/storage';
import { fc, today, isOverdue, statusColor, invoicesToCSV, downloadText, downloadJSON, avgDaysToPay } from '../utils/helpers';
import { StatusBadge, EmptyState, SectionTitle, Field, Input, Select, Textarea, Modal, Confirm, Toast, ActionRow } from '../components/UI';
import { EmailModal, EmailSettingsTab } from '../components/Email';
import { ExpenseCategoryChart } from './Features';

// ════════════════════════════════════════════════════════════════════════════
// INVOICES LIST
// ════════════════════════════════════════════════════════════════════════════
export function InvoicesList({ settings, setPage, setEditInvoice }) {
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');
  const [confirm,    setConfirm]    = useState(null);
  const [toast,      setToast]      = useState('');
  const [emailInv,   setEmailInv]   = useState(null);
  const sym = settings.currency_symbol || '£';
  const fmt = settings.date_format || 'DD/MM/YYYY';

  const allInvoices = useMemo(() => {
    return loadInvoices().map(h => ({
      ...h,
      status: (h.status === 'Unpaid' && isOverdue(h.due_date, fmt)) ? 'Overdue' : h.status,
    }));
  }, [fmt]);

  const filtered = useMemo(() => {
    let list = allInvoices;
    if (filter !== 'All') list = list.filter(h => h.status === filter);
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(h =>
        (h.number || '').toLowerCase().includes(q) ||
        (h.client_name || '').toLowerCase().includes(q) ||
        (h.status || '').toLowerCase().includes(q)
      );
    }
    return list;
  }, [allInvoices, filter, search]);

  function markPaid(inv) {
    const list = loadInvoices().map(h =>
      h.number === inv.number ? { ...h, status: 'Paid', paid_date: today(fmt) } : h
    );
    saveInvoices(list);
    setToast('✅ Marked as paid');
  }

  function deleteInv(inv) {
    saveInvoices(loadInvoices().filter(h => h.number !== inv.number));
    setConfirm(null);
    setToast('🗑️ Deleted');
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Invoices</h1>
        <button className="btn btn-primary btn-sm" onClick={() => { setEditInvoice(null); setPage('new'); }}>＋</button>
      </div>

      {/* Search */}
      <div className="search-bar">
        <span style={{ color: 'var(--text-dim)' }}>🔍</span>
        <input placeholder="Search invoices..." value={search} onChange={e => setSearch(e.target.value)} />
        {search && <button style={{ background: 'none', color: 'var(--text-dim)', fontSize: '1rem' }} onClick={() => setSearch('')}>✕</button>}
      </div>

      {/* Filters */}
      <div className="filter-bar">
        {['All','Unpaid','Paid','Overdue','Draft'].map(f => (
          <button key={f} className={`filter-chip${filter === f ? ' active' : ''}`} onClick={() => setFilter(f)}>{f}</button>
        ))}
      </div>

      {/* Export */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
        <button className="btn btn-ghost btn-sm" onClick={() => downloadText(invoicesToCSV(allInvoices), 'invoices.csv')}>
          📊 Export CSV
        </button>
      </div>

      <div className="card">
        {filtered.length === 0
          ? <EmptyState icon="📄" title="No invoices" message={filter !== 'All' ? `No ${filter.toLowerCase()} invoices.` : 'Create your first invoice.'} />
          : filtered.map(inv => (
            <InvoiceRow key={inv.number} inv={inv} sym={sym}
              onEdit={() => { setEditInvoice(inv); setPage('new'); }}
              onPaid={() => markPaid(inv)}
              onDelete={() => setConfirm(inv)}
              onEmail={() => setEmailInv(inv)}
            />
          ))
        }
      </div>

      {emailInv && (
        <EmailModal
          inv={emailInv}
          settings={settings}
          onClose={() => setEmailInv(null)}
          onSent={(dest) => { setEmailInv(null); if (dest === 'settings') setPage('settings'); else setToast('✅ Invoice sent!'); }}
        />
      )}

      {confirm && (
        <Confirm
          title="Delete Invoice"
          message={`Delete ${confirm.number} (${confirm.client_name})? This cannot be undone.`}
          danger
          onConfirm={() => deleteInv(confirm)}
          onCancel={() => setConfirm(null)}
        />
      )}
      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

function InvoiceRow({ inv, sym, onEdit, onPaid, onDelete, onEmail }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <div className="inv-row" onClick={() => setOpen(o => !o)} style={{ cursor: 'pointer' }}>
        <div className="inv-row-left">
          <div className="inv-row-num">{inv.number}</div>
          <div className="inv-row-client">{inv.client_name || '—'}</div>
        </div>
        <div className="inv-row-right">
          <div className="inv-row-amount" style={{ color: statusColor(inv.status) }}>{fc(inv.total, sym)}</div>
          <StatusBadge status={inv.status} />
        </div>
      </div>
      {open && (
        <div style={{ background: 'var(--bg-hover)', padding: '10px 16px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: 8 }}>
            Due: {inv.due_date} · {inv.date}
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {inv.status === 'Draft' || inv.status === 'Unpaid' || inv.status === 'Overdue' ? (
              <button className="btn btn-primary btn-sm" onClick={e => { e.stopPropagation(); onEdit(); }}>✏️ Edit</button>
            ) : null}
            {inv.status !== 'Paid' && (
              <button className="btn btn-ghost btn-sm" onClick={e => { e.stopPropagation(); onPaid(); setOpen(false); }}>✓ Mark Paid</button>
            )}
            <button className="btn btn-primary btn-sm" onClick={e => { e.stopPropagation(); onEmail && onEmail(); setOpen(false); }}>📧 Email</button>
            <button className="btn btn-ghost btn-sm" onClick={e => { e.stopPropagation(); onEdit(); }}>⧉ Duplicate</button>
            <button className="btn btn-ghost btn-sm" style={{ color: 'var(--red)' }} onClick={e => { e.stopPropagation(); onDelete(); setOpen(false); }}>🗑️ Delete</button>
          </div>
        </div>
      )}
    </>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// CLIENTS
// ════════════════════════════════════════════════════════════════════════════
export function ClientsList({ settings, setPage, setNewInvoiceClient, setSelectedClient }) {
  const [clients,  setClients]  = useState(loadClients);
  const [editing,  setEditing]  = useState(null);
  const [showAdd,  setShowAdd]  = useState(false);
  const [confirm,  setConfirm]  = useState(null);
  const [toast,    setToast]    = useState('');
  const fmt = settings.date_format || 'DD/MM/YYYY';
  const invoices = loadInvoices();

  function saveAndRefresh(list) { saveClients(list); setClients(list); }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Clients</h1>
        <button className="btn btn-primary btn-sm" onClick={() => { setEditing(null); setShowAdd(true); }}>＋</button>
      </div>

      {clients.length === 0
        ? <EmptyState icon="👥" title="No clients yet" message="Add clients to load them quickly onto invoices." action={() => setShowAdd(true)} actionLabel="Add First Client" />
        : <div className="card">
            {clients.map(c => {
              const avg = avgDaysToPay(c.name, invoices, fmt);
              return (
                <div key={c.name} className="inv-row" style={{ cursor: 'pointer' }} onClick={() => { setSelectedClient && setSelectedClient(c); setPage('client-detail'); }}>
                  <div className="inv-row-left">
                    <div className="inv-row-num">{c.name}</div>
                    <div className="inv-row-client">{c.email}</div>
                  </div>
                  <div className="inv-row-right" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {avg !== null && (
                      <span style={{ fontSize: '0.75rem', color: avg <= 14 ? 'var(--accent)' : avg <= 30 ? 'var(--gold)' : 'var(--red)' }}>
                        {avg}d avg
                      </span>
                    )}
                    <button className="btn btn-ghost btn-sm" onClick={() => { setEditing(c); setShowAdd(true); }}>Edit</button>
                    <button className="btn btn-ghost btn-sm" style={{ color: 'var(--red)' }} onClick={() => setConfirm(c)}>✕</button>
                  </div>
                </div>
              );
            })}
          </div>
      }

      {showAdd && (
        <ClientForm
          initial={editing}
          onSave={data => {
            const list = clients.filter(c => c.name !== (editing?.name || ''));
            list.push(data);
            saveAndRefresh(list);
            setShowAdd(false); setEditing(null);
            setToast('✅ Client saved');
          }}
          onClose={() => { setShowAdd(false); setEditing(null); }}
        />
      )}

      {confirm && (
        <Confirm title="Delete Client" message={`Delete ${confirm.name}?`} danger
          onConfirm={() => { saveAndRefresh(clients.filter(c => c.name !== confirm.name)); setConfirm(null); setToast('🗑️ Deleted'); }}
          onCancel={() => setConfirm(null)}
        />
      )}
      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

function ClientForm({ initial, onSave, onClose }) {
  const [name,    setName]    = useState(initial?.name || '');
  const [email,   setEmail]   = useState(initial?.email || '');
  const [phone,   setPhone]   = useState(initial?.phone || '');
  const [address, setAddress] = useState(initial?.address || '');
  return (
    <Modal title={initial ? 'Edit Client' : 'Add Client'} onClose={onClose}
      actions={<>
        <button className="btn btn-ghost" style={{ flex: 1 }} onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => {
          if (!name.trim()) return;
          onSave({ name: name.trim(), email, phone, address, notes: '' });
        }}>Save</button>
      </>}>
      <Field label="Name *"><input value={name} onChange={e => setName(e.target.value)} placeholder="Client name" /></Field>
      <Field label="Email"><input type="email" value={email} onChange={e => setEmail(e.target.value)} /></Field>
      <Field label="Phone"><input type="tel" value={phone} onChange={e => setPhone(e.target.value)} /></Field>
      <Field label="Address"><textarea rows={2} value={address} onChange={e => setAddress(e.target.value)} /></Field>
    </Modal>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// EXPENSES
// ════════════════════════════════════════════════════════════════════════════
export function ExpensesList({ settings }) {
  const [expenses, setExpenses] = useState(loadExpenses);
  const [showAdd,  setShowAdd]  = useState(false);
  const [toast,    setToast]    = useState('');
  const sym = settings.currency_symbol || '£';

  const total = expenses.reduce((s, e) => s + (parseFloat(e.amount) || 0), 0);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Expenses</h1>
          <div className="page-subtitle">Total: {fc(total, sym)}</div>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowAdd(true)}>＋</button>
      </div>

      <ExpenseCategoryChart expenses={expenses} sym={sym} />

      {expenses.length === 0
        ? <EmptyState icon="💸" title="No expenses" message="Log business costs to track your true profit." action={() => setShowAdd(true)} actionLabel="Add Expense" />
        : <div className="card">
            {expenses.slice().reverse().map((e, i) => (
              <div key={i} className="inv-row">
                <div className="inv-row-left">
                  <div className="inv-row-num">{e.description}</div>
                  <div className="inv-row-client">{e.category} · {e.date}</div>
                </div>
                <div className="inv-row-right">
                  <div className="inv-row-amount" style={{ color: 'var(--red)' }}>-{fc(e.amount, sym)}</div>
                  <button style={{ background: 'none', color: 'var(--text-dim)', fontSize: '0.9rem', cursor: 'pointer' }}
                    onClick={() => { const list = [...expenses]; list.splice(expenses.length - 1 - i, 1); saveExpenses(list); setExpenses(list); }}>
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
      }

      {showAdd && (
        <AddExpenseForm
          sym={sym}
          onSave={data => {
            const list = [...expenses, data];
            saveExpenses(list); setExpenses(list);
            setShowAdd(false); setToast('✅ Expense saved');
          }}
          onClose={() => setShowAdd(false)}
        />
      )}
      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

function AddExpenseForm({ sym, onSave, onClose }) {
  const [desc, setDesc] = useState('');
  const [amount, setAmount] = useState('');
  const [cat, setCat] = useState('General');
  const [date, setDate] = useState(today());
  const cats = ['General','Software','Travel','Equipment','Marketing','Office','Professional Services','Other'];
  return (
    <Modal title="Add Expense" onClose={onClose}
      actions={<>
        <button className="btn btn-ghost" style={{ flex: 1 }} onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => {
          if (!desc || !amount) return;
          onSave({ description: desc, amount: parseFloat(amount), category: cat, date });
        }}>Save</button>
      </>}>
      <Field label="Description"><input value={desc} onChange={e => setDesc(e.target.value)} placeholder="e.g. Adobe subscription" /></Field>
      <Field label="Amount ({sym})"><input type="number" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} placeholder="0.00" /></Field>
      <Field label="Category">
        <select value={cat} onChange={e => setCat(e.target.value)}>
          {cats.map(c => <option key={c}>{c}</option>)}
        </select>
      </Field>
      <Field label="Date"><input type="text" value={date} onChange={e => setDate(e.target.value)} placeholder="DD/MM/YYYY" /></Field>
    </Modal>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// REPORTS
// ════════════════════════════════════════════════════════════════════════════
export function Reports({ settings }) {
  const sym      = settings.currency_symbol || '£';
  const invoices = loadInvoices();
  const expenses = loadExpenses();
  const year     = new Date().getFullYear();
  const paid     = invoices.filter(h => h.status === 'Paid');
  const revenue  = paid.reduce((s, h) => s + (parseFloat(h.total) || 0), 0);
  const vat      = paid.reduce((s, h) => s + (parseFloat(h.tax) || 0), 0);
  const expTotal = expenses.reduce((s, e) => s + (parseFloat(e.amount) || 0), 0);

  const byMonth  = Array.from({ length: 12 }, (_, i) => {
    const m = String(i + 1).padStart(2, '0');
    const monthPaid = paid.filter(h => (h.date || '').includes(`/${m}/${year}`) || (h.date || '').includes(`-${year}-${m}`));
    return { month: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i], rev: monthPaid.reduce((s,h) => s+(parseFloat(h.total)||0),0) };
  });
  const maxRev = Math.max(...byMonth.map(m => m.rev), 1);

  return (
    <div className="page">
      <div className="page-header"><h1>Reports</h1></div>

      <div className="stats-grid" style={{ marginBottom: 16 }}>
        <div className="stat-card"><div className="stat-label">Revenue {year}</div><div className="stat-value" style={{ color: 'var(--accent)' }}>{fc(revenue, sym)}</div></div>
        <div className="stat-card"><div className="stat-label">VAT Collected</div><div className="stat-value">{fc(vat, sym)}</div></div>
        <div className="stat-card"><div className="stat-label">Expenses</div><div className="stat-value" style={{ color: 'var(--red)' }}>{fc(expTotal, sym)}</div></div>
        <div className="stat-card"><div className="stat-label">Net Profit</div><div className="stat-value" style={{ color: 'var(--gold)' }}>{fc(revenue - expTotal, sym)}</div></div>
      </div>

      {/* Bar chart */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header"><div className="card-label">Monthly Revenue — {year}</div></div>
        <div className="card-body">
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 80 }}>
            {byMonth.map(({ month, rev }) => (
              <div key={month} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
                <div style={{ width: '100%', background: rev > 0 ? 'var(--accent)' : 'var(--border)', borderRadius: 3, height: Math.max(3, (rev / maxRev) * 70), transition: 'height 0.3s' }} />
                <span style={{ fontSize: '0.6rem', color: 'var(--text-dim)' }}>{month}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* HMRC VAT */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header"><div className="card-label">🇬🇧 HMRC VAT Return</div></div>
        <div className="card-body">
          {[
            ['Box 1', 'VAT due on sales', fc(vat, sym)],
            ['Box 3', 'Total VAT due', fc(vat, sym)],
            ['Box 6', 'Total sales (excl. VAT)', fc(revenue - vat, sym)],
          ].map(([box, label, val]) => (
            <div key={box} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border)', fontSize: '0.87rem' }}>
              <span style={{ color: 'var(--accent)', fontWeight: 700, width: 48 }}>{box}</span>
              <span style={{ flex: 1, color: 'var(--text-med)' }}>{label}</span>
              <span style={{ fontWeight: 600 }}>{val}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => downloadText(invoicesToCSV(paid), `report_${year}.csv`)}>
          📊 Export CSV
        </button>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// SETTINGS
// ════════════════════════════════════════════════════════════════════════════
export function Settings({ settings, setSettings }) {
  const [local, setLocal]   = useState({ ...settings });
  const [tab,   setTab]     = useState('business');
  const [toast, setToast]   = useState('');

  function update(key, val) { setLocal(s => ({ ...s, [key]: val })); }

  function saveAll() {
    saveSettings(local);
    setSettings(local);
    setToast('✅ Settings saved');
  }

  const tabs = [
    { id: 'business',  label: '🏢 Business' },
    { id: 'invoicing', label: '💰 Invoicing' },
    { id: 'email',     label: '📧 Email' },
    { id: 'backup',    label: '☁️ Backup' },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <h1>Settings</h1>
        <button className="btn btn-primary btn-sm" onClick={saveAll}>Save</button>
      </div>

      {/* Tab bar */}
      <div className="filter-bar" style={{ marginBottom: 16 }}>
        {tabs.map(t => (
          <button key={t.id} className={`filter-chip${tab === t.id ? ' active' : ''}`} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'business' && <>
        <SectionTitle>Your Business</SectionTitle>
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-body">
            <Field label="Company Name"><input value={local.company_name} onChange={e => update('company_name', e.target.value)} /></Field>
            <Field label="Email"><input type="email" value={local.company_email} onChange={e => update('company_email', e.target.value)} /></Field>
            <div className="field-row">
              <Field label="Phone"><input value={local.company_phone} onChange={e => update('company_phone', e.target.value)} /></Field>
              <Field label="Website"><input value={local.company_website} onChange={e => update('company_website', e.target.value)} /></Field>
            </div>
            <Field label="Address"><textarea rows={3} value={local.company_address} onChange={e => update('company_address', e.target.value)} /></Field>
            <Field label="VAT Number"><input value={local.vat_number} onChange={e => update('vat_number', e.target.value)} placeholder="GB123456789" /></Field>
          </div>
        </div>
        <SectionTitle>Banking & Payments</SectionTitle>
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-body">
            <Field label="Bank Name"><input value={local.bank_name} onChange={e => update('bank_name', e.target.value)} /></Field>
            <div className="field-row">
              <Field label="Sort Code"><input value={local.bank_sort_code} onChange={e => update('bank_sort_code', e.target.value)} placeholder="00-00-00" /></Field>
              <Field label="Account Number"><input value={local.bank_account} onChange={e => update('bank_account', e.target.value)} /></Field>
            </div>
            <Field label="Payment Reference"><input value={local.bank_reference} onChange={e => update('bank_reference', e.target.value)} /></Field>
            <Field label="Payment Terms (days)"><input type="number" value={local.payment_terms} onChange={e => update('payment_terms', e.target.value)} /></Field>
          </div>
        </div>
      </>}

      {tab === 'invoicing' && <>
        <SectionTitle>Tax & Currency</SectionTitle>
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-body">
            <div className="field-row">
              <Field label="Currency Symbol"><input value={local.currency_symbol} onChange={e => update('currency_symbol', e.target.value)} placeholder="£" /></Field>
              <Field label="Tax Rate (%)"><input type="number" value={local.tax_rate} onChange={e => update('tax_rate', e.target.value)} /></Field>
            </div>
            <div className="field-row">
              <Field label="Tax Label"><input value={local.tax_label} onChange={e => update('tax_label', e.target.value)} placeholder="VAT" /></Field>
              <Field label="Invoice Prefix"><input value={local.invoice_prefix} onChange={e => update('invoice_prefix', e.target.value)} placeholder="INV" /></Field>
            </div>
            <Field label="Starting Number"><input type="number" value={local.invoice_start} onChange={e => update('invoice_start', e.target.value)} /></Field>
            <Field label="Default Notes"><textarea rows={2} value={local.default_notes} onChange={e => update('default_notes', e.target.value)} /></Field>
          </div>
        </div>
      </>}

      {tab === 'email' && (
        <EmailSettingsTab local={local} update={update} />
      )}

      {tab === 'backup' && <>
        <SectionTitle>Data Management</SectionTitle>
        <div className="card" style={{ marginBottom: 12 }}>
          <div className="card-body">
            <ActionRow icon="📦" label="Export All Data" sub="Download a JSON backup of everything"
              onClick={() => downloadJSON(exportAllData(), `invoice-backup-${new Date().toISOString().slice(0,10)}.json`)} />
            <ActionRow icon="📥" label="Import Backup" sub="Restore from a JSON backup file"
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file'; input.accept = '.json';
                input.onchange = e => {
                  const file = e.target.files[0];
                  if (!file) return;
                  const reader = new FileReader();
                  reader.onload = ev => {
                    try {
                      const data = JSON.parse(ev.target.result);
                      const mode = window.confirm('Replace ALL data? (OK = replace, Cancel = merge)') ? 'replace' : 'merge';
                      importAllData(data, mode);
                      setToast('✅ Data imported — reload to see changes');
                    } catch { setToast('⚠️ Invalid backup file'); }
                  };
                  reader.readAsText(file);
                };
                input.click();
              }}
            />
            <ActionRow icon="🗑️" label="Clear All Data" sub="Wipe invoices, clients and expenses" danger
              onClick={() => {
                if (window.confirm('Delete all data? This cannot be undone.')) {
                  localStorage.clear();
                  setToast('🗑️ All data cleared');
                  setTimeout(() => window.location.reload(), 1000);
                }
              }}
            />
          </div>
        </div>
      </>}

      <button className="btn btn-primary" style={{ width: '100%', marginTop: 8 }} onClick={saveAll}>
        💾 Save Settings
      </button>

      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// MORE (Help, About)
// ════════════════════════════════════════════════════════════════════════════
export function More({ settings, setPage }) {
  return (
    <div className="page">
      <div className="page-header"><h1>More</h1></div>

      <SectionTitle>Tools</SectionTitle>
      <div className="card" style={{ marginBottom: 16 }}>
        <ActionRow icon="💸" label="Expenses" sub="Log and track business costs" onClick={() => setPage('expenses')} />
        <ActionRow icon="📈" label="Reports" sub="Revenue, VAT and profit summaries" onClick={() => setPage('reports')} />
        <ActionRow icon="🔁" label="Recurring Invoices" sub="Retainers & regular clients" onClick={() => setPage('recurring')} />
        <ActionRow icon="🔔" label="Overdue Reminders" sub="Chase unpaid invoices" onClick={() => setPage('reminders')} />
        <ActionRow icon="🧮" label="Late Fee Calculator" sub="UK Late Payment Act rates" onClick={() => setPage('late-fee')} />
        <ActionRow icon="⚙️" label="Settings" sub="Business details, tax, invoicing" onClick={() => setPage('settings')} />
      </div>

      <SectionTitle>Mobile Tools</SectionTitle>
      <div className="card" style={{ marginBottom: 16 }}>
        <ActionRow icon="⚡" label="Quick Invoice" sub="Send an invoice in 60 seconds" onClick={() => setPage('quick-invoice')} />
        <ActionRow icon="📷" label="Scan Receipt" sub="Camera → expense in one tap" onClick={() => setPage('scan-receipt')} />
      </div>

      <SectionTitle>Help & Debug</SectionTitle>
      <div className="card" style={{ marginBottom: 16 }}>
        <ActionRow icon="📖" label="Help Centre" sub="Guides, VAT law, FAQ" onClick={() => setPage('help-hub')} />
        <ActionRow icon="🐛" label="Error Log" sub="Crash reports for developers" onClick={() => setPage('error-log')} />
        <ActionRow icon="ℹ️" label="About" sub={`Version 1.0 · LetUsTech`} onClick={() => setPage('about')} />
      </div>

      <div className="card" style={{ marginBottom: 16, padding: 20, textAlign: 'center' }}>
        <div style={{ fontSize: '2rem', marginBottom: 8 }}>🧾</div>
        <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.1rem', color: 'var(--accent)' }}>Invoice Generator</div>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginTop: 4 }}>Free. Offline. No account needed.</div>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginTop: 2 }}>Made by Deano @ LetUsTech · letustech.uk</div>
        <a href="https://www.paypal.com/donate/?hosted_button_id=MJNXEL8GRRPSL"
          target="_blank" rel="noreferrer"
          style={{ display: 'inline-block', marginTop: 14, background: '#ffc439', color: '#000', borderRadius: 8, padding: '8px 20px', fontWeight: 700, fontSize: '0.87rem', textDecoration: 'none' }}>
          ☕ Buy me a coffee
        </a>
      </div>
    </div>
  );
}

import React, { useMemo } from 'react';
import { loadInvoices, loadExpenses } from '../utils/storage';
import { fc, isOverdue, statusColor } from '../utils/helpers';
import { StatusBadge, EmptyState } from '../components/UI';
import { NotificationBanner } from '../components/Mobile';

export default function Dashboard({ settings, setPage, setEditInvoice }) {
  const invoices = loadInvoices();
  const expenses = loadExpenses();
  const sym = settings.currency_symbol || '£';

  const stats = useMemo(() => {
    const paid     = invoices.filter(h => h.status === 'Paid');
    const unpaid   = invoices.filter(h => h.status === 'Unpaid' || h.status === 'Overdue');
    const overdue  = invoices.filter(h => h.status === 'Overdue' ||
                       (h.status === 'Unpaid' && isOverdue(h.due_date, settings.date_format)));
    const revenue  = paid.reduce((s, h) => s + (parseFloat(h.total) || 0), 0);
    const outstanding = unpaid.reduce((s, h) => s + (parseFloat(h.total) || 0), 0);
    const exp_total   = expenses.reduce((s, e) => s + (parseFloat(e.amount) || 0), 0);
    return { revenue, outstanding, overdue: overdue.length, expTotal: exp_total, paidCount: paid.length };
  }, [invoices, expenses, settings.date_format]);

  const recent = invoices.slice(0, 5);

  return (
    <div className="page">
      <NotificationBanner settings={settings} setPage={setPage} setEditInvoice={setEditInvoice} />
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          {settings.company_name && (
            <div className="page-subtitle">{settings.company_name}</div>
          )}
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setPage('new')}>＋ Invoice</button>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Revenue</div>
          <div className="stat-value" style={{ color: 'var(--accent)' }}>{fc(stats.revenue, sym)}</div>
          <div className="stat-sub">{stats.paidCount} paid</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Outstanding</div>
          <div className="stat-value" style={{ color: 'var(--gold)' }}>{fc(stats.outstanding, sym)}</div>
          <div className="stat-sub">awaiting payment</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Overdue</div>
          <div className="stat-value" style={{ color: stats.overdue > 0 ? 'var(--red)' : 'var(--text-dim)' }}>
            {stats.overdue}
          </div>
          <div className="stat-sub">invoice{stats.overdue !== 1 ? 's' : ''}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Expenses</div>
          <div className="stat-value">{fc(stats.expTotal, sym)}</div>
          <div className="stat-sub">logged</div>
        </div>
      </div>

      {/* Recent invoices */}
      <div className="section-title">Recent Invoices</div>
      <div className="card" style={{ marginBottom: 16 }}>
        {recent.length === 0
          ? <EmptyState icon="📄" title="No invoices yet" message="Create your first invoice to get started." />
          : recent.map(inv => (
            <div key={inv.number} className="inv-row"
              onClick={() => { setEditInvoice(inv); setPage('invoice-detail'); }}
              style={{ cursor: 'pointer' }}
            >
              <div className="inv-row-left">
                <div className="inv-row-num">{inv.number}</div>
                <div className="inv-row-client">{inv.client_name || '—'}</div>
              </div>
              <div className="inv-row-right">
                <div className="inv-row-amount" style={{ color: statusColor(inv.status) }}>
                  {fc(inv.total, sym)}
                </div>
                <StatusBadge status={inv.status} />
              </div>
            </div>
          ))
        }
      </div>

      {recent.length > 0 && (
        <button className="btn btn-ghost" style={{ width: '100%' }} onClick={() => setPage('invoices')}>
          View All Invoices
        </button>
      )}

      {/* Quick actions */}
      <div className="section-title" style={{ marginTop: 20 }}>Quick Actions</div>
      <div className="card">
        {[
          { icon: '📄', label: 'New Invoice',     sub: 'Create and send',          action: () => setPage('new') },
          { icon: '👥', label: 'Add Client',       sub: 'Save to address book',    action: () => setPage('add-client') },
          { icon: '💸', label: 'Log Expense',      sub: 'Track a business cost',   action: () => setPage('add-expense') },
          { icon: '📈', label: 'View Reports',     sub: 'Revenue & VAT summary',   action: () => setPage('reports') },
        ].map(({ icon, label, sub, action }) => (
          <div key={label} className="action-row" onClick={action}>
            <div className="action-row-icon">{icon}</div>
            <div className="action-row-text">
              <div className="action-row-label">{label}</div>
              <div className="action-row-sub">{sub}</div>
            </div>
            <span className="action-row-arrow">›</span>
          </div>
        ))}
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { statusColor, statusBg } from '../utils/helpers';

// ── StatusBadge ───────────────────────────────────────────────────────────
export function StatusBadge({ status }) {
  return (
    <span className="badge" style={{
      color: statusColor(status),
      background: statusBg(status),
    }}>
      {status}
    </span>
  );
}

// ── Toast ─────────────────────────────────────────────────────────────────
export function Toast({ message, onDone }) {
  useEffect(() => {
    const t = setTimeout(onDone, 2200);
    return () => clearTimeout(t);
  }, [onDone]);
  return <div className="toast">{message}</div>;
}

// ── Modal ─────────────────────────────────────────────────────────────────
export function Modal({ title, onClose, children, actions }) {
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-handle" />
        {title && <h2>{title}</h2>}
        {children}
        {actions && <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>{actions}</div>}
      </div>
    </div>
  );
}

// ── Confirm dialog ────────────────────────────────────────────────────────
export function Confirm({ title, message, onConfirm, onCancel, danger }) {
  return (
    <Modal title={title} onClose={onCancel} actions={
      <>
        <button className="btn btn-ghost" style={{ flex: 1 }} onClick={onCancel}>Cancel</button>
        <button className={`btn ${danger ? 'btn-danger' : 'btn-primary'}`} style={{ flex: 1 }} onClick={onConfirm}>
          Confirm
        </button>
      </>
    }>
      <p style={{ color: 'var(--text-med)', fontSize: '0.92rem', lineHeight: 1.5 }}>{message}</p>
    </Modal>
  );
}

// ── Empty state ───────────────────────────────────────────────────────────
export function EmptyState({ icon, title, message, action, actionLabel }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{message}</p>
      {action && (
        <button className="btn btn-primary" style={{ marginTop: 20 }} onClick={action}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}

// ── Section title ─────────────────────────────────────────────────────────
export function SectionTitle({ children }) {
  return <div className="section-title">{children}</div>;
}

// ── Field ─────────────────────────────────────────────────────────────────
export function Field({ label, children, style }) {
  return (
    <div className="field" style={style}>
      {label && <label>{label}</label>}
      {children}
    </div>
  );
}

// ── Input ─────────────────────────────────────────────────────────────────
export function Input({ label, ...props }) {
  return (
    <Field label={label}>
      <input {...props} />
    </Field>
  );
}

// ── Select ────────────────────────────────────────────────────────────────
export function Select({ label, options, ...props }) {
  return (
    <Field label={label}>
      <select {...props}>
        {options.map(o => (
          <option key={typeof o === 'string' ? o : o.value} value={typeof o === 'string' ? o : o.value}>
            {typeof o === 'string' ? o : o.label}
          </option>
        ))}
      </select>
    </Field>
  );
}

// ── Textarea ──────────────────────────────────────────────────────────────
export function Textarea({ label, rows = 3, ...props }) {
  return (
    <Field label={label}>
      <textarea rows={rows} {...props} />
    </Field>
  );
}

// ── Action row ────────────────────────────────────────────────────────────
export function ActionRow({ icon, label, sub, onClick, danger, right }) {
  return (
    <div className="action-row" onClick={onClick}>
      <div className="action-row-icon" style={danger ? { background: '#ef444422', color: '#ef4444' } : {}}>
        {icon}
      </div>
      <div className="action-row-text">
        <div className="action-row-label" style={danger ? { color: 'var(--red)' } : {}}>{label}</div>
        {sub && <div className="action-row-sub">{sub}</div>}
      </div>
      {right || <span className="action-row-arrow">›</span>}
    </div>
  );
}

// ── BottomNav ─────────────────────────────────────────────────────────────
export function BottomNav({ page, setPage }) {
  const items = [
    { id: 'dashboard', icon: '◈', label: 'Home' },
    { id: 'invoices',  icon: '⬡', label: 'Invoices' },
    { id: 'new',       icon: '+', label: 'New', fab: true },
    { id: 'clients',   icon: '◎', label: 'Clients' },
    { id: 'more',      icon: '⋯', label: 'More' },
  ];
  return (
    <nav className="bottom-nav">
      {items.map(item => (
        <button
          key={item.id}
          className={`nav-item${page === item.id ? ' active' : ''}`}
          onClick={() => setPage(item.id)}
          style={item.fab ? {
            margin: '-10px 4px 0',
          } : {}}
        >
          {item.fab
            ? <span style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                width: 46, height: 46, borderRadius: '50%',
                background: 'var(--accent)', color: '#000',
                fontSize: '1.6rem', fontWeight: 700,
                boxShadow: '0 4px 16px rgba(0,230,118,0.4)',
              }}>+</span>
            : <>
                <span className="nav-icon" style={{ fontSize: '1.25rem' }}>{item.icon}</span>
                <span>{item.label}</span>
              </>
          }
        </button>
      ))}
    </nav>
  );
}

// ── Sidebar (desktop) ─────────────────────────────────────────────────────
export function Sidebar({ page, setPage }) {
  const items = [
    { id: 'dashboard', icon: '◈', label: 'Dashboard' },
    { id: 'invoices',  icon: '⬡', label: 'Invoices' },
    { id: 'new',       icon: '＋', label: 'New Invoice' },
    { id: 'clients',   icon: '◎', label: 'Clients' },
    { id: 'expenses',  icon: '💸', label: 'Expenses' },
    { id: 'reports',   icon: '📈', label: 'Reports' },
    { id: 'settings',  icon: '⚙', label: 'Settings' },
    { id: 'more',      icon: '⋯', label: 'More' },
  ];
  return (
    <div className="sidebar" style={{ display: 'none' }}>
      <div className="sidebar-logo">
        <span>🧾</span> Invoice
      </div>
      {items.map(item => (
        <button
          key={item.id}
          className={`sidebar-nav-item${page === item.id ? ' active' : ''}`}
          onClick={() => setPage(item.id)}
        >
          <span className="nav-icon">{item.icon}</span>
          {item.label}
        </button>
      ))}
    </div>
  );
}

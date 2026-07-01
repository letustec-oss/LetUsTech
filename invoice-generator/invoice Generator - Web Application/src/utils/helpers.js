// ── Currency ──────────────────────────────────────────────────────────────
export function fc(amount, sym = '£') {
  const n = parseFloat(amount) || 0;
  return `${sym}${n.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// ── Date ──────────────────────────────────────────────────────────────────
export function today(fmt = 'DD/MM/YYYY') {
  return formatDate(new Date(), fmt);
}

export function formatDate(date, fmt = 'DD/MM/YYYY') {
  const d = new Date(date);
  if (isNaN(d)) return '';
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  if (fmt === 'MM/DD/YYYY') return `${mm}/${dd}/${yyyy}`;
  if (fmt === 'YYYY-MM-DD') return `${yyyy}-${mm}-${dd}`;
  return `${dd}/${mm}/${yyyy}`;
}

export function parseDate(str, fmt = 'DD/MM/YYYY') {
  if (!str) return null;
  try {
    let d;
    if (fmt === 'DD/MM/YYYY') {
      const [dd, mm, yyyy] = str.split('/');
      d = new Date(`${yyyy}-${mm}-${dd}`);
    } else if (fmt === 'MM/DD/YYYY') {
      const [mm, dd, yyyy] = str.split('/');
      d = new Date(`${yyyy}-${mm}-${dd}`);
    } else {
      d = new Date(str);
    }
    return isNaN(d) ? null : d;
  } catch { return null; }
}

export function addDays(dateStr, days, fmt = 'DD/MM/YYYY') {
  const d = parseDate(dateStr, fmt) || new Date();
  d.setDate(d.getDate() + days);
  return formatDate(d, fmt);
}

export function dueDate(terms = 30, fmt = 'DD/MM/YYYY') {
  const d = new Date();
  d.setDate(d.getDate() + parseInt(terms));
  return formatDate(d, fmt);
}

export function isOverdue(dueDateStr, fmt = 'DD/MM/YYYY') {
  const d = parseDate(dueDateStr, fmt);
  if (!d) return false;
  return d < new Date();
}

export function daysBetween(dateStr1, dateStr2, fmt = 'DD/MM/YYYY') {
  const d1 = parseDate(dateStr1, fmt);
  const d2 = parseDate(dateStr2, fmt);
  if (!d1 || !d2) return null;
  return Math.round((d2 - d1) / (1000 * 60 * 60 * 24));
}

// ── Invoice totals ────────────────────────────────────────────────────────
export function calcTotals(items = [], taxRate = 20, discountPct = 0) {
  const subtotal  = items.reduce((s, i) => s + (parseFloat(i.qty) || 0) * (parseFloat(i.price) || 0), 0);
  const tax       = items.reduce((s, i) => {
    if (!i.taxable) return s;
    return s + (parseFloat(i.qty) || 0) * (parseFloat(i.price) || 0) * (taxRate / 100);
  }, 0);
  const discAmt   = subtotal * ((parseFloat(discountPct) || 0) / 100);
  const grand     = subtotal + tax - discAmt;
  return { subtotal, tax, discount: discAmt, grand };
}

// ── Status helpers ────────────────────────────────────────────────────────
export function statusColor(status) {
  return {
    Paid:     '#00e676',
    Overdue:  '#ef4444',
    Unpaid:   '#f59e0b',
    Draft:    '#6b7280',
  }[status] || '#6b7280';
}

export function statusBg(status) {
  return {
    Paid:     '#00e67622',
    Overdue:  '#ef444422',
    Unpaid:   '#f59e0b22',
    Draft:    '#6b728022',
  }[status] || '#6b728022';
}

// ── Avg days to pay ───────────────────────────────────────────────────────
export function avgDaysToPay(clientName, invoices, fmt = 'DD/MM/YYYY') {
  const deltas = invoices
    .filter(h => (h.client_name || '').toLowerCase() === clientName.toLowerCase() &&
                  h.status === 'Paid' && h.paid_date && h.date)
    .map(h => daysBetween(h.date, h.paid_date, fmt))
    .filter(d => d !== null && d > 0);
  if (!deltas.length) return null;
  return Math.round(deltas.reduce((a, b) => a + b, 0) / deltas.length);
}

// ── CSV export ────────────────────────────────────────────────────────────
export function invoicesToCSV(invoices) {
  const headers = ['Invoice #','Client','Date','Due Date','Total','Status'];
  const rows    = invoices.map(h => [
    h.number, h.client_name || '', h.date || '', h.due_date || '',
    h.total || 0, h.status || '',
  ]);
  return [headers, ...rows].map(r => r.map(v => `"${v}"`).join(',')).join('\n');
}

// ── Download helpers ──────────────────────────────────────────────────────
export function downloadJSON(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  downloadBlob(blob, filename);
}

export function downloadText(text, filename, type = 'text/csv') {
  const blob = new Blob([text], { type });
  downloadBlob(blob, filename);
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a   = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

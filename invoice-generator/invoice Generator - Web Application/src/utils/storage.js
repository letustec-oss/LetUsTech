// ── Storage keys ──────────────────────────────────────────────────────────
const KEYS = {
  settings: 'ig_settings',
  invoices: 'ig_invoices',
  clients:  'ig_clients',
  expenses: 'ig_expenses',
  counter:  'ig_counter',
};

const DEFAULT_SETTINGS = {
  // EmailJS email sending
  emailjs_service_id:      '',
  emailjs_template_id:     '',
  emailjs_public_key:      '',
  email_from_name:         '',
  email_reply_to:          '',
  company_name:    '',
  company_email:   '',
  company_phone:   '',
  company_address: '',
  company_website: '',
  vat_number:      '',
  bank_name:       '',
  bank_sort_code:  '',
  bank_account:    '',
  bank_reference:  '',
  currency_symbol: '£',
  tax_rate:        20,
  tax_label:       'VAT',
  payment_terms:   30,
  invoice_prefix:  'INV',
  invoice_start:   1000,
  date_format:     'DD/MM/YYYY',
  theme_accent:    '#00e676',
  invoice_template:'Professional',
  default_notes:   'Thank you for your business. Payment is due within {terms} days.',
};

// ── Generic helpers ───────────────────────────────────────────────────────
function load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw);
  } catch { return fallback; }
}

function save(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
}

// ── Settings ──────────────────────────────────────────────────────────────
export function loadSettings() {
  const saved = load(KEYS.settings, {});
  return { ...DEFAULT_SETTINGS, ...saved };
}
export function saveSettings(s) { save(KEYS.settings, s); }
export { DEFAULT_SETTINGS };

// ── Invoices ──────────────────────────────────────────────────────────────
export function loadInvoices() { return load(KEYS.invoices, []); }
export function saveInvoices(list) { save(KEYS.invoices, list.slice(0, 500)); }

export function saveInvoice(inv) {
  const list = loadInvoices().filter(h => h.number !== inv.number);
  list.unshift(inv);
  saveInvoices(list);
}

// ── Clients ───────────────────────────────────────────────────────────────
export function loadClients() { return load(KEYS.clients, []); }
export function saveClients(list) { save(KEYS.clients, list); }

export function saveClient(client) {
  const list = loadClients().filter(c => c.name !== client.name);
  list.push(client);
  saveClients(list);
}

// ── Expenses ──────────────────────────────────────────────────────────────
export function loadExpenses() { return load(KEYS.expenses, []); }
export function saveExpenses(list) { save(KEYS.expenses, list); }

// ── Counter ───────────────────────────────────────────────────────────────
export function nextInvNum(settings) {
  const start  = parseInt(settings.invoice_start) || 1000;
  const prefix = settings.invoice_prefix || 'INV';
  const n      = load(KEYS.counter, { next: start }).next || start;
  return `${prefix}-${String(n).padStart(4, '0')}`;
}

export function bumpCounter(settings) {
  const start = parseInt(settings.invoice_start) || 1000;
  const cur   = load(KEYS.counter, { next: start });
  save(KEYS.counter, { next: (cur.next || start) + 1 });
}

// ── Full export/import ────────────────────────────────────────────────────
export function exportAllData() {
  return {
    settings: loadSettings(),
    invoices: loadInvoices(),
    clients:  loadClients(),
    expenses: loadExpenses(),
    exportedAt: new Date().toISOString(),
    version: '1.0',
  };
}

export function importAllData(data, mode = 'replace') {
  if (mode === 'replace') {
    if (data.settings) saveSettings(data.settings);
    if (data.invoices) saveInvoices(data.invoices);
    if (data.clients)  saveClients(data.clients);
    if (data.expenses) saveExpenses(data.expenses);
  } else {
    // Merge
    if (data.settings) saveSettings({ ...loadSettings(), ...data.settings });
    if (data.invoices) {
      const existing = new Set(loadInvoices().map(h => h.number));
      const merged   = [...loadInvoices(), ...(data.invoices || []).filter(h => !existing.has(h.number))];
      saveInvoices(merged);
    }
    if (data.clients) {
      const existing = new Set(loadClients().map(c => c.name));
      const merged   = [...loadClients(), ...(data.clients || []).filter(c => !existing.has(c.name))];
      saveClients(merged);
    }
    if (data.expenses) saveExpenses([...loadExpenses(), ...(data.expenses || [])]);
  }
}

// ── Recurring ─────────────────────────────────────────────────────────────
export function loadRecurring() { return load('ig_recurring', []); }
export function saveRecurring(list) { save('ig_recurring', list); }

import React, { useState } from 'react';

// ═══════════════════════════════════════════════════════════════════
// SHARED COMPONENTS
// ═══════════════════════════════════════════════════════════════════

function HelpSection({ icon, title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ background: 'var(--bg-card)', borderRadius: 12, border: '1px solid var(--border)', marginBottom: 10, overflow: 'hidden' }}>
      <div onClick={() => setOpen(o => !o)} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', cursor: 'pointer', userSelect: 'none' }}>
        <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>{icon}</span>
        <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem', flex: 1, lineHeight: 1.3 }}>{title}</span>
        <span style={{ color: 'var(--text-dim)', fontSize: '1rem', transform: open ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s', flexShrink: 0 }}>›</span>
      </div>
      {open && <div style={{ padding: '4px 16px 16px', borderTop: '1px solid var(--border)' }}>{children}</div>}
    </div>
  );
}

function P({ children, style }) {
  return <p style={{ fontSize: '0.84rem', color: 'var(--text-med)', lineHeight: 1.75, margin: '10px 0 0', ...style }}>{children}</p>;
}

function H({ children }) {
  return <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)', margin: '14px 0 4px' }}>{children}</div>;
}

function Note({ children, type = 'info' }) {
  const s = { info: { bg: '#0d1a2e', border: '#3b82f640', color: '#93c5fd' }, success: { bg: '#0d1a0d', border: '#00e67640', color: '#00e676' }, warning: { bg: '#1a1000', border: '#f59e0b40', color: '#f59e0b' }, danger: { bg: '#1a0808', border: '#ef444440', color: '#ef4444' } }[type];
  return <div style={{ background: s.bg, border: `1px solid ${s.border}`, borderRadius: 8, padding: '10px 14px', margin: '12px 0 0', fontSize: '0.81rem', color: s.color, lineHeight: 1.65 }}>{children}</div>;
}

function Step({ n, title, children }) {
  return (
    <div style={{ display: 'flex', gap: 14, marginTop: 14 }}>
      <div style={{ width: 26, height: 26, borderRadius: '50%', background: 'var(--accent)', color: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '0.82rem', flexShrink: 0, marginTop: 1 }}>{n}</div>
      <div style={{ flex: 1 }}>
        {title && <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--text)', marginBottom: 4 }}>{title}</div>}
        <div style={{ fontSize: '0.83rem', color: 'var(--text-med)', lineHeight: 1.7 }}>{children}</div>
      </div>
    </div>
  );
}

function Tip({ children }) {
  return <div style={{ display: 'flex', gap: 8, marginTop: 10, padding: '8px 12px', background: 'var(--bg-hover)', borderRadius: 8, borderLeft: '3px solid var(--accent)' }}><span style={{ fontSize: '0.82rem', flexShrink: 0 }}>💡</span><span style={{ fontSize: '0.81rem', color: 'var(--text-med)', lineHeight: 1.6 }}>{children}</span></div>;
}

function CodeBlock({ children }) {
  return <div style={{ background: '#0d1117', borderRadius: 8, padding: '10px 14px', margin: '8px 0 0', fontFamily: 'Consolas, monospace', fontSize: '0.78rem', color: 'var(--accent)', lineHeight: 1.8, whiteSpace: 'pre', overflowX: 'auto' }}>{children}</div>;
}

function Divider() { return <div style={{ height: 1, background: 'var(--border)', margin: '14px 0' }} />; }

function HelpPage({ title, back, backLabel = 'Help', children }) {
  return (
    <div className="page" style={{ paddingTop: 0 }}>
      <div className="top-bar">
        <button className="back-btn" onClick={back}>‹ {backLabel}</button>
        <div className="top-bar-title">{title}</div>
      </div>
      <div style={{ padding: '16px 16px 110px' }}>{children}</div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// HUB
// ═══════════════════════════════════════════════════════════════════

export function HelpHub({ setPage }) {
  const sections = [
    { icon: '🚀', label: 'Quick Start Guide', sub: 'New here? Start with this — 5 min setup', page: 'help-quickstart' },
    { icon: '📄', label: 'Creating Invoices', sub: 'Full form, quick invoice, line items, previewing', page: 'help-invoices' },
    { icon: '💷', label: 'Getting Paid', sub: 'Mark paid, partial payments, overdue detection', page: 'help-payments' },
    { icon: '🔔', label: 'Reminders & Late Fees', sub: 'Chase invoices, copy messages, fee calculator', page: 'help-reminders' },
    { icon: '👥', label: 'Managing Clients', sub: 'Address book, payment history, reliability scores', page: 'help-clients' },
    { icon: '💸', label: 'Expenses & Receipts', sub: 'Log costs, scan receipts with camera, charts', page: 'help-expenses' },
    { icon: '📈', label: 'Reports & VAT', sub: 'Revenue, profit, HMRC 9-box VAT return', page: 'help-reports' },
    { icon: '🔁', label: 'Recurring Invoices', sub: 'Retainers, monthly schedules, auto-drafts', page: 'help-recurring' },
    { icon: '📧', label: 'Sending Emails', sub: 'EmailJS setup, share sheet, send direct', page: 'help-email' },
    { icon: '⚖️', label: 'UK VAT Law', sub: '13 required fields, VAT rates, when to register', page: 'help-vat' },
    { icon: '☁️', label: 'Backup & Restore', sub: 'Export, import, move to new device', page: 'help-backup' },
    { icon: '📱', label: 'Mobile Features', sub: 'PWA install, share sheet, search, notifications', page: 'help-mobile' },
    { icon: '❓', label: 'FAQ & Troubleshooting', sub: 'Common problems and fixes', page: 'help-faq' },
  ];
  return (
    <div className="page" style={{ paddingTop: 0 }}>
      <div className="top-bar">
        <button className="back-btn" onClick={() => setPage('more')}>‹ More</button>
        <div className="top-bar-title">Help Centre</div>
      </div>
      <div style={{ padding: '16px 16px 100px' }}>
        <div style={{ background: '#0d1a0d', border: '1px solid var(--accent)', borderRadius: 12, padding: '14px 16px', marginBottom: 20 }}>
          <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, color: 'var(--accent)', marginBottom: 6 }}>🧾 Invoice Generator — Help Centre</div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', lineHeight: 1.6 }}>Free, offline invoicing for UK freelancers and small businesses. Every guide is written specifically for this app. Tap any topic for the full guide.</div>
        </div>
        {sections.map(({ icon, label, sub, page }) => (
          <div key={page} onClick={() => setPage(page)} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 12, marginBottom: 8, cursor: 'pointer' }}>
            <div style={{ width: 42, height: 42, borderRadius: 10, background: 'var(--bg-hover)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.3rem', flexShrink: 0 }}>{icon}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text)' }}>{label}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: 2 }}>{sub}</div>
            </div>
            <span style={{ color: 'var(--text-dim)', fontSize: '1rem' }}>›</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// QUICK START
// ═══════════════════════════════════════════════════════════════════

export function HelpQuickStart({ setPage }) {
  return (
    <HelpPage title="🚀 Quick Start" back={() => setPage('help-hub')}>
      <Note type="success">Do steps 1–3 before anything else. You can fill in the rest as you go.</Note>

      <HelpSection icon="🏢" title="Step 1 — Enter your business details" defaultOpen>
        <P>Go to <strong>More → Settings → 🏢 Business tab</strong>. Fill in your Company Name, Email, Phone, Address, VAT Number (if VAT registered), and Website.</P>
        <P>Your company name and address print on every invoice. Your address is legally required on UK VAT invoices. If you're not VAT registered, leave the VAT Number blank.</P>
        <Tip>Tap Save at the top right of the Settings page after making changes. Nothing saves automatically.</Tip>
      </HelpSection>

      <HelpSection icon="🏦" title="Step 2 — Add your bank details">
        <P>Still in Settings → Business, scroll to Banking & Payments. Fill in Sort Code, Account Number, Bank Name and a Reference (your business name works well).</P>
        <P>These appear in a Payment Details section at the bottom of every invoice PDF so clients know exactly where to send money by bank transfer.</P>
        <Note>If you accept PayPal or Stripe, add payment links in Settings → Invoicing. They appear as clickable links on the PDF.</Note>
      </HelpSection>

      <HelpSection icon="💰" title="Step 3 — Set your tax rate and currency">
        <P>Settings → 💰 Invoicing → Tax & Currency:</P>
        <div style={{ margin: '8px 0', fontSize: '0.83rem', color: 'var(--text-med)', lineHeight: 1.9 }}>
          <div>• <strong style={{ color: 'var(--text)' }}>Currency Symbol</strong> — £ for UK</div>
          <div>• <strong style={{ color: 'var(--text)' }}>Tax Rate</strong> — 20 for standard UK VAT, 0 if not VAT registered</div>
          <div>• <strong style={{ color: 'var(--text)' }}>Tax Label</strong> — VAT for UK businesses</div>
          <div>• <strong style={{ color: 'var(--text)' }}>Payment Terms</strong> — 30 = payment due 30 days from invoice date (UK standard)</div>
          <div>• <strong style={{ color: 'var(--text)' }}>Invoice Prefix</strong> — INV by default. Change to your initials if you prefer.</div>
        </div>
      </HelpSection>

      <HelpSection icon="👤" title="Step 4 — Add your first client">
        <P>Go to <strong>Clients → ＋</strong>. Enter their name, email, phone and billing address. Tap Save.</P>
        <P>Once saved, you can load all their details onto any invoice in one tap using the "Load ›" button. No retyping needed.</P>
        <Tip>You can also save a client directly from the invoice form — fill in their details and tap "👥 Save to Address Book".</Tip>
      </HelpSection>

      <HelpSection icon="📄" title="Step 5 — Create your first invoice">
        <Step n="1" title="Tap New Invoice in the bottom nav" />
        <Step n="2" title="Load a saved client or type their details" />
        <Step n="3" title="Check the dates — auto-filled to today and +30 days" />
        <Step n="4" title="Add line items — description, qty and price for each item" />
        <Step n="5" title="Review the total — updates live as you type" />
        <Step n="6" title='Tap "⬇ PDF" top right to generate and share the invoice' />
        <Note type="success">The invoice saves automatically when you export it. Find it in the Invoices list.</Note>
      </HelpSection>

      <HelpSection icon="✅" title="Step 6 — Mark invoices as paid">
        <P>When payment arrives, go to <strong>Invoices</strong>, tap the invoice row to expand it, and tap <strong>✓ Mark Paid</strong>. The date is recorded. This updates your Dashboard totals and the client's payment score.</P>
      </HelpSection>
    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// CREATING INVOICES
// ═══════════════════════════════════════════════════════════════════

export function HelpInvoices({ setPage }) {
  return (
    <HelpPage title="📄 Creating Invoices" back={() => setPage('help-hub')}>

      <HelpSection icon="⚡" title="Quick Invoice — 60 second invoicing" defaultOpen>
        <P>Go to <strong>More → ⚡ Quick Invoice</strong> for the fastest way to invoice on-site.</P>
        <Step n="1" title="Select or type the client name">Use the Quick Load dropdown to fill in a saved client automatically.</Step>
        <Step n="2" title="Add a description, price and quantity">E.g. Description = "Plumbing repair", Price = £75, Qty = 3 hours. Total calculates live.</Step>
        <Step n="3" title="Toggle VAT on or off">Tick VAT if this job is taxable. Total updates immediately.</Step>
        <Step n="4" title='Tap "📤 Send Invoice"'>Generates the PDF and opens the native share sheet — share via WhatsApp, email, iMessage or save it.</Step>
        <Tip>The invoice saves automatically. Find it in the Invoices list afterwards.</Tip>
      </HelpSection>

      <HelpSection icon="📄" title="Full invoice form — every field explained">
        <H>Invoice number</H>
        <P>Auto-assigned from your counter. Tap the INV-XXXX field to edit it manually. The counter advances after each save or export so the next invoice gets the next number.</P>

        <H>Status</H>
        <P>Unpaid by default. Options: Draft (not counted in totals), Unpaid, Paid, Overdue. Change it using the dropdown top-right of the form.</P>

        <H>Invoice date and due date</H>
        <P>Both auto-fill — today's date and today + your payment terms. Tap either field to edit. Format: DD/MM/YYYY unless changed in Settings.</P>

        <H>PO / Reference</H>
        <P>Optional field for your client's purchase order number or project reference. Appears on the PDF for their accounting records.</P>

        <H>Loading a saved client</H>
        <P>Tap <strong>Load ›</strong> (top right of the Client Details card) to open your address book and load a client in one tap.</P>

        <H>Line items — the core of your invoice</H>
        <div style={{ margin: '8px 0', fontSize: '0.83rem', color: 'var(--text-med)', lineHeight: 1.9 }}>
          <div>• <strong style={{ color: 'var(--text)' }}>Description</strong> — what you did or supplied</div>
          <div>• <strong style={{ color: 'var(--text)' }}>Qty</strong> — number of units, hours, days etc.</div>
          <div>• <strong style={{ color: 'var(--text)' }}>Price</strong> — the unit price (not the total). £50/hr × 3 = £150 total</div>
          <div>• <strong style={{ color: 'var(--text)' }}>VAT checkbox</strong> — tick if this item is taxable at your standard rate</div>
        </div>
        <P>Tap <strong>+ Add Line</strong> to add more rows. Tap ✕ to remove a row. You can mix taxable and non-taxable items on the same invoice.</P>

        <H>Discount %</H>
        <P>Applies a percentage discount to the whole invoice. 10% on a £500 invoice deducts £50.</P>

        <H>Partial payment</H>
        <P>Tap <strong>💛 Record Payment</strong> to record a deposit or part-payment. The balance is shown and printed on the PDF.</P>

        <H>Notes & Terms</H>
        <P>Free text at the bottom of the PDF. Pre-filled from your default notes in Settings. Edit per-invoice for payment instructions, project references, thanks etc.</P>
      </HelpSection>

      <HelpSection icon="👁" title="Previewing before you export">
        <P>Scroll to the bottom of the invoice form and tap <strong>👁 Preview Invoice</strong> to see exactly what the PDF will look like — company header, client details, all line items, totals, bank details and notes — before generating the file.</P>
        <P>From the preview, tap <strong>⬇ Export</strong> to generate and share, or <strong>✕ Close</strong> to go back and edit.</P>
        <Tip>Always preview before sending to a new client to check your branding and details are correct.</Tip>
      </HelpSection>

      <HelpSection icon="💾" title="Saving drafts">
        <P>Tap <strong>💾 Save Draft</strong> to save without sending. Drafts appear in the Invoices list with a grey Draft badge and don't count toward your revenue totals.</P>
        <P>To continue: go to Invoices, tap the draft row to expand it, tap <strong>✏️ Edit</strong>. All your details are restored exactly as left.</P>
        <Note>Saving a draft advances the invoice counter so the next new invoice gets a fresh number — preventing two invoices with the same number.</Note>
      </HelpSection>

      <HelpSection icon="⧉" title="Duplicating an invoice">
        <P>In the Invoices list, tap a row to expand it, then tap <strong>⧉ Duplicate</strong>. Creates a new draft with all the same details but a new invoice number and today's date. Ideal for regular repeat work.</P>
      </HelpSection>

      <HelpSection icon="🔢" title="Invoice numbering rules">
        <P>Every invoice gets a unique sequential number: INV-1001, INV-1002, INV-1003. Change the prefix and starting number in Settings → Invoicing.</P>
        <Note type="warning">UK law requires sequential numbers with no gaps. HMRC can ask about missing numbers during a tax investigation. Don't skip numbers or edit them out of sequence.</Note>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// GETTING PAID
// ═══════════════════════════════════════════════════════════════════

export function HelpPayments({ setPage }) {
  return (
    <HelpPage title="💷 Getting Paid" back={() => setPage('help-hub')}>

      <HelpSection icon="✅" title="Marking an invoice as paid" defaultOpen>
        <P>Go to <strong>Invoices</strong>, tap the invoice row to expand it, then tap <strong>✓ Mark Paid</strong>.</P>
        <P>Automatically: status → Paid, payment date recorded, invoice removed from Outstanding total, client's avg days-to-pay updated, Revenue on Dashboard increases.</P>
        <Tip>Mark invoices paid as soon as money arrives — it keeps your Dashboard and reports accurate.</Tip>
      </HelpSection>

      <HelpSection icon="💛" title="Partial payments — deposits and stage payments">
        <Step n="1" title="Open the invoice form">From Invoices, tap the row then ✏️ Edit.</Step>
        <Step n="2" title="Tap 💛 Record Payment in the Partial Payment section">Enter the amount received. The balance calculates instantly.</Step>
        <Step n="3" title="Save and re-export">The PDF will show: Gross Total → Amount Paid → Balance Due. Send the updated PDF to your client.</Step>
        <P>If the payment equals the full invoice total, the status changes to Paid automatically.</P>
      </HelpSection>

      <HelpSection icon="🔴" title="How overdue detection works">
        <P>Every time you open the Invoices page, the app checks all Unpaid invoices. Any with a due date in the past are automatically changed to <strong>Overdue</strong> (red badge).</P>
        <P>A red notification banner appears on the Dashboard showing how many are overdue and the total amount outstanding.</P>
      </HelpSection>

      <HelpSection icon="📊" title="Dashboard totals — what each number means">
        <div style={{ margin: '8px 0' }}>
          {[
            ['var(--accent)', 'Revenue', 'Total of all Paid invoices. Money you have actually received.'],
            ['var(--gold)',   'Outstanding', 'Total of all Unpaid and Overdue invoices. Money owed to you.'],
            ['var(--red)',    'Overdue', 'Count of invoices past their due date. Tap to go to Reminders.'],
            ['var(--text)',   'Expenses', 'Total logged expenses. Revenue minus this = net profit.'],
          ].map(([color, label, desc]) => (
            <div key={label} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: '0.83rem' }}>
              <span style={{ fontWeight: 700, color, display: 'block' }}>{label}</span>
              <span style={{ color: 'var(--text-dim)' }}>{desc}</span>
            </div>
          ))}
        </div>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// REMINDERS & LATE FEES
// ═══════════════════════════════════════════════════════════════════

export function HelpReminders({ setPage }) {
  return (
    <HelpPage title="🔔 Reminders & Late Fees" back={() => setPage('help-hub')}>

      <HelpSection icon="🔔" title="The Overdue Reminders page" defaultOpen>
        <P>Go to <strong>More → Overdue Reminders</strong>. Shows every overdue invoice sorted by how many days late — most overdue at top.</P>
        <P>For each: invoice number, client, amount, days overdue, email address, and action buttons: 📧 Email, 📋 Copy Message, ✓ Mark Paid, ✏️ Edit.</P>
      </HelpSection>

      <HelpSection icon="📧" title="Sending a reminder email">
        <P>Tap <strong>📧 Email</strong> on any overdue invoice. Opens your phone's email app with a pre-written reminder filled in — invoice number, amount, due date, polite chase message. Edit and send.</P>
        <Tip>If you've set up EmailJS (Settings → Email), you can also send directly from inside the app without leaving.</Tip>
      </HelpSection>

      <HelpSection icon="📋" title="Copying a reminder for WhatsApp">
        <P>Tap <strong>📋 Copy Message</strong>. A professional reminder is copied to your clipboard — paste directly into WhatsApp, text message or any app.</P>
        <CodeBlock>{`Hi Tom,

This is a friendly reminder that invoice
INV-1005 for £144.00 was due on
15/04/2026 and is now 7 days overdue.

Please arrange payment at your earliest
convenience.

Kind regards,
Dean Wilson`}</CodeBlock>
      </HelpSection>

      <HelpSection icon="🧮" title="Late fee calculator">
        <P>Go to <strong>More → Late Fee Calculator</strong>. Enter invoice total and days overdue. Shows:</P>
        <div style={{ margin: '8px 0', fontSize: '0.83rem', color: 'var(--text-med)', lineHeight: 1.8 }}>
          <div>• Your custom fee (your % or fixed amount)</div>
          <div>• UK statutory interest — 8% above Bank of England base rate per year</div>
          <div>• Fixed compensation — £40 (under £1k), £70 (£1k–£10k), £100 (over £10k)</div>
        </div>
        <Note type="info">UK businesses can legally charge statutory interest on late B2B payments under the Late Payment of Commercial Debts Act 1998 — it applies automatically without needing it in your contract.</Note>
        <P>To add a late fee: Invoices → ✏️ Edit the invoice → add a new line item for the fee amount.</P>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// CLIENTS
// ═══════════════════════════════════════════════════════════════════

export function HelpClients({ setPage }) {
  return (
    <HelpPage title="👥 Managing Clients" back={() => setPage('help-hub')}>

      <HelpSection icon="➕" title="Adding a client" defaultOpen>
        <P>Go to <strong>Clients → ＋</strong>. Fill in name, email, phone and billing address. Tap Save.</P>
        <P>Name = appears on invoices. Email = used for sending reminders. Address = required on UK VAT invoices.</P>
        <Tip>Add clients from the invoice form too — fill in details and tap "👥 Save to Address Book".</Tip>
      </HelpSection>

      <HelpSection icon="📋" title="Client detail page — full payment history">
        <P>Tap any client row to open their detail page. Shows:</P>
        <div style={{ margin: '8px 0', fontSize: '0.83rem', color: 'var(--text-med)', lineHeight: 1.9 }}>
          <div>• <strong style={{ color: 'var(--text)' }}>Total billed</strong> — lifetime invoiced amount</div>
          <div>• <strong style={{ color: 'var(--text)' }}>Outstanding</strong> — unpaid invoices right now</div>
          <div>• <strong style={{ color: 'var(--text)' }}>Avg Days to Pay</strong> — how quickly they typically pay (from payment history)</div>
          <div>• Every invoice ever sent, with status, amount and dates</div>
        </div>
        <P>From here, tap <strong>＋ Invoice</strong> to create a new invoice with their details pre-filled.</P>
      </HelpSection>

      <HelpSection icon="📊" title="Average days to pay — colour codes">
        {[['var(--accent)', '0–7 days', 'Excellent — pays almost immediately'], ['#22d3ee', '8–14 days', 'Good — pays within 2 weeks'], ['var(--gold)', '15–30 days', 'Average — takes up to a month'], ['var(--red)', '30+ days', 'Slow — consistently late']].map(([c, r, l]) => (
          <div key={r} style={{ display: 'flex', gap: 12, marginTop: 8, alignItems: 'center' }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: c, flexShrink: 0 }} />
            <span style={{ color: 'var(--text)', fontWeight: 600, fontSize: '0.83rem', width: 70 }}>{r}</span>
            <span style={{ color: 'var(--text-dim)', fontSize: '0.83rem' }}>{l}</span>
          </div>
        ))}
        <Note type="info">Score only calculates from invoices where you've recorded a paid date. Same-day payments (0 days) are excluded as they usually mean you marked it paid immediately after creating the invoice.</Note>
      </HelpSection>

      <HelpSection icon="✏️" title="Editing or deleting a client">
        <P>Tap <strong>Edit</strong> next to any client to update their details. Tap <strong>✕</strong> to delete (with confirmation).</P>
        <Note type="warning">Deleting a client does not delete their invoices — they stay in your history with the client name intact.</Note>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// EXPENSES & RECEIPTS
// ═══════════════════════════════════════════════════════════════════

export function HelpExpenses({ setPage }) {
  return (
    <HelpPage title="💸 Expenses & Receipts" back={() => setPage('help-hub')}>

      <HelpSection icon="➕" title="Logging an expense manually" defaultOpen>
        <P>Go to <strong>Expenses → ＋</strong>. Fill in description, amount, category (General, Software, Travel, Equipment, Marketing, Office, Professional Services, Food & Drink, Other) and date.</P>
        <Tip>Log expenses on the day you buy them. It takes 10 seconds and saves hours at tax time.</Tip>
      </HelpSection>

      <HelpSection icon="📷" title="Scanning receipts with the camera">
        <P>Go to <strong>More → 📷 Scan Receipt</strong>.</P>
        <Step n="1" title="Point camera at the receipt">Keep it flat and well-lit. A green frame appears as a guide.</Step>
        <Step n="2" title="Tap the white capture button">Or tap Gallery to use an existing photo.</Step>
        <Step n="3" title='Tap "✨ Scan Receipt"'>AI reads the merchant, total, category and date automatically.</Step>
        <Step n="4" title="Review and confirm">Check the pre-filled details. Edit anything that looks wrong.</Step>
        <Step n="5" title='Tap "💾 Save Expense"'>Done. Saved with the receipt photo attached.</Step>
        <Note type="info">Receipt scanning needs an internet connection to send the photo to AI. The photo is not stored externally.</Note>
        <Note type="warning">Camera not opening? Grant camera permission: iOS: Settings → Safari → Camera → Allow. Android: tap the lock icon in the browser address bar → Permissions → Camera → Allow.</Note>
      </HelpSection>

      <HelpSection icon="📊" title="Expense categories chart">
        <P>The colour-coded bar chart at the top of the Expenses page shows each category as a proportion of total spend — helping you see at a glance where your money goes.</P>
      </HelpSection>

      <HelpSection icon="💰" title="How expenses affect your numbers">
        <P>Revenue (paid invoices) minus Expenses = <strong style={{ color: 'var(--accent)' }}>Net Profit</strong> shown on the Dashboard and in Reports.</P>
        <Tip>For VAT-registered businesses, input VAT on expenses can be reclaimed. Reports estimates this in Box 4 of the VAT Return based on your tax rate.</Tip>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// REPORTS & VAT
// ═══════════════════════════════════════════════════════════════════

export function HelpReports({ setPage }) {
  return (
    <HelpPage title="📈 Reports & VAT" back={() => setPage('help-hub')}>

      <HelpSection icon="📈" title="What the Reports page shows" defaultOpen>
        <P>Go to <strong>More → Reports</strong>. Shows figures for the current calendar year:</P>
        {[['Revenue', 'Total of all Paid invoices this year'], ['VAT Collected', 'VAT charged on paid invoices'], ['Expenses', 'Total logged expenses this year'], ['Net Profit', 'Revenue minus expenses — your actual take-home before personal tax']].map(([l, d]) => (
          <div key={l} style={{ padding: '7px 0', borderBottom: '1px solid var(--border)', fontSize: '0.83rem' }}>
            <span style={{ fontWeight: 600, color: 'var(--text)', display: 'block' }}>{l}</span>
            <span style={{ color: 'var(--text-dim)' }}>{d}</span>
          </div>
        ))}
      </HelpSection>

      <HelpSection icon="📊" title="Monthly revenue chart">
        <P>Bar chart of revenue by month. Taller bars = more revenue. Spot busy/quiet periods, plan cash flow, decide when to push for new work.</P>
        <Tip>If a month looks low, check if all invoices were marked Paid. Draft and Unpaid invoices don't count toward Revenue.</Tip>
      </HelpSection>

      <HelpSection icon="🇬🇧" title="HMRC VAT Return — the 9 boxes explained">
        <P>Pre-calculated from your invoice data. Share these with your accountant or use as reference when filing through Making Tax Digital.</P>
        {[['Box 1', 'VAT due on your sales — the VAT you charged clients'], ['Box 2', 'VAT on EU acquisitions — usually £0 for UK-only businesses'], ['Box 3', 'Total VAT due — Box 1 + Box 2'], ['Box 4', 'VAT you can reclaim on purchases — estimated from your expenses'], ['Box 5', 'Net VAT to pay HMRC — Box 3 minus Box 4'], ['Box 6', 'Total sales, excluding VAT'], ['Box 7', 'Total purchases, excluding VAT'], ['Box 8', 'Goods supplied to EU — usually £0'], ['Box 9', 'Goods acquired from EU — usually £0']].map(([box, desc]) => (
          <div key={box} style={{ display: 'flex', gap: 12, padding: '7px 0', borderBottom: '1px solid var(--border)', fontSize: '0.82rem' }}>
            <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, color: 'var(--accent)', width: 46, flexShrink: 0 }}>{box}</span>
            <span style={{ color: 'var(--text-med)', lineHeight: 1.5 }}>{desc}</span>
          </div>
        ))}
        <Note type="warning">These are a pre-calculation for your records only. File VAT returns through HMRC's Making Tax Digital service — not this app. Always verify with your accountant.</Note>
      </HelpSection>

      <HelpSection icon="📥" title="Exporting for your accountant">
        <P>Tap <strong>📊 Export CSV</strong> at the bottom of Reports to download a spreadsheet of all paid invoices. Most accountants also want your expenses and the VAT figures from the 9-box summary.</P>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// RECURRING INVOICES
// ═══════════════════════════════════════════════════════════════════

export function HelpRecurring({ setPage }) {
  return (
    <HelpPage title="🔁 Recurring Invoices" back={() => setPage('help-hub')}>

      <HelpSection icon="🔁" title="What are recurring invoices?" defaultOpen>
        <P>Schedules that automatically create draft invoices at regular intervals — weekly, monthly, quarterly or annually. Ideal for monthly retainers, regular maintenance contracts, and any work billed at the same rate repeatedly.</P>
      </HelpSection>

      <HelpSection icon="➕" title="Setting up a schedule">
        <P>Go to <strong>More → Recurring → ＋</strong>.</P>
        <Step n="1" title="Select the client">Loads email and address automatically from your address book.</Step>
        <Step n="2" title="Enter a description">Becomes the line item on each invoice. E.g. "Monthly website maintenance retainer".</Step>
        <Step n="3" title="Set amount and frequency">Price per invoice and how often: Weekly, Monthly, Quarterly or Annually.</Step>
        <Step n="4" title="Set the first due date">When the first invoice should be created. Use today's date to generate one immediately.</Step>
        <Step n="5" title="Tap Save">Schedule is created and tracked automatically.</Step>
      </HelpSection>

      <HelpSection icon="⚡" title="Generating drafts when they're due">
        <P>When schedules are due, a green banner appears: <em>"⚡ 2 invoices due — Ready to generate"</em>. Tap <strong>Generate</strong> to create draft invoices for all due schedules at once.</P>
        <P>Each draft is saved with today's date, your payment terms due date, the client's details and the schedule amount. The next date advances automatically.</P>
        <P>Go to the Invoices list, find the drafts, review them, then export and send.</P>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// EMAIL SETUP
// ═══════════════════════════════════════════════════════════════════

export function HelpEmail({ setPage }) {
  return (
    <HelpPage title="📧 Sending Emails" back={() => setPage('help-hub')}>

      <HelpSection icon="📤" title="Two ways to send invoices by email" defaultOpen>
        <H>Option 1 — Share sheet (easiest, works right now)</H>
        <P>Tap ⬇ Export PDF on any invoice, then use the native share sheet to share the PDF via Mail, Gmail, WhatsApp, iMessage or any app. No setup required.</P>
        <Divider />
        <H>Option 2 — Send directly from the app (requires EmailJS)</H>
        <P>Sends a professional email with invoice details directly from within the app. One-time 5-minute setup. Free for 200 emails/month.</P>
      </HelpSection>

      <HelpSection icon="⚙️" title="Setting up EmailJS step by step">
        <Note type="info">EmailJS lets web apps send emails without a backend server. Free tier = 200 emails/month.</Note>
        <Step n="1" title="Create a free account">Go to emailjs.com and sign up.</Step>
        <Step n="2" title="Add your email service">EmailJS dashboard → Email Services → Add New Service. Connect Gmail or Outlook.</Step>
        <Step n="3" title="Create an email template">Email Templates → Create New. Set up:</Step>
        <CodeBlock>{`To:      {{to_email}}
From:    {{from_name}}
Reply:   {{reply_to}}
Subject: {{subject}}
Body:    {{message}}`}</CodeBlock>
        <Step n="4" title="Copy your three IDs">Service ID, Template ID, and Public Key (Account → General).</Step>
        <Step n="5" title="Paste into the app">Settings → 📧 Email tab → paste all three IDs and your From Name and Reply-To email → Save.</Step>
        <Note type="success">Once configured, ✅ EmailJS connected appears. You can now send invoices directly from the invoice form and Invoices list.</Note>
      </HelpSection>

      <HelpSection icon="📧" title="Sending an invoice email">
        <P>From the <strong>Invoices list</strong>: tap a row → expand → tap 📧 Email.</P>
        <P>From the <strong>invoice form</strong>: tap the small 📧 button in the top bar.</P>
        <P>A compose screen opens with To, Subject and Message pre-filled from the invoice data. Your bank details are included in the message automatically. Edit anything and tap <strong>📧 Send Invoice</strong>.</P>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// UK VAT LAW
// ═══════════════════════════════════════════════════════════════════

export function HelpVAT({ setPage }) {
  return (
    <HelpPage title="⚖️ UK VAT Law" back={() => setPage('help-hub')}>
      <Note>Covers UK VAT invoice requirements under HMRC Notice 700. Applies to VAT-registered businesses. Verify specifics with your accountant.</Note>

      <HelpSection icon="📋" title="The 13 required fields on a UK VAT invoice" defaultOpen>
        <P>A full UK VAT invoice must include ALL of:</P>
        {[['1','A unique, sequential invoice number'],['2','Your VAT registration number'],['3','The invoice date'],['4','The tax point if different from invoice date'],['5','Your business name and address'],['6','Customer name and address'],['7','Description of goods/services'],['8','Quantity and unit price per item (ex VAT)'],['9','Rate of any discount per item'],['10','VAT rate applied to each line'],['11','VAT amount per line'],['12','Total excluding VAT'],['13','Total VAT charged']].map(([n, t]) => (
          <div key={n} style={{ display: 'flex', gap: 10, marginTop: 8, padding: '5px 0', borderBottom: '1px solid var(--border)' }}>
            <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, color: 'var(--accent)', fontSize: '0.8rem', width: 20, flexShrink: 0 }}>{n}</span>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-med)', lineHeight: 1.5 }}>{t}</span>
          </div>
        ))}
        <div style={{ marginTop: 8, fontSize: '0.72rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>Source: HMRC Notice 700, Section 16</div>
      </HelpSection>

      <HelpSection icon="🔢" title="Invoice numbering rules">
        <H>Sequential — no gaps</H>
        <P>Numbers must run in order: INV-1001, INV-1002, INV-1003. You cannot skip or reuse numbers. HMRC investigates gaps.</P>
        <H>Format is your choice</H>
        <P>Any consistent system: INV-1001, 2026/001, DW-001. Change prefix and starting number in Settings → Invoicing.</P>
        <Note type="warning">If you delete an invoice, that number is gone. Note it as "cancelled" in your records — don't reuse it.</Note>
      </HelpSection>

      <HelpSection icon="💰" title="UK VAT rates">
        {[['20%','Standard rate','Most goods and services'],['5%','Reduced rate','Domestic fuel, children\'s car seats, energy-saving materials'],['0%','Zero rated','Most food, books, children\'s clothes, public transport'],['Exempt','Outside scope','Insurance, education, some healthcare']].map(([r, l, d]) => (
          <div key={r} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', gap: 10, alignItems: 'baseline', marginBottom: 2 }}>
              <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, color: 'var(--accent)', width: 52 }}>{r}</span>
              <span style={{ fontWeight: 700, fontSize: '0.87rem', color: 'var(--text)' }}>{l}</span>
            </div>
            <P style={{ margin: '0 0 0 62px', fontSize: '0.8rem' }}>{d}</P>
          </div>
        ))}
      </HelpSection>

      <HelpSection icon="📅" title="When to register for VAT">
        <H>Compulsory threshold</H>
        <P>Must register when taxable turnover exceeds <strong>£90,000</strong> in any rolling 12-month period (April 2024). Register within 30 days of exceeding this threshold.</P>
        <H>Voluntary registration</H>
        <P>You can register voluntarily below the threshold to reclaim VAT on business purchases — useful if your suppliers are VAT registered.</P>
        <H>Penalties</H>
        <P>Up to 15% of VAT unpaid from the date you should have registered. Register early at gov.uk/register-for-vat.</P>
      </HelpSection>

      <HelpSection icon="📅" title="VAT returns and Making Tax Digital">
        <P>Most businesses file quarterly. Deadline: 1 month and 7 days after the end of each VAT period.</P>
        <P>All VAT-registered businesses must use <strong>Making Tax Digital (MTD)</strong> — digital records and MTD-compatible software for filing. This app provides the figures; file through HMRC-approved MTD software.</P>
        <P>Keep all VAT records for at least <strong>6 years</strong> (5 years for sole traders on cash accounting).</P>
        <Note type="info">Export a full backup monthly and store it in cloud storage. Settings → Backup → Export All Data.</Note>
      </HelpSection>

      <HelpSection icon="🧾" title="Simplified VAT invoices (under £250)">
        <P>For total invoices of <strong>£250 or less</strong> (including VAT), you only need: your name/address/VAT number, date, description, total including VAT, and VAT rate. No need for customer details or per-line VAT breakdown.</P>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// BACKUP & RESTORE
// ═══════════════════════════════════════════════════════════════════

export function HelpBackup({ setPage }) {
  return (
    <HelpPage title="☁️ Backup & Restore" back={() => setPage('help-hub')}>

      <HelpSection icon="⚠️" title="IMPORTANT — read this first" defaultOpen>
        <P>Data is stored in your browser's <strong>localStorage</strong> — on your device only, not in the cloud. It can be lost if you:</P>
        <div style={{ margin: '8px 0', fontSize: '0.83rem', color: 'var(--text-med)', lineHeight: 1.9 }}>
          <div>• Clear browser history or cache</div>
          <div>• Use Private/Incognito mode</div>
          <div>• Your browser clears it due to low storage</div>
          <div>• Uninstall or reset the browser</div>
        </div>
        <Note type="danger">Export a backup after every invoicing session. It takes 5 seconds. Settings → Backup → Export All Data.</Note>
      </HelpSection>

      <HelpSection icon="📦" title="Exporting a backup">
        <P>Settings → ☁️ Backup tab → <strong>Export All Data</strong>. Downloads a JSON file with all invoices, clients, expenses, settings and counter.</P>
        <P>Save to iCloud Drive, Google Drive, OneDrive, or email it to yourself. Don't leave it only on the device.</P>
        <Tip>Name backups with the date: invoice-backup-2026-04-15.json</Tip>
      </HelpSection>

      <HelpSection icon="📥" title="Restoring from a backup">
        <P>Settings → ☁️ Backup → <strong>Import Backup</strong>. Select your JSON file. Choose:</P>
        <H>Replace All</H>
        <P>Wipes everything and restores from backup. Use for new device setup or after accidental data loss.</P>
        <H>Merge</H>
        <P>Keeps existing data, adds new entries from backup. Skips duplicates. Use to combine data from multiple devices.</P>
      </HelpSection>

      <HelpSection icon="📱" title="Moving to a new phone">
        <Step n="1" title="Old phone">Settings → Backup → Export All Data. Save to iCloud or Google Drive.</Step>
        <Step n="2" title="New phone">Open Invoice Generator in the browser. Install to home screen.</Step>
        <Step n="3" title="Import">Settings → Backup → Import Backup. Choose your file → Replace All.</Step>
        <Step n="4" title="Done">All invoices, clients, expenses and settings restored. Counter continues from where it left off.</Step>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// MOBILE FEATURES
// ═══════════════════════════════════════════════════════════════════

export function HelpMobile({ setPage }) {
  return (
    <HelpPage title="📱 Mobile Features" back={() => setPage('help-hub')}>

      <HelpSection icon="📲" title="Installing to your home screen (PWA)" defaultOpen>
        <H>iPhone (Safari)</H>
        <P>1. Open in Safari → 2. Tap the Share button → 3. Tap "Add to Home Screen" → 4. Tap Add. Opens fullscreen like a native app.</P>
        <H>Android (Chrome)</H>
        <P>1. Open in Chrome → 2. Tap the three-dot menu → 3. Tap "Add to Home screen" or "Install app" → 4. Tap Install.</P>
        <Note type="info">The installed app uses the same browser storage as the browser tab — they share the same data.</Note>
      </HelpSection>

      <HelpSection icon="📤" title="Share sheet — send PDFs via WhatsApp, iMessage etc.">
        <P>When you tap ⬇ Export PDF or 📤 Send Invoice, the app opens your phone's native share sheet. Send via WhatsApp, Mail, Gmail, iMessage, AirDrop, save to Files, or any other app that accepts PDFs.</P>
      </HelpSection>

      <HelpSection icon="🔍" title="Global search">
        <P>Tap the 🔍 button (bottom-right, above nav bar) to search all invoices and clients instantly. Results appear as you type. Tap any result to open it.</P>
        <P>On desktop: <strong>Ctrl+K</strong> (Windows) or <strong>Cmd+K</strong> (Mac) opens search from anywhere.</P>
      </HelpSection>

      <HelpSection icon="🔴" title="Dashboard notification banner">
        <P>Appears automatically when you have overdue invoices (red) or invoices due within 7 days (amber). Tap the buttons to go to Reminders or Invoices. Tap ✕ to dismiss for the day — reappears tomorrow if unresolved.</P>
      </HelpSection>

    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// FAQ
// ═══════════════════════════════════════════════════════════════════

export function HelpFAQ({ setPage }) {
  const faqs = [
    { q: 'My data has disappeared — what happened?', a: 'Almost always caused by clearing browser history/cache, using Private/Incognito mode, or the browser clearing localStorage due to low storage.\n\nIf you have a backup: Settings → Backup → Import Backup.\n\nIf not, the data cannot be recovered. This is why we strongly recommend exporting a backup after every session.' },
    { q: 'The invoice number keeps showing the same number', a: 'Create an invoice, fill in a client name, and tap Save Draft — the counter should advance after saving.\n\nIf still stuck: Settings → Backup → Clear All Data → tick "Invoice counter only". This resets the counter without affecting your invoices.' },
    { q: 'Camera won\'t open for receipt scanning', a: 'Camera needs a secure connection.\n\n• iPhone: Settings → Safari → Camera → Allow\n• Android: tap the lock icon in browser address bar → Camera → Allow\n• On localhost this should work automatically\n• Over http:// on a local network: use https:// or localhost instead' },
    { q: 'My invoice PDFs don\'t have a logo', a: 'Logo support is in the desktop app (Settings → Logo Image). The PWA generates PDFs without logos currently — planned for a future update.\n\nWorkaround: use the desktop app for logo invoices, mobile for quick on-site invoicing.' },
    { q: 'EmailJS is set up but emails aren\'t sending', a: 'Check in order:\n\n1. All three IDs correct? Service ID, Template ID, Public Key — must match your EmailJS dashboard exactly\n2. Service is Active? EmailJS dashboard → Email Services\n3. Hit free tier limit? 200/month max on free plan\n4. Template To field set to {{to_email}}? Not hardcoded?\n5. Check EmailJS dashboard → Email Logs for error details' },
    { q: 'How do I invoice in a different currency?', a: 'Settings → Invoicing → Currency Symbol. Change to $ (USD), € (EUR), or any symbol. Affects all new invoices. Existing invoices keep their original symbol.' },
    { q: 'Can I use this on multiple devices?', a: 'Data doesn\'t sync automatically. To use across devices:\n1. Export backup from device A\n2. Import on device B\n3. When done on device B, export and import back to device A\n\nManual but works well if you mainly use one device.' },
    { q: 'The app is slow or lagging', a: 'Usually fine. If slow:\n• Many invoices: the list takes a moment to filter — normal\n• Try pulling down to refresh (mobile) or pressing F5 (desktop)\n• PDF generation takes 2–3 seconds on older devices — expected\n• Large backup import: give it a few seconds' },
    { q: 'Something crashed — how do I report it?', a: 'More → Error Log shows all recorded crashes with exact file and line number. Tap 📋 copy to copy the full report. Send to letustec@gmail.com or Discord: discord.gg/dkebMS5eCX.\n\nInclude: what you were doing, which page, and paste the error report.' },
    { q: 'What\'s the difference between the desktop app and this?', a: 'Desktop app: company profiles, SMTP email, full keyboard shortcuts, no localStorage risk, more reports.\n\nMobile PWA: camera receipt scanning, native share sheet, Quick Invoice for on-site use, works on any device without installing, overdue notifications.' },
  ];
  return (
    <HelpPage title="❓ FAQ & Troubleshooting" back={() => setPage('help-hub')}>
      {faqs.map(({ q, a }) => (
        <HelpSection key={q} icon="❓" title={q}>
          <P style={{ whiteSpace: 'pre-line' }}>{a}</P>
        </HelpSection>
      ))}
    </HelpPage>
  );
}

// ═══════════════════════════════════════════════════════════════════
// ABOUT
// ═══════════════════════════════════════════════════════════════════

export function About({ setPage }) {
  return (
    <div className="page" style={{ paddingTop: 0 }}>
      <div className="top-bar">
        <button className="back-btn" onClick={() => setPage('more')}>‹ More</button>
        <div className="top-bar-title">About</div>
      </div>
      <div style={{ padding: '24px 20px 110px', textAlign: 'center' }}>
        <div style={{ fontSize: '3.5rem', marginBottom: 12 }}>🧾</div>
        <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.6rem', color: 'var(--accent)', letterSpacing: '-0.5px' }}>Invoice Generator</div>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginTop: 6 }}>Version 1.0 · PWA Edition</div>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginTop: 2 }}>Made by Deano @ LetUsTech · Liverpool</div>
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 14, padding: '18px 20px', marginTop: 24, textAlign: 'left' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-dim)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 10 }}>About</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-med)', lineHeight: 1.7 }}>Free, fully offline invoice management for UK freelancers and small businesses. No accounts. No subscriptions. No internet required (except receipt scanning and email sending). Your data stays on your device.</div>
        </div>
        {[{ icon: '🌐', label: 'Website', value: 'letustech.uk', href: 'https://letustech.uk' }, { icon: '📧', label: 'Email', value: 'letustec@gmail.com', href: 'mailto:letustec@gmail.com' }, { icon: '💬', label: 'Discord', value: 'discord.gg/dkebMS5eCX', href: 'https://discord.gg/dkebMS5eCX' }].map(({ icon, label, value, href }) => (
          <a key={label} href={href} target="_blank" rel="noreferrer" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 10, marginTop: 8, fontSize: '0.87rem', textDecoration: 'none' }}>
            <span style={{ color: 'var(--text-dim)' }}>{icon} {label}</span>
            <span style={{ color: 'var(--accent)', fontWeight: 500 }}>{value}</span>
          </a>
        ))}
        <div style={{ marginTop: 24, background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 14, padding: '18px 20px' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-med)', marginBottom: 14 }}>☕ If this saved you time or money, a small donation helps keep LetUsTech running.</div>
          <a href="https://www.paypal.com/donate/?hosted_button_id=MJNXEL8GRRPSL" target="_blank" rel="noreferrer" style={{ display: 'inline-block', background: '#ffc439', color: '#000', borderRadius: 10, padding: '11px 28px', fontWeight: 700, fontSize: '0.92rem', textDecoration: 'none' }}>💛 Donate via PayPal</a>
          <div style={{ marginTop: 10, fontSize: '0.75rem', color: 'var(--text-dim)' }}>Sort: 04-00-04 · Account: 49376025 · Ref: LetUsTech</div>
        </div>
      </div>
    </div>
  );
}

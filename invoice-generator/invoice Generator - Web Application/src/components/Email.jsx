import React, { useState } from 'react';
import emailjs from '@emailjs/browser';
import { fc } from '../utils/helpers';
import { Modal, Toast, Field } from '../components/UI';

// ── EmailJS config keys stored in settings ────────────────────────────────
// Users set these up once in Settings → Email tab
// We use Deano's LetUsTech EmailJS account as the default service
// but users can override with their own

export const DEFAULT_EMAIL_SETTINGS = {
  emailjs_service_id:  '',   // e.g. service_g7uurlg
  emailjs_template_id: '',   // e.g. template_invoice
  emailjs_public_key:  '',   // e.g. uq2xMcj3Wtw2WHsdE
  email_from_name:     '',   // shown as sender name
  email_reply_to:      '',   // your business email for replies
};

// ── Generate PDF as base64 string (for email attachment) ─────────────────
async function generatePDFBase64(inv, settings) {
  const { jsPDF } = await import('jspdf');
  await import('jspdf-autotable');

  const doc  = new jsPDF({ unit: 'mm', format: 'a4' });
  const sym  = settings.currency_symbol || '£';
  const fmtM = n => `${sym}${parseFloat(n || 0).toFixed(2)}`;

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

  // Company right
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.setTextColor(200, 200, 200);
  let ry = 14;
  [settings.company_name, settings.company_address?.split('\n')[0], settings.company_email, settings.vat_number ? `VAT: ${settings.vat_number}` : null]
    .filter(Boolean).forEach(l => { doc.text(l, 196, ry, { align: 'right' }); ry += 5; });

  // Bill to
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

  // Items table
  const rows = (inv.items || []).filter(i => i.desc || parseFloat(i.price)).map(i => [
    i.desc || '',
    parseFloat(i.qty || 1).toFixed(0),
    fmtM(i.price),
    i.taxable ? `${settings.tax_rate || 20}%` : '0%',
    fmtM((parseFloat(i.qty || 1)) * (parseFloat(i.price || 0))),
  ]);

  doc.autoTable({
    startY: 72, head: [['Description', 'Qty', 'Unit Price', 'Tax', 'Amount']],
    body: rows,
    styles: { fillColor: [19,23,32], textColor: [200,200,200], fontSize: 9, cellPadding: 4 },
    headStyles: { fillColor: [11,14,20], textColor: [0,230,118], fontStyle: 'bold', fontSize: 8 },
    alternateRowStyles: { fillType: 'fill', fillColor: [26,32,48] },
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

  if (inv.notes) {
    doc.setFont('helvetica', 'normal'); doc.setFontSize(8); doc.setTextColor(107, 114, 128);
    doc.text(inv.notes, 14, ty + 20, { maxWidth: 180 });
  }

  doc.setFont('helvetica', 'normal'); doc.setFontSize(7); doc.setTextColor(75, 85, 99);
  doc.text('Generated with Invoice Generator — letustech.uk', 105, 290, { align: 'center' });

  // Return as base64 string (without the data:application/pdf;base64, prefix)
  return doc.output('datauristring').split(',')[1];
}

// ── Send invoice email via EmailJS ────────────────────────────────────────
export async function sendInvoiceEmail({ inv, settings, toEmail, toName, subject, message }) {
  const { emailjs_service_id, emailjs_template_id, emailjs_public_key } = settings;

  if (!emailjs_service_id || !emailjs_template_id || !emailjs_public_key) {
    throw new Error('EmailJS not configured. Go to Settings → Email to set it up.');
  }

  const sym = settings.currency_symbol || '£';
  const pdfBase64 = await generatePDFBase64(inv, settings);
  const filename  = `${inv.number}_${(inv.client_name || 'invoice').replace(/\s+/g, '_')}.pdf`;

  const templateParams = {
    // Standard fields
    to_email:     toEmail,
    to_name:      toName || inv.client_name || '',
    from_name:    settings.email_from_name || settings.company_name || 'Invoice Generator',
    reply_to:     settings.email_reply_to || settings.company_email || '',
    subject:      subject,
    message:      message,
    // Invoice details (for use in template)
    invoice_number:  inv.number || '',
    invoice_date:    inv.date || '',
    invoice_due:     inv.due_date || '',
    invoice_total:   fc(inv.total, sym),
    client_name:     inv.client_name || '',
    company_name:    settings.company_name || '',
    company_email:   settings.company_email || '',
    // PDF attachment (EmailJS supports this via content/filename fields)
    pdf_content:  pdfBase64,
    pdf_filename: filename,
  };

  await emailjs.send(emailjs_service_id, emailjs_template_id, templateParams, emailjs_public_key);
  return { filename };
}

// ════════════════════════════════════════════════════════════════════════════
// EMAIL MODAL — compose and send
// ════════════════════════════════════════════════════════════════════════════
export function EmailModal({ inv, settings, onClose, onSent }) {
  const sym = settings.currency_symbol || '£';
  const isConfigured = settings.emailjs_service_id && settings.emailjs_template_id && settings.emailjs_public_key;

  const [to,      setTo]      = useState(inv.client_email || '');
  const [toName,  setToName]  = useState(inv.client_name  || '');
  const [subject, setSubject] = useState(`Invoice ${inv.number} from ${settings.company_name || 'us'}`);
  const [message, setMessage] = useState(
    `Hi ${inv.client_name || 'there'},\n\nPlease find attached invoice ${inv.number} for ${fc(inv.total, sym)}.\n\nPayment is due by ${inv.due_date || 'the date shown on the invoice'}.\n\n${settings.bank_account ? `Bank transfer details:\nBank: ${settings.bank_name}\nSort Code: ${settings.bank_sort_code}\nAccount: ${settings.bank_account}\nReference: ${inv.number}\n\n` : ''}Thank you for your business.\n\nKind regards,\n${settings.company_name || ''}${settings.company_email ? `\n${settings.company_email}` : ''}${settings.company_phone ? `\n${settings.company_phone}` : ''}`
  );
  const [sending, setSending] = useState(false);
  const [toast,   setToast]   = useState('');
  const [error,   setError]   = useState('');

  async function send() {
    if (!to.trim()) { setError('Enter a recipient email address.'); return; }
    if (!to.includes('@')) { setError('Enter a valid email address.'); return; }
    setSending(true);
    setError('');
    try {
      const result = await sendInvoiceEmail({ inv, settings, toEmail: to, toName, subject, message });
      setToast(`✅ Invoice sent to ${to}`);
      setTimeout(() => { onSent && onSent(); onClose(); }, 1500);
    } catch (e) {
      setError(e.message || 'Failed to send. Check your EmailJS settings.');
      setSending(false);
    }
  }

  if (!isConfigured) {
    return (
      <Modal title="📧 Send Invoice" onClose={onClose}>
        <div style={{ background: '#1a0808', border: '1px solid #ef444440', borderRadius: 10, padding: '14px', marginBottom: 16 }}>
          <div style={{ fontWeight: 700, color: '#ef4444', fontSize: '0.88rem', marginBottom: 6 }}>EmailJS not set up</div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-med)', lineHeight: 1.6 }}>
            To send invoices by email you need to connect EmailJS. It's free and takes about 5 minutes.
          </div>
        </div>
        <div style={{ fontSize: '0.83rem', color: 'var(--text-med)', lineHeight: 1.7, marginBottom: 16 }}>
          <strong style={{ color: 'var(--text)' }}>How to set it up:</strong><br />
          1. Go to <strong>emailjs.com</strong> and create a free account<br />
          2. Add an email service (Gmail, Outlook etc.)<br />
          3. Create an email template (see guide below)<br />
          4. Copy your Service ID, Template ID and Public Key<br />
          5. Paste them in <strong>Settings → Email</strong>
        </div>
        <div style={{ background: 'var(--bg-hover)', borderRadius: 10, padding: '12px 14px', marginBottom: 16 }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-dim)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8 }}>EmailJS Template Variables</div>
          <div style={{ fontFamily: 'Consolas, monospace', fontSize: '0.78rem', color: 'var(--accent)', lineHeight: 1.8 }}>
            {`{{to_name}} — client name\n{{subject}} — email subject\n{{message}} — email body\n{{invoice_number}} — e.g. INV-1001\n{{invoice_total}} — e.g. £144.00\n{{invoice_due}} — due date\n{{company_name}} — your business\n{{from_name}} — sender display name\n{{reply_to}} — your email`}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-ghost" style={{ flex: 1 }} onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => { onClose(); /* navigate to settings handled by parent */ onSent && onSent('settings'); }}>
            Go to Settings
          </button>
        </div>
      </Modal>
    );
  }

  return (
    <Modal title="📧 Send Invoice" onClose={onClose}>
      {/* Invoice summary */}
      <div style={{ background: 'var(--bg-hover)', borderRadius: 10, padding: '10px 14px', marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text)' }}>{inv.number}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: 2 }}>Due: {inv.due_date}</div>
        </div>
        <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.1rem', color: 'var(--accent)' }}>
          {fc(inv.total, sym)}
        </div>
      </div>

      {error && (
        <div style={{ background: '#1a0808', border: '1px solid #ef444440', borderRadius: 8, padding: '10px 14px', marginBottom: 12, fontSize: '0.82rem', color: '#ef4444' }}>
          ⚠️ {error}
        </div>
      )}

      <Field label="To (email address)">
        <input type="email" value={to} onChange={e => setTo(e.target.value)} placeholder="client@example.com" />
      </Field>
      <Field label="Recipient Name">
        <input value={toName} onChange={e => setToName(e.target.value)} placeholder="e.g. Tom Connor" />
      </Field>
      <Field label="Subject">
        <input value={subject} onChange={e => setSubject(e.target.value)} />
      </Field>
      <Field label="Message">
        <textarea rows={8} value={message} onChange={e => setMessage(e.target.value)} style={{ fontSize: '0.83rem' }} />
      </Field>

      <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: 16, padding: '8px 10px', background: 'var(--bg-hover)', borderRadius: 8 }}>
        📎 The PDF invoice will be attached automatically.
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <button className="btn btn-ghost" style={{ flex: 1 }} onClick={onClose} disabled={sending}>
          Cancel
        </button>
        <button className="btn btn-primary" style={{ flex: 2 }} onClick={send} disabled={sending}>
          {sending ? '⏳ Sending...' : '📧 Send Invoice'}
        </button>
      </div>

      {toast && <Toast message={toast} onDone={() => setToast('')} />}
    </Modal>
  );
}

// ════════════════════════════════════════════════════════════════════════════
// EMAIL SETTINGS TAB CONTENT (rendered inside Settings page)
// ════════════════════════════════════════════════════════════════════════════
export function EmailSettingsTab({ local, update }) {
  const isConfigured = local.emailjs_service_id && local.emailjs_template_id && local.emailjs_public_key;

  return (
    <>
      {isConfigured ? (
        <div style={{ background: '#0d1a0d', border: '1px solid var(--accent)', borderRadius: 10, padding: '10px 14px', marginBottom: 16, fontSize: '0.82rem', color: 'var(--accent)' }}>
          ✅ EmailJS connected — you can send invoices by email
        </div>
      ) : (
        <div style={{ background: '#1a0d00', border: '1px solid var(--gold)', borderRadius: 10, padding: '12px 14px', marginBottom: 16 }}>
          <div style={{ fontWeight: 700, color: 'var(--gold)', fontSize: '0.87rem', marginBottom: 6 }}>⚠️ Not connected yet</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-med)', lineHeight: 1.6 }}>
            Sign up free at <strong>emailjs.com</strong> → add a service → create a template → paste the IDs below.
          </div>
        </div>
      )}

      <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-dim)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8 }}>EmailJS Credentials</div>
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-body">
          <Field label="Service ID">
            <input value={local.emailjs_service_id || ''} onChange={e => update('emailjs_service_id', e.target.value)} placeholder="e.g. service_abc123" />
          </Field>
          <Field label="Template ID">
            <input value={local.emailjs_template_id || ''} onChange={e => update('emailjs_template_id', e.target.value)} placeholder="e.g. template_xyz789" />
          </Field>
          <Field label="Public Key">
            <input value={local.emailjs_public_key || ''} onChange={e => update('emailjs_public_key', e.target.value)} placeholder="e.g. uq2xMcj3Wtw2WHsdE" />
          </Field>
        </div>
      </div>

      <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-dim)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8 }}>Sender Details</div>
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-body">
          <Field label="From Name (shown to recipient)">
            <input value={local.email_from_name || ''} onChange={e => update('email_from_name', e.target.value)} placeholder="e.g. Dean Wilson" />
          </Field>
          <Field label="Reply-to Email">
            <input type="email" value={local.email_reply_to || ''} onChange={e => update('email_reply_to', e.target.value)} placeholder="your@email.com" />
          </Field>
        </div>
      </div>

      {/* Template guide */}
      <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-dim)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8 }}>EmailJS Template Setup</div>
      <div className="card" style={{ marginBottom: 12 }}>
        <div style={{ padding: '12px 14px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-med)', lineHeight: 1.7, marginBottom: 10 }}>
            In your EmailJS template, use these variables:
          </div>
          {[
            ['{{to_email}}',       'Recipient email (required in To field)'],
            ['{{to_name}}',        'Client name'],
            ['{{from_name}}',      'Your display name'],
            ['{{reply_to}}',       'Your reply-to address'],
            ['{{subject}}',        'Email subject line'],
            ['{{message}}',        'The email body text'],
            ['{{invoice_number}}', 'e.g. INV-1001'],
            ['{{invoice_total}}',  'e.g. £144.00'],
            ['{{invoice_due}}',    'Due date'],
            ['{{company_name}}',   'Your business name'],
          ].map(([v, d]) => (
            <div key={v} style={{ display: 'flex', gap: 10, padding: '4px 0', borderBottom: '1px solid var(--border)', fontSize: '0.78rem' }}>
              <code style={{ color: 'var(--accent)', fontFamily: 'Consolas, monospace', width: 160, flexShrink: 0 }}>{v}</code>
              <span style={{ color: 'var(--text-dim)' }}>{d}</span>
            </div>
          ))}
          <div style={{ marginTop: 10, fontSize: '0.75rem', color: 'var(--text-dim)', lineHeight: 1.6 }}>
            ⚠️ PDF attachment requires EmailJS Pro or a workaround — on free tier the email will send without the PDF attached, so use the Share button to attach the PDF via the native share sheet instead.
          </div>
        </div>
      </div>

      <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-dim)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8 }}>Quick Setup Links</div>
      <div className="card">
        {[
          { label: '1. Create EmailJS account', url: 'https://www.emailjs.com/', sub: 'Free — 200 emails/month' },
          { label: '2. Add email service', url: 'https://dashboard.emailjs.com/admin', sub: 'Connect Gmail or Outlook' },
          { label: '3. Create email template', url: 'https://dashboard.emailjs.com/admin/templates', sub: 'Use the variables above' },
        ].map(({ label, url, sub }) => (
          <a key={url} href={url} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', borderBottom: '1px solid var(--border)', textDecoration: 'none', cursor: 'pointer' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.87rem', fontWeight: 600, color: 'var(--text)' }}>{label}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: 2 }}>{sub}</div>
            </div>
            <span style={{ color: 'var(--accent)', fontSize: '0.85rem' }}>↗</span>
          </a>
        ))}
      </div>
    </>
  );
}

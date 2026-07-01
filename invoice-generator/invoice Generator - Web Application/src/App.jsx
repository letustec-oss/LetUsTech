import React, { useState, useEffect } from 'react';
import { loadSettings } from './utils/storage';
import Dashboard from './pages/Dashboard';
import NewInvoice from './pages/NewInvoice';
import { InvoicesList, ClientsList, ExpensesList, Reports, Settings, More } from './pages/Pages';
import { Reminders, Recurring, ClientDetail, GlobalSearch, LateFeeCalculator } from './pages/Features';
import { ReceiptScanner, QuickInvoice } from './components/Mobile';
import { ErrorBoundary, ErrorLog } from './components/ErrorBoundary';
import { HelpHub, HelpQuickStart, HelpVAT, HelpInvoices, HelpPayments, HelpExpenses, HelpEmail, HelpBackup, HelpFAQ, HelpRecurring, HelpReminders, HelpClients, HelpReports, HelpMobile, About } from './pages/Help';
import { BottomNav, Sidebar } from './components/UI';
import './styles/globals.css';

export default function App() {
  const [page,           setPage]           = useState('dashboard');
  const [settings,       setSettings]       = useState(loadSettings);
  const [editInvoice,    setEditInvoice]    = useState(null);
  const [selectedClient, setSelectedClient] = useState(null);
  const [searchOpen,     setSearchOpen]     = useState(false);

  useEffect(() => {
    document.documentElement.style.setProperty('--accent', settings.theme_accent || '#00e676');
  }, [settings.theme_accent]);

  useEffect(() => {
    const handler = e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(s => !s);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  function navigate(p) {
    if (p === 'new') setEditInvoice(null);
    setPage(p);
  }

  function renderPage() {
    switch (page) {
      case 'dashboard':
        return <Dashboard settings={settings} setPage={navigate} setEditInvoice={setEditInvoice} />;
      case 'new':
      case 'invoice-detail':
        return <NewInvoice settings={settings} setPage={navigate} prefill={editInvoice} onSaved={() => setEditInvoice(null)} />;
      case 'invoices':
        return <InvoicesList settings={settings} setPage={navigate} setEditInvoice={setEditInvoice} />;
      case 'clients':
      case 'add-client':
        return <ClientsList settings={settings} setPage={navigate} setSelectedClient={setSelectedClient} />;
      case 'client-detail':
        return selectedClient
          ? <ClientDetail client={selectedClient} settings={settings} setPage={navigate} setEditInvoice={setEditInvoice} />
          : (navigate('clients'), null);
      case 'expenses':
      case 'add-expense':
        return <ExpensesList settings={settings} setPage={navigate} />;
      case 'reports':
        return <Reports settings={settings} />;
      case 'reminders':
        return <Reminders settings={settings} setPage={navigate} setEditInvoice={setEditInvoice} />;
      case 'recurring':
        return <Recurring settings={settings} setPage={navigate} />;
      case 'late-fee':
        return <LateFeeCalculator settings={settings} />;
      case 'quick-invoice':
        return <QuickInvoice settings={settings} setPage={navigate} onSaved={() => setEditInvoice(null)} />;
      case 'scan-receipt':
        return <ReceiptScanner settings={settings} onClose={() => navigate('expenses')} onSaved={() => navigate('expenses')} />;
      case 'error-log':
        return <ErrorLog setPage={navigate} />;
      case 'help-hub':
        return <HelpHub setPage={navigate} />;
      case 'help-quickstart':
        return <HelpQuickStart setPage={navigate} />;
      case 'help-vat':
        return <HelpVAT setPage={navigate} />;
      case 'help-invoices':
        return <HelpInvoices setPage={navigate} />;
      case 'help-payments':
        return <HelpPayments setPage={navigate} />;
      case 'help-expenses':
        return <HelpExpenses setPage={navigate} />;
      case 'help-email':
        return <HelpEmail setPage={navigate} />;
      case 'help-backup':
        return <HelpBackup setPage={navigate} />;
      case 'help-faq':
        return <HelpFAQ setPage={navigate} />;
      case 'help-reminders':
        return <HelpReminders setPage={navigate} />;
      case 'help-clients':
        return <HelpClients setPage={navigate} />;
      case 'help-reports':
        return <HelpReports setPage={navigate} />;
      case 'help-recurring':
        return <HelpRecurring setPage={navigate} />;
      case 'help-mobile':
        return <HelpMobile setPage={navigate} />;
      case 'about':
        return <About setPage={navigate} />;
      case 'settings':
        return <Settings settings={settings} setSettings={s => setSettings(s)} />;
      case 'more':
      default:
        return <More settings={settings} setPage={navigate} />;
    }
  }

  const navPage = ['dashboard','invoices','new','clients','more'].includes(page) ? page
    : { expenses:'more', reports:'more', settings:'more', reminders:'more', recurring:'more',
        'late-fee':'more', 'quick-invoice':'more', 'scan-receipt':'more', 'error-log':'more',
        'help-hub':'more','help-quickstart':'more','help-vat':'more',
        'help-invoices':'more','help-payments':'more','help-expenses':'more',
        'help-email':'more','help-backup':'more','help-faq':'more','about':'more','help-reminders':'more','help-clients':'more','help-reports':'more','help-recurring':'more','help-mobile':'more',
        'add-client':'clients', 'add-expense':'more',
        'client-detail':'clients', 'invoice-detail':'invoices' }[page] || 'more';

  return (
    <ErrorBoundary>
      <Sidebar page={navPage} setPage={navigate} />
      {renderPage()}
      <button onClick={() => setSearchOpen(true)} style={{
        position:'fixed', bottom:`calc(var(--nav-h) + env(safe-area-inset-bottom,0px) + 12px)`,
        right:16, zIndex:90, background:'var(--bg-card)', border:'1px solid var(--border)',
        borderRadius:24, padding:'8px 14px', color:'var(--text-dim)', fontSize:'0.82rem',
        fontFamily:'DM Sans,sans-serif', display:'flex', alignItems:'center', gap:6,
        cursor:'pointer', boxShadow:'0 2px 12px rgba(0,0,0,0.3)',
      }}>🔍</button>
      <BottomNav page={navPage} setPage={navigate} />
      {searchOpen && <GlobalSearch settings={settings} setPage={navigate} setEditInvoice={setEditInvoice} onClose={() => setSearchOpen(false)} />}
    </ErrorBoundary>
  );
}

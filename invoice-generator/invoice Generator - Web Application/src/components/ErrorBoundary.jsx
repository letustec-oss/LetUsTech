import React from 'react';

// ── Global error log stored in localStorage ───────────────────────────────
const ERROR_LOG_KEY = 'ig_error_log';

function logError(error, info) {
  try {
    const entry = {
      timestamp:  new Date().toISOString(),
      message:    error?.message || String(error),
      stack:      error?.stack || '',
      component:  info?.componentStack || '',
      url:        window.location.href,
      userAgent:  navigator.userAgent,
      appVersion: '1.0.0',
    };
    const existing = JSON.parse(localStorage.getItem(ERROR_LOG_KEY) || '[]');
    existing.unshift(entry);
    localStorage.setItem(ERROR_LOG_KEY, JSON.stringify(existing.slice(0, 20))); // keep last 20
  } catch {}
}

export function loadErrorLog() {
  try { return JSON.parse(localStorage.getItem(ERROR_LOG_KEY) || '[]'); } catch { return []; }
}

export function clearErrorLog() {
  localStorage.removeItem(ERROR_LOG_KEY);
}

// ── Error Boundary class component ───────────────────────────────────────
export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null, info: null, copied: false };
  }

  componentDidCatch(error, info) {
    logError(error, info);
    this.setState({ error, info });
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  copyReport() {
    const { error, info } = this.state;
    const report = [
      '=== Invoice Generator Error Report ===',
      `Time: ${new Date().toISOString()}`,
      `URL: ${window.location.href}`,
      '',
      '--- Error Message ---',
      error?.message || 'Unknown error',
      '',
      '--- Stack Trace ---',
      error?.stack || 'No stack trace',
      '',
      '--- Component Stack ---',
      info?.componentStack || 'No component stack',
      '',
      '--- Environment ---',
      `Browser: ${navigator.userAgent}`,
    ].join('\n');

    navigator.clipboard?.writeText(report)
      .then(() => this.setState({ copied: true }))
      .catch(() => {});
  }

  render() {
    const { error, info, copied } = this.state;

    if (!error) return this.props.children;

    // Extract the most useful line from the stack
    const stackLines = (error?.stack || '').split('\n').filter(l => l.trim());
    const relevantLine = stackLines.find(l =>
      l.includes('/src/') || l.includes('.jsx') || l.includes('.js')
    ) || stackLines[1] || '';

    // Extract component name from component stack
    const compStack = (info?.componentStack || '').trim().split('\n').filter(l => l.trim());
    const failedIn  = compStack[0]?.trim().replace(/^\s*at\s+/, '') || 'Unknown component';

    return (
      <div style={{
        minHeight: '100vh', background: '#0b0e14', color: '#e8eaf0',
        fontFamily: 'DM Sans, sans-serif', padding: 20,
        display: 'flex', flexDirection: 'column',
      }}>
        {/* Header */}
        <div style={{ marginBottom: 24 }}>
          <div style={{ fontSize: '2rem', marginBottom: 8 }}>💥</div>
          <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.4rem', color: '#ef4444', margin: 0 }}>
            Something went wrong
          </h1>
          <p style={{ color: '#6b7280', fontSize: '0.85rem', marginTop: 6 }}>
            The app crashed. The error has been saved automatically.
          </p>
        </div>

        {/* Quick summary card */}
        <div style={{ background: '#1a0808', border: '1px solid #ef444440', borderRadius: 12, padding: 16, marginBottom: 16 }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#ef4444', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>
            Error
          </div>
          <div style={{ fontFamily: 'Consolas, monospace', fontSize: '0.88rem', color: '#fca5a5', wordBreak: 'break-word', lineHeight: 1.5 }}>
            {error?.message || 'Unknown error'}
          </div>
        </div>

        {/* Where it broke */}
        {relevantLine && (
          <div style={{ background: '#131720', border: '1px solid #1f2937', borderRadius: 12, padding: 16, marginBottom: 16 }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#9ca3af', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>
              📍 Where it broke
            </div>
            <div style={{ fontFamily: 'Consolas, monospace', fontSize: '0.82rem', color: '#00e676', wordBreak: 'break-word', lineHeight: 1.6 }}>
              {relevantLine.trim()}
            </div>
            {failedIn && (
              <div style={{ marginTop: 6, fontSize: '0.78rem', color: '#6b7280' }}>
                Failed in: <span style={{ color: '#9ca3af' }}>{failedIn}</span>
              </div>
            )}
          </div>
        )}

        {/* Full stack trace (collapsed by default) */}
        <details style={{ marginBottom: 16 }}>
          <summary style={{ cursor: 'pointer', color: '#6b7280', fontSize: '0.83rem', padding: '8px 0', userSelect: 'none' }}>
            Show full stack trace
          </summary>
          <div style={{ background: '#0d1117', border: '1px solid #1f2937', borderRadius: 8, padding: 14, marginTop: 8, overflow: 'auto', maxHeight: 200 }}>
            <pre style={{ fontFamily: 'Consolas, monospace', fontSize: '0.75rem', color: '#9ca3af', margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word', lineHeight: 1.5 }}>
              {error?.stack || 'No stack trace available'}
            </pre>
          </div>
        </details>

        {/* Component stack */}
        {compStack.length > 0 && (
          <details style={{ marginBottom: 20 }}>
            <summary style={{ cursor: 'pointer', color: '#6b7280', fontSize: '0.83rem', padding: '8px 0', userSelect: 'none' }}>
              Show component tree
            </summary>
            <div style={{ background: '#0d1117', border: '1px solid #1f2937', borderRadius: 8, padding: 14, marginTop: 8 }}>
              {compStack.map((line, i) => (
                <div key={i} style={{ fontFamily: 'Consolas, monospace', fontSize: '0.75rem', color: i === 0 ? '#ef4444' : '#6b7280', padding: '1px 0', paddingLeft: `${i * 12}px` }}>
                  {line.trim()}
                </div>
              ))}
            </div>
          </details>
        )}

        {/* Actions */}
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 20 }}>
          <button
            onClick={() => window.location.reload()}
            style={{ flex: 1, minWidth: 120, background: '#00e676', color: '#000', border: 'none', borderRadius: 8, padding: '11px 16px', fontFamily: 'DM Sans, sans-serif', fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer' }}>
            🔄 Reload App
          </button>
          <button
            onClick={() => this.copyReport()}
            style={{ flex: 1, minWidth: 120, background: '#1a2030', color: copied ? '#00e676' : '#9ca3af', border: '1px solid #1f2937', borderRadius: 8, padding: '11px 16px', fontFamily: 'DM Sans, sans-serif', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer' }}>
            {copied ? '✅ Copied!' : '📋 Copy Report'}
          </button>
        </div>

        {/* Dev instructions */}
        <div style={{ background: '#131720', border: '1px solid #1f2937', borderRadius: 12, padding: 16 }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#9ca3af', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 10 }}>
            🔧 For developers
          </div>
          <div style={{ fontSize: '0.82rem', color: '#6b7280', lineHeight: 1.7 }}>
            1. Click <strong style={{ color: '#9ca3af' }}>Copy Report</strong> and paste into your bug tracker<br/>
            2. The line in <strong style={{ color: '#9ca3af' }}>Where it broke</strong> is the exact file and line number<br/>
            3. All crashes are saved to <code style={{ color: '#00e676', fontSize: '0.8rem' }}>localStorage → ig_error_log</code><br/>
            4. View crash history at <strong style={{ color: '#9ca3af' }}>More → Error Log</strong> in the app
          </div>
        </div>
      </div>
    );
  }
}

// ── Error Log viewer page (in-app) ───────────────────────────────────────
export function ErrorLog({ setPage }) {
  const [log, setLog]       = React.useState(loadErrorLog);
  const [copied, setCopied] = React.useState(null);

  function copy(entry) {
    const text = [
      `Time: ${entry.timestamp}`,
      `Error: ${entry.message}`,
      `Stack: ${entry.stack}`,
      `Component: ${entry.component}`,
    ].join('\n');
    navigator.clipboard?.writeText(text).then(() => {
      setCopied(entry.timestamp);
      setTimeout(() => setCopied(null), 2000);
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Error Log</h1>
          <div className="page-subtitle">{log.length} crash{log.length !== 1 ? 'es' : ''} recorded</div>
        </div>
        {log.length > 0 && (
          <button className="btn btn-ghost btn-sm" style={{ color: 'var(--red)' }}
            onClick={() => { clearErrorLog(); setLog([]); }}>
            Clear
          </button>
        )}
      </div>

      {log.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">✅</div>
          <h3>No crashes recorded</h3>
          <p>The app hasn't crashed. Error reports will appear here when they occur.</p>
        </div>
      ) : log.map((entry, i) => {
        const stackLines = (entry.stack || '').split('\n').filter(l => l.includes('/src/') || l.includes('.jsx'));
        const keyLine    = stackLines[0]?.trim() || entry.stack?.split('\n')[1]?.trim() || '';
        return (
          <div key={i} className="card" style={{ marginBottom: 10 }}>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{new Date(entry.timestamp).toLocaleString()}</div>
                <div style={{ fontFamily: 'Consolas, monospace', fontSize: '0.85rem', color: 'var(--red)', marginTop: 4, wordBreak: 'break-word' }}>
                  {entry.message}
                </div>
              </div>
              <button className="btn btn-ghost btn-sm" style={{ marginLeft: 10, flexShrink: 0 }} onClick={() => copy(entry)}>
                {copied === entry.timestamp ? '✅' : '📋'}
              </button>
            </div>
            {keyLine && (
              <div style={{ padding: '8px 16px', fontFamily: 'Consolas, monospace', fontSize: '0.75rem', color: 'var(--accent)', wordBreak: 'break-word', background: 'var(--bg-hover)' }}>
                📍 {keyLine}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs   = require('fs');
const crypto = require('crypto');

// ── Data ─────────────────────────────────────────────────────────────────────
let DATA_FILE;

function getDataFile() {
  if (!DATA_FILE) DATA_FILE = path.join(app.getPath('userData'), 'data.json');
  return DATA_FILE;
}

function load() {
  try {
    const f = getDataFile();
    if (fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, 'utf8'));
  } catch {}
  return { clients: [], jobs: [] };
}

function save(data) {
  fs.writeFileSync(getDataFile(), JSON.stringify(data, null, 2));
}

function uid() { return crypto.randomUUID(); }

function now() { return new Date().toISOString(); }

// ── Window ────────────────────────────────────────────────────────────────────
function createWindow() {
  const win = new BrowserWindow({
    width: 1100, height: 720,
    minWidth: 800, minHeight: 560,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    autoHideMenuBar: true,
    title: 'LetUsTech Client Manager'
  });
  win.loadFile(path.join(__dirname, 'src', 'index.html'));
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());

// ── IPC: Clients ──────────────────────────────────────────────────────────────
ipcMain.handle('get-clients', () => {
  return load().clients.sort((a, b) => a.name.localeCompare(b.name));
});

ipcMain.handle('add-client', (_, client) => {
  const data = load();
  const newClient = { id: uid(), createdAt: now(), ...client };
  data.clients.push(newClient);
  save(data);
  return newClient;
});

ipcMain.handle('update-client', (_, id, changes) => {
  const data = load();
  const i = data.clients.findIndex(c => c.id === id);
  if (i === -1) return null;
  data.clients[i] = { ...data.clients[i], ...changes, updatedAt: now() };
  save(data);
  return data.clients[i];
});

ipcMain.handle('delete-client', (_, id) => {
  const data = load();
  data.clients = data.clients.filter(c => c.id !== id);
  data.jobs    = data.jobs.filter(j => j.clientId !== id);
  save(data);
  return true;
});

// ── IPC: Jobs ─────────────────────────────────────────────────────────────────
ipcMain.handle('get-jobs', (_, clientId) => {
  const data = load();
  const jobs = clientId
    ? data.jobs.filter(j => j.clientId === clientId)
    : data.jobs;
  return jobs.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
});

ipcMain.handle('add-job', (_, job) => {
  const data = load();
  const newJob = { id: uid(), createdAt: now(), status: 'open', ...job };
  data.jobs.push(newJob);
  save(data);
  return newJob;
});

ipcMain.handle('update-job', (_, id, changes) => {
  const data = load();
  const i = data.jobs.findIndex(j => j.id === id);
  if (i === -1) return null;
  if (changes.status === 'complete' && !data.jobs[i].completedAt) {
    changes.completedAt = now();
  }
  data.jobs[i] = { ...data.jobs[i], ...changes, updatedAt: now() };
  save(data);
  return data.jobs[i];
});

ipcMain.handle('delete-job', (_, id) => {
  const data = load();
  data.jobs = data.jobs.filter(j => j.id !== id);
  save(data);
  return true;
});

// ── IPC: Stats ────────────────────────────────────────────────────────────────
ipcMain.handle('get-stats', () => {
  const data = load();
  const thisMonth = new Date();
  thisMonth.setDate(1); thisMonth.setHours(0, 0, 0, 0);
  return {
    totalClients:    data.clients.length,
    openJobs:        data.jobs.filter(j => j.status === 'open').length,
    inProgressJobs:  data.jobs.filter(j => j.status === 'in-progress').length,
    completedMonth:  data.jobs.filter(j => j.status === 'complete' && new Date(j.completedAt) >= thisMonth).length
  };
});

// ── IPC: Export ───────────────────────────────────────────────────────────────
ipcMain.handle('export-client', async (_, clientId) => {
  const data = load();
  const client = data.clients.find(c => c.id === clientId);
  if (!client) return { ok: false };
  const jobs = data.jobs.filter(j => j.clientId === clientId);
  const lines = [
    `CLIENT RECORD — ${client.name}`,
    `${'─'.repeat(50)}`,
    `Company:  ${client.company || '—'}`,
    `Email:    ${client.email || '—'}`,
    `Phone:    ${client.phone || '—'}`,
    `Address:  ${client.address || '—'}`,
    `Devices:  ${client.devices || '—'}`,
    `Notes:    ${client.notes || '—'}`,
    `Added:    ${new Date(client.createdAt).toLocaleDateString('en-GB')}`,
    '',
    `JOBS (${jobs.length})`,
    `${'─'.repeat(50)}`,
    ...jobs.map(j =>
      `[${j.status.toUpperCase()}] ${j.title}\n` +
      `  Category: ${j.category || '—'}  Priority: ${j.priority || 'normal'}\n` +
      `  Added: ${new Date(j.createdAt).toLocaleDateString('en-GB')}` +
      (j.completedAt ? `  Completed: ${new Date(j.completedAt).toLocaleDateString('en-GB')}` : '') + '\n' +
      (j.description ? `  Description: ${j.description}\n` : '') +
      (j.workNotes ? `  Work notes: ${j.workNotes}\n` : '')
    )
  ];
  const { filePath } = await dialog.showSaveDialog({
    title: 'Export Client Record',
    defaultPath: `${client.name.replace(/\s+/g, '_')}_record.txt`,
    filters: [{ name: 'Text', extensions: ['txt'] }]
  });
  if (!filePath) return { ok: false };
  fs.writeFileSync(filePath, lines.join('\n'));
  return { ok: true };
});

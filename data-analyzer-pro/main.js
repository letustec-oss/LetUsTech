const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const https = require('https');
const os = require('os');

const CONFIG_PATH = path.join(app.getPath('userData'), 'config.json');

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch {}
  return { apiKey: '', theme: 'dark' };
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#0d1117',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    icon: path.join(__dirname, 'src', 'assets', 'icon.png')
  });

  win.loadFile(path.join(__dirname, 'src', 'index.html'));

  const menu = Menu.buildFromTemplate([
    {
      label: 'File',
      submenu: [
        { label: 'Open CSV...', accelerator: 'CmdOrCtrl+O', click: () => win.webContents.send('menu-open-file') },
        { label: 'Export Report...', accelerator: 'CmdOrCtrl+E', click: () => win.webContents.send('menu-export') },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' }, { role: 'redo' }, { type: 'separator' },
        { role: 'cut' }, { role: 'copy' }, { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' }, { role: 'toggleDevTools' },
        { type: 'separator' }, { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Settings',
      click: () => win.webContents.send('open-settings')
    },
    {
      label: 'Help',
      submenu: [
        { label: 'LetUsTech Website', click: () => shell.openExternal('https://letustech.uk') },
        { label: 'About Data Analyzer Pro', click: () => {
          dialog.showMessageBox(win, {
            type: 'info', title: 'Data Analyzer Pro',
            message: 'Data Analyzer Pro v1.0.0',
            detail: 'Advanced CSV analysis with AI insights.\nBuilt by LetUsTech\nletustech.uk'
          });
        }}
      ]
    }
  ]);
  Menu.setApplicationMenu(menu);
}

ipcMain.handle('open-csv-dialog', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    title: 'Open CSV File',
    filters: [{ name: 'CSV Files', extensions: ['csv'] }, { name: 'All Files', extensions: ['*'] }],
    properties: ['openFile']
  });
  if (canceled || !filePaths.length) return null;
  const content = fs.readFileSync(filePaths[0], 'utf8');
  return { path: filePaths[0], name: path.basename(filePaths[0]), content };
});

ipcMain.handle('save-report', async (_, { content, defaultName }) => {
  const { canceled, filePath } = await dialog.showSaveDialog({
    title: 'Save Report',
    defaultPath: defaultName || 'report.html',
    filters: [{ name: 'HTML Report', extensions: ['html'] }, { name: 'CSV Export', extensions: ['csv'] }]
  });
  if (canceled || !filePath) return false;
  fs.writeFileSync(filePath, content, 'utf8');
  shell.openPath(filePath);
  return true;
});

ipcMain.handle('get-config', () => loadConfig());
ipcMain.handle('save-config', (_, config) => { saveConfig(config); return true; });

ipcMain.handle('claude-api', async (_, { apiKey, messages }) => {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1000,
      messages
    });
    const req = https.request({
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'Content-Length': Buffer.byteLength(body)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { reject(new Error('Failed to parse response')); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
});

app.whenReady().then(createWindow);
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });

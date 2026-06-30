const { app, BrowserWindow, ipcMain, shell, Notification } = require('electron');
const path = require('path');
const fs   = require('fs');

const CONFIG_FILE = () => path.join(app.getPath('userData'), 'firebase-config.json');

let mainWindow;
let lastDeviceStates = {};

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200, height: 740,
    minWidth: 900, minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    autoHideMenuBar: true,
    title: 'LetUsTech RMM'
  });
  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());

// ── Firebase config ──────────────────────────────────────────────────────────
ipcMain.handle('get-firebase-config', () => {
  try {
    const f = CONFIG_FILE();
    if (fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, 'utf8'));
  } catch {}
  return null;
});

ipcMain.handle('save-firebase-config', (_, config) => {
  fs.writeFileSync(CONFIG_FILE(), JSON.stringify(config, null, 2));
  return true;
});

// ── Notifications ────────────────────────────────────────────────────────────
ipcMain.handle('notify', (_, title, body) => {
  if (Notification.isSupported()) {
    new Notification({ title, body }).show();
  }
});

ipcMain.handle('device-state-change', (_, deviceId, newStatus, deviceName) => {
  const prev = lastDeviceStates[deviceId];
  lastDeviceStates[deviceId] = newStatus;
  if (prev === 'online' && newStatus === 'offline') {
    if (Notification.isSupported()) {
      new Notification({
        title: 'Device Offline',
        body: `${deviceName} has gone offline`
      }).show();
    }
  }
  if (prev === 'offline' && newStatus === 'online') {
    if (Notification.isSupported()) {
      new Notification({
        title: 'Device Online',
        body: `${deviceName} is back online`
      }).show();
    }
  }
});

// ── External links ───────────────────────────────────────────────────────────
ipcMain.handle('open-external', (_, url) => shell.openExternal(url));

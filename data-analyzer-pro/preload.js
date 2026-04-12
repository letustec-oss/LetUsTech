const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openCSVDialog: () => ipcRenderer.invoke('open-csv-dialog'),
  saveReport: (opts) => ipcRenderer.invoke('save-report', opts),
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  claudeAPI: (opts) => ipcRenderer.invoke('claude-api', opts),
  onMenuOpenFile: (cb) => ipcRenderer.on('menu-open-file', cb),
  onMenuExport: (cb) => ipcRenderer.on('menu-export', cb),
  onOpenSettings: (cb) => ipcRenderer.on('open-settings', cb)
});

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getFirebaseConfig:   ()                    => ipcRenderer.invoke('get-firebase-config'),
  saveFirebaseConfig:  (config)              => ipcRenderer.invoke('save-firebase-config', config),
  notify:              (title, body)         => ipcRenderer.invoke('notify', title, body),
  deviceStateChange:   (id, status, name)    => ipcRenderer.invoke('device-state-change', id, status, name),
  openExternal:        (url)                 => ipcRenderer.invoke('open-external', url)
});

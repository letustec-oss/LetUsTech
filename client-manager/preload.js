const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getClients:   ()           => ipcRenderer.invoke('get-clients'),
  addClient:    (client)     => ipcRenderer.invoke('add-client', client),
  updateClient: (id, data)   => ipcRenderer.invoke('update-client', id, data),
  deleteClient: (id)         => ipcRenderer.invoke('delete-client', id),

  getJobs:      (clientId)   => ipcRenderer.invoke('get-jobs', clientId),
  addJob:       (job)        => ipcRenderer.invoke('add-job', job),
  updateJob:    (id, data)   => ipcRenderer.invoke('update-job', id, data),
  deleteJob:    (id)         => ipcRenderer.invoke('delete-job', id),

  getStats:     ()           => ipcRenderer.invoke('get-stats'),
  exportClient: (clientId)   => ipcRenderer.invoke('export-client', clientId)
});

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Remote Support
  launchQuickAssist:  ()      => ipcRenderer.invoke('launch-quick-assist'),
  openContact:        ()      => ipcRenderer.invoke('open-contact'),

  // Diagnostics
  getSystemInfo:      ()      => ipcRenderer.invoke('get-system-info'),
  getDefenderStatus:  ()      => ipcRenderer.invoke('get-defender-status'),
  runQuickScan:       ()      => ipcRenderer.invoke('run-quick-scan'),
  runDefenderFull:    ()      => ipcRenderer.invoke('run-defender-full'),
  openWindowsSecurity:()      => ipcRenderer.invoke('open-windows-security'),

  // Network
  getNetworkInfo:     ()      => ipcRenderer.invoke('get-network-info'),
  flushDns:           ()      => ipcRenderer.invoke('flush-dns'),
  renewIp:            ()      => ipcRenderer.invoke('renew-ip'),
  runPingTest:        (host)  => ipcRenderer.invoke('run-ping-test', host),

  // Tech mode
  resetWinsock:       ()      => ipcRenderer.invoke('reset-winsock'),
  resetTcpIp:         ()      => ipcRenderer.invoke('reset-tcpip'),
  getEventErrors:     ()      => ipcRenderer.invoke('get-event-errors'),
  getStartupApps:     ()      => ipcRenderer.invoke('get-startup-apps'),
  checkHostsFile:     ()      => ipcRenderer.invoke('check-hosts-file'),
  openDeviceManager:  ()      => ipcRenderer.invoke('open-device-manager'),
  openEventViewer:    ()      => ipcRenderer.invoke('open-event-viewer'),

  // Events from main
  onScanOutput: (cb) => ipcRenderer.on('scan-output', (_, d) => cb(d))
});

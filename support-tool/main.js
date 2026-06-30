const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const { exec, execSync, spawn } = require('child_process');
const path = require('path');
const os   = require('os');
const fs   = require('fs');

// ── Admin ────────────────────────────────────────────────────────────────────
function isElevated() {
  try { execSync('net session', { stdio: 'pipe' }); return true; }
  catch { return false; }
}

function relaunchAsAdmin() {
  const script = `Start-Process -FilePath "${process.execPath.replace(/\\/g,'\\\\')}" -Verb RunAs`;
  const tmp = path.join(os.tmpdir(), 'lut_relaunch.ps1');
  fs.writeFileSync(tmp, '﻿' + script);
  exec(`powershell.exe -ExecutionPolicy Bypass -File "${tmp}"`);
  setTimeout(() => app.quit(), 1500);
}

// ── PowerShell helper ────────────────────────────────────────────────────────
function runPS(script, timeout = 30000) {
  return new Promise((resolve, reject) => {
    const tmp = path.join(os.tmpdir(), `lut_${Date.now()}.ps1`);
    fs.writeFileSync(tmp, '﻿' + script);
    exec(`powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${tmp}"`,
      { timeout },
      (err, stdout) => {
        try { fs.unlinkSync(tmp); } catch {}
        if (err && !stdout) return reject(err.message);
        resolve(stdout.trim());
      });
  });
}

// ── Window ───────────────────────────────────────────────────────────────────
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 980, height: 680,
    minWidth: 800, minHeight: 560,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    autoHideMenuBar: true,
    title: 'LetUsTech Support'
  });
  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));
}

app.whenReady().then(async () => {
  if (!isElevated()) {
    const { response } = await dialog.showMessageBox({
      type: 'info',
      title: 'LetUsTech Support',
      message: 'Administrator access is needed for some features.',
      detail: 'Would you like to relaunch with administrator permissions?',
      buttons: ['Relaunch as Admin', 'Continue Anyway'],
      defaultId: 0
    });
    if (response === 0) { relaunchAsAdmin(); return; }
  }
  createWindow();
});

app.on('window-all-closed', () => app.quit());

// ── IPC: Remote Support ──────────────────────────────────────────────────────
ipcMain.handle('launch-quick-assist', async () => {
  try {
    exec('start ms-quick-assist:');
    return { ok: true };
  } catch {
    try { exec('powershell.exe -Command "Start-Process msra.exe"'); return { ok: true }; }
    catch (e) { return { ok: false, error: e.message }; }
  }
});

ipcMain.handle('open-contact', () => {
  shell.openExternal('mailto:letustec@gmail.com?subject=Remote Support Request');
});

// ── IPC: System Info ─────────────────────────────────────────────────────────
ipcMain.handle('get-system-info', async () => {
  const script = `
$os   = Get-CimInstance Win32_OperatingSystem
$cpu  = Get-CimInstance Win32_Processor | Select-Object -First 1
$cs   = Get-CimInstance Win32_ComputerSystem
$disk = Get-PSDrive C
$boot = $os.LastBootUpTime
$upH  = [math]::Floor(((Get-Date) - $boot).TotalHours)
$ramTotalGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
$ramFreeGB  = [math]::Round($os.FreePhysicalMemory / 1MB / 1024, 1)
$ramUsedPct = [math]::Round((1 - ($os.FreePhysicalMemory * 1024) / $cs.TotalPhysicalMemory) * 100)
$diskUsedGB = [math]::Round($disk.Used / 1GB, 1)
$diskFreeGB = [math]::Round($disk.Free / 1GB, 1)
$diskPct    = [math]::Round($disk.Used / ($disk.Used + $disk.Free) * 100)
$act = (Get-CimInstance SoftwareLicensingProduct -Filter "PartialProductKey IS NOT NULL AND Name LIKE 'Windows*'" -ErrorAction SilentlyContinue | Select-Object -First 1).LicenseStatus
$upToDate = (Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1).InstalledOn

ConvertTo-Json -Compress @{
  os        = $os.Caption
  build     = $os.BuildNumber
  cpu       = $cpu.Name.Trim()
  ramTotal  = $ramTotalGB
  ramFree   = $ramFreeGB
  ramUsed   = $ramUsedPct
  diskUsed  = $diskUsedGB
  diskFree  = $diskFreeGB
  diskPct   = $diskPct
  uptime    = $upH
  activated = ($act -eq 1)
  lastPatch = if($upToDate){"$upToDate"}else{"Unknown"}
  computer  = $env:COMPUTERNAME
  user      = $env:USERNAME
}`;
  try {
    const raw = await runPS(script, 20000);
    return JSON.parse(raw);
  } catch (e) {
    return { error: e.message };
  }
});

// ── IPC: Defender ────────────────────────────────────────────────────────────
ipcMain.handle('get-defender-status', async () => {
  const script = `
try {
  $s = Get-MpComputerStatus
  ConvertTo-Json -Compress @{
    enabled     = $s.AntivirusEnabled
    realTime    = $s.RealTimeProtectionEnabled
    sigAge      = $s.AntivirusSignatureAge
    lastScan    = $s.QuickScanAge
    lastScanDate= "$($s.QuickScanEndTime)"
    threats     = $s.QuarantineCount
  }
} catch { '{"error":"Defender unavailable"}' }`;
  try { return JSON.parse(await runPS(script, 15000)); }
  catch (e) { return { error: e.message }; }
});

ipcMain.handle('run-quick-scan', async (event) => {
  const script = `
Update-MpSignature -ErrorAction SilentlyContinue
Start-MpScan -ScanType QuickScan
$s = Get-MpComputerStatus
Write-Output "DONE:$($s.QuarantineCount)"`;
  const tmp = path.join(os.tmpdir(), `lut_scan_${Date.now()}.ps1`);
  fs.writeFileSync(tmp, '﻿' + script);
  return new Promise((resolve) => {
    const proc = spawn('powershell.exe', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', tmp]);
    proc.stdout.on('data', d => {
      const t = d.toString().trim();
      if (mainWindow) mainWindow.webContents.send('scan-output', t);
    });
    proc.on('close', () => {
      try { fs.unlinkSync(tmp); } catch {}
      resolve({ ok: true });
    });
  });
});

// ── IPC: Network ─────────────────────────────────────────────────────────────
ipcMain.handle('get-network-info', async () => {
  const script = `
$adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }
$primary  = $adapters | Select-Object -First 1
$ipInfo   = Get-NetIPAddress -InterfaceIndex $primary.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -First 1
$profile  = Get-NetConnectionProfile -InterfaceIndex $primary.InterfaceIndex -ErrorAction SilentlyContinue | Select-Object -First 1
$dns      = (Get-DnsClientServerAddress -InterfaceIndex $primary.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue).ServerAddresses -join ", "
$gwInfo   = (Get-NetRoute -InterfaceIndex $primary.InterfaceIndex -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Select-Object -First 1).NextHop

$wifiSig = ""
try {
  $wifiLine = (netsh wlan show interfaces 2>$null) | Select-String "Signal"
  if($wifiLine){ $wifiSig = $wifiLine.ToString().Split(":")[1].Trim() }
} catch {}

$ping = Test-Connection -ComputerName 8.8.8.8 -Count 2 -ErrorAction SilentlyContinue
$latency = if($ping){ [math]::Round(($ping.ResponseTime | Measure-Object -Average).Average) }else{$null}

ConvertTo-Json -Compress @{
  adapter   = $primary.Name
  desc      = $primary.InterfaceDescription
  ip        = if($ipInfo){ $ipInfo.IPAddress }else{"N/A"}
  gateway   = if($gwInfo){ $gwInfo }else{"N/A"}
  dns       = if($dns){ $dns }else{"N/A"}
  network   = if($profile){ $profile.Name }else{"N/A"}
  wifiSig   = $wifiSig
  online    = ($null -ne $ping)
  latency   = $latency
  type      = $primary.MediaType
}`;
  try { return JSON.parse(await runPS(script, 20000)); }
  catch (e) { return { error: e.message }; }
});

ipcMain.handle('flush-dns', async () => {
  try {
    await runPS('ipconfig /flushdns; Write-Output "DNS cache cleared."');
    return { ok: true };
  } catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle('renew-ip', async () => {
  try {
    await runPS('ipconfig /release; Start-Sleep -Seconds 2; ipconfig /renew; Write-Output "IP renewed."', 30000);
    return { ok: true };
  } catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle('run-ping-test', async (_, host) => {
  const target = host || '8.8.8.8';
  const script = `
$results = Test-Connection -ComputerName "${target}" -Count 4 -ErrorAction SilentlyContinue
if ($results) {
  $avg = [math]::Round(($results.ResponseTime | Measure-Object -Average).Average)
  $min = ($results.ResponseTime | Measure-Object -Minimum).Minimum
  $max = ($results.ResponseTime | Measure-Object -Maximum).Maximum
  ConvertTo-Json -Compress @{ ok=$true; avg=$avg; min=$min; max=$max; host="${target}"; count=$results.Count }
} else {
  ConvertTo-Json -Compress @{ ok=$false; host="${target}" }
}`;
  try { return JSON.parse(await runPS(script, 15000)); }
  catch (e) { return { ok: false, error: e.message }; }
});

// ── IPC: Tech Mode ───────────────────────────────────────────────────────────
ipcMain.handle('reset-winsock', async () => {
  try { await runPS('netsh winsock reset; Write-Output "Done."', 15000); return { ok: true }; }
  catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle('reset-tcpip', async () => {
  try { await runPS('netsh int ip reset; Write-Output "Done."', 15000); return { ok: true }; }
  catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle('get-event-errors', async () => {
  const script = `
$events = Get-WinEvent -FilterHashtable @{LogName='System','Application'; Level=2; StartTime=(Get-Date).AddHours(-24)} -MaxEvents 20 -ErrorAction SilentlyContinue
if ($events) {
  $events | Select-Object TimeCreated,ProviderName,Message | ForEach-Object {
    "$($_.TimeCreated.ToString('HH:mm')) | $($_.ProviderName) | $($_.Message -replace '\r?\n',' ' | Select-Object -First 1)"
  } | ConvertTo-Json -Compress
} else { '[]' }`;
  try {
    const raw = await runPS(script, 20000);
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [parsed];
  } catch { return []; }
});

ipcMain.handle('get-startup-apps', async () => {
  const script = `
$items = @()
$paths = @(
  "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
  "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
)
foreach ($p in $paths) {
  $reg = Get-ItemProperty $p -ErrorAction SilentlyContinue
  if ($reg) {
    $reg.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
      $items += @{ name=$_.Name; path=$_.Value; hive=($p -split "\\\\")[0] }
    }
  }
}
$items | ConvertTo-Json -Compress`;
  try {
    const raw = await runPS(script, 15000);
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : (parsed ? [parsed] : []);
  } catch { return []; }
});

ipcMain.handle('check-hosts-file', async () => {
  const script = `
$hosts = Get-Content "$env:SystemRoot\\System32\\drivers\\etc\\hosts" -ErrorAction SilentlyContinue
$custom = $hosts | Where-Object { $_ -notmatch '^#' -and $_ -match '\S' }
ConvertTo-Json -Compress @{
  entries = @($custom)
  count   = $custom.Count
  suspicious = @($custom | Where-Object { $_ -notmatch '127\.0\.0\.1|::1|localhost|0\.0\.0\.0\s+0\.0\.0\.0' })
}`;
  try { return JSON.parse(await runPS(script, 10000)); }
  catch { return { entries: [], count: 0, suspicious: [] }; }
});

ipcMain.handle('run-defender-full', async () => {
  try { exec('powershell.exe -Command "Start-MpScan -ScanType FullScan"'); return { ok: true }; }
  catch (e) { return { ok: false, error: e.message }; }
});

ipcMain.handle('open-windows-security', () => {
  exec('start windowsdefender:');
});

ipcMain.handle('open-device-manager', () => {
  exec('devmgmt.msc');
});

ipcMain.handle('open-event-viewer', () => {
  exec('eventvwr.msc');
});

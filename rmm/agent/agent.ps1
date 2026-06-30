# LetUsTech RMM Agent
# Collects system health data and pushes to Firebase Realtime Database
# Runs every 5 minutes via Windows Task Scheduler

$ConfigPath = "$PSScriptRoot\config.json"

if (-not (Test-Path $ConfigPath)) {
    Write-Host "ERROR: config.json not found at $ConfigPath"
    exit 1
}

$Config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
$FirebaseUrl  = $Config.firebaseUrl.TrimEnd('/')
$Secret       = $Config.firebaseSecret
$ClientName   = $Config.clientName
$DeviceId     = $Config.deviceId

# ── Collect system metrics ────────────────────────────────────────────────────
$DeviceName = $env:COMPUTERNAME
$UserName   = $env:USERNAME
$OS         = (Get-CimInstance Win32_OperatingSystem).Caption

# CPU (average over 2 samples, 500ms apart)
$Cpu1 = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
Start-Sleep -Milliseconds 500
$Cpu2 = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
$CpuPct = [math]::Round(($Cpu1 + $Cpu2) / 2)

# RAM
$OS_Info  = Get-CimInstance Win32_OperatingSystem
$TotalRAM = $OS_Info.TotalVisibleMemorySize
$FreeRAM  = $OS_Info.FreePhysicalMemory
$RamPct   = [math]::Round((($TotalRAM - $FreeRAM) / $TotalRAM) * 100)

# Disk (C: drive)
$Disk     = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$DiskTotal = $Disk.Size
$DiskFree  = $Disk.FreeSpace
$DiskUsed  = [math]::Round((($DiskTotal - $DiskFree) / $DiskTotal) * 100)
$DiskFreeGB = [math]::Round($DiskFree / 1GB, 1)

# Uptime (hours)
$BootTime = $OS_Info.LastBootUpTime
$Uptime   = [math]::Round((New-TimeSpan -Start $BootTime -End (Get-Date)).TotalHours, 1)

# ── Windows Defender ──────────────────────────────────────────────────────────
$DefEnabled  = $false
$DefRealTime = $false
$DefSigAge   = 999
$DefLastScan = 999

try {
    $Defender = Get-MpComputerStatus -ErrorAction Stop
    $DefEnabled  = $Defender.AntivirusEnabled
    $DefRealTime = $Defender.RealTimeProtectionEnabled
    $SigDate     = $Defender.AntivirusSignatureLastUpdated
    $DefSigAge   = [math]::Round((New-TimeSpan -Start $SigDate -End (Get-Date)).TotalDays)
    $ScanDate    = $Defender.QuickScanEndTime
    if ($ScanDate -and $ScanDate -ne [DateTime]::MinValue) {
        $DefLastScan = [math]::Round((New-TimeSpan -Start $ScanDate -End (Get-Date)).TotalDays)
    }
} catch {}

# ── Windows Updates ───────────────────────────────────────────────────────────
$PendingUpdates = 0
try {
    $UpdateSession  = New-Object -ComObject Microsoft.Update.Session
    $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
    $Result = $UpdateSearcher.Search("IsInstalled=0 and Type='Software'")
    $PendingUpdates = $Result.Updates.Count
} catch {}

# ── Build payload ─────────────────────────────────────────────────────────────
$Payload = @{
    clientName = $ClientName
    deviceName = $DeviceName
    userName   = $UserName
    lastSeen   = (Get-Date -Format "o")
    system     = @{
        os        = $OS
        cpu       = $CpuPct
        ramUsed   = $RamPct
        diskUsed  = $DiskUsed
        diskFreeGB = $DiskFreeGB
        uptime    = $Uptime
    }
    defender = @{
        enabled  = $DefEnabled
        realTime = $DefRealTime
        sigAge   = $DefSigAge
        lastScan = $DefLastScan
    }
    updates = @{
        pendingCount = $PendingUpdates
        lastCheck    = (Get-Date -Format "o")
    }
} | ConvertTo-Json -Depth 5

# ── Push to Firebase ──────────────────────────────────────────────────────────
$Uri = "$FirebaseUrl/devices/$DeviceId.json?auth=$Secret"
try {
    Invoke-RestMethod -Uri $Uri -Method Put -Body $Payload -ContentType "application/json" | Out-Null
} catch {
    Write-Host "Firebase push failed: $_"
    exit 1
}

# ── Check for commands ────────────────────────────────────────────────────────
$CmdUri = "$FirebaseUrl/commands/$DeviceId.json?auth=$Secret"
try {
    $CmdData = Invoke-RestMethod -Uri $CmdUri -Method Get
    if ($CmdData -and $CmdData.cmd) {
        $Cmd = $CmdData.cmd

        # Clear the command so it only runs once
        Invoke-RestMethod -Uri $CmdUri -Method Delete | Out-Null

        switch ($Cmd) {
            "run-updates" {
                Start-Process -FilePath "powershell.exe" -ArgumentList "-Command", "Install-Module PSWindowsUpdate -Force -Confirm:`$false; Import-Module PSWindowsUpdate; Install-WindowsUpdate -AcceptAll -IgnoreReboot" -WindowStyle Hidden
            }
            "run-defender" {
                Start-Process -FilePath "powershell.exe" -ArgumentList "-Command", "Start-MpScan -ScanType QuickScan" -WindowStyle Hidden
            }
            "flush-dns" {
                ipconfig /flushdns | Out-Null
            }
            "restart" {
                Start-Sleep -Seconds 10
                Restart-Computer -Force
            }
        }
    }
} catch {}

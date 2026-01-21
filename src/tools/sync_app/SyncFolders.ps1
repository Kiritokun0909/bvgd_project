# --- CONFIGURATION ---
$ServerList  = Get-Content "C:\Users\pnqt\PycharmProjects\bvgd_project\src\tools\sync_app\IpKhoaKham.csv"
$LocalFolder = "C:\Users\pnqt\PycharmProjects\bvgd_project\dist"
$RemoteShare = "ehosbk\EhosBackup"
$LogFolder   = "C:\Users\pnqt\PycharmProjects\bvgd_project\src\tools\sync_app"
$User   = "tuanpnq"
$Password   = "123"

# 1. Ensure log directory exists
if (!(Test-Path $LogFolder)) {
    New-Item -ItemType Directory -Path $LogFolder | Out-Null
}

foreach ($IP in $ServerList) {
    if ([string]::IsNullOrWhiteSpace($IP)) { continue }

    $Destination = "\\$IP\$RemoteShare"
    $LogPath = "$LogFolder\Sync_$($IP)_$(Get-Date -Format 'yyyyMMdd').txt"

    Write-Host "----------------------------------------------------" -ForegroundColor White
    Write-Host "Checking Connection to $IP..." -ForegroundColor Cyan

    # 2. Ping Check (Connection test)
    if (Test-Connection -ComputerName $IP -Count 1 -Quiet) {

        Write-Host "[OK] $IP is Online. Authenticating..." -ForegroundColor Green

        # 3. Handle Password Protection (Authentication)
        # This maps the drive temporarily to allow Robocopy access
        $NetPath = "\\$IP\IPC$" # IPC$ is a hidden share used for authentication
        net use $NetPath /user:$User $Password /persistent:no | Out-Null

        Write-Host ">>> Starting Sync to $Destination..." -ForegroundColor Yellow

        # 4. Run Robocopy
        robocopy $LocalFolder $Destination /MIR /LOG:$LogPath /TEE

        if ($LASTEXITCODE -le 8) {
            Write-Host "[SUCCESS] Synced $IP (Code: $LASTEXITCODE)" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Robocopy failed for $IP. Check log." -ForegroundColor Red
        }

        # 5. Cleanup Authentication (Disconnect)
        net use $NetPath /delete /y | Out-Null

    } else {
        Write-Host "[SKIP] $IP is Offline. Skipping sync." -ForegroundColor Gray
        Add-Content -Path $LogPath -Value "$(Get-Date): Machine was offline. Sync skipped."
    }
}

Write-Host "`n--- All Tasks Finished ---" -ForegroundColor Yellow
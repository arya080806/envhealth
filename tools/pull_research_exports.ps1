param(
    [string]$RemoteHost = "43.167.184.248",
    [string]$RemoteUser = "zm",
    [string]$RemoteProject = "/home/zm/envhealth",
    [string]$RemoteExport = "/home/zm/envhealth/research_exports",
    [string]$RemoteArchive = "/tmp/envhealth_research_exports.tar.gz",
    [string]$LocalRecordDir = "D:\SSH\环境游戏程序\记录",
    [string]$IdentityFile = "$env:USERPROFILE\.ssh\id_rsa"
)

$ErrorActionPreference = "Stop"

$ssh = "C:\Program Files\Git\usr\bin\ssh.exe"
$scp = "C:\Program Files\Git\usr\bin\scp.exe"
if (-not (Test-Path -LiteralPath $ssh)) { $ssh = "ssh" }
if (-not (Test-Path -LiteralPath $scp)) { $scp = "scp" }

New-Item -ItemType Directory -Force -Path $LocalRecordDir | Out-Null

$remote = "$RemoteUser@$RemoteHost"
$remoteCommand = "cd $RemoteProject && /home/zm/.local/bin/uv run python -m app.services.research_archive --output $RemoteExport && tar -C $RemoteExport -czf $RemoteArchive ."
Write-Host "Generating remote archive on $remote..."
& $ssh -i $IdentityFile -o BatchMode=yes -o ConnectTimeout=20 $remote $remoteCommand
if ($LASTEXITCODE -ne 0) {
    throw "Remote archive generation failed with exit code $LASTEXITCODE"
}

$localArchive = Join-Path $LocalRecordDir "research_exports_latest.tar.gz"
Write-Host "Pulling archive to $LocalRecordDir..."
& $scp -i $IdentityFile -o BatchMode=yes -o ConnectTimeout=20 "${remote}:$RemoteArchive" $localArchive
if ($LASTEXITCODE -ne 0) {
    throw "Archive download failed with exit code $LASTEXITCODE"
}

Write-Host "Extracting archive..."
& tar -xzf $localArchive -C $LocalRecordDir
if ($LASTEXITCODE -ne 0) {
    throw "Archive extraction failed with exit code $LASTEXITCODE"
}

Write-Host "Done. Index files:"
Write-Host "  $LocalRecordDir\index.xlsx"
Write-Host "  $LocalRecordDir\index.csv"

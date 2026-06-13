param(
    [string]$RemoteHost = "43.167.184.248",
    [string]$RemoteUser = "zm",
    [string]$RemoteProject = "/home/zm/envhealth",
    [string]$RemoteExport = "/home/zm/envhealth/research_exports",
    [string]$RemoteArchive = "/tmp/envhealth_research_exports.tar.gz",
    [string]$LocalRecordDir = "",
    [string]$IdentityFile = "$env:USERPROFILE\.ssh\id_rsa"
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($LocalRecordDir)) {
    $LocalRecordDir = $PSScriptRoot
}

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

$tempArchiveName = "envhealth_research_exports.tar.gz"
$tempArchive = Join-Path $env:TEMP $tempArchiveName
$localArchive = Join-Path $LocalRecordDir "research_exports_latest.tar.gz"
Remove-Item -LiteralPath $tempArchive -Force -ErrorAction SilentlyContinue
Write-Host "Pulling archive to $LocalRecordDir..."
Push-Location $env:TEMP
try {
    & $scp -i $IdentityFile -o BatchMode=yes -o ConnectTimeout=20 "${remote}:$RemoteArchive" $tempArchiveName
} finally {
    Pop-Location
}
if ($LASTEXITCODE -ne 0) {
    throw "Archive download failed with exit code $LASTEXITCODE"
}
Copy-Item -LiteralPath $tempArchive -Destination $localArchive -Force

Write-Host "Extracting archive..."
Remove-Item -LiteralPath (Join-Path $LocalRecordDir "participants") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $LocalRecordDir "index.csv") -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $LocalRecordDir "index.xlsx") -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $LocalRecordDir "manifest.json") -Force -ErrorAction SilentlyContinue
$pythonCandidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
)
$python = $pythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $python) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $python = $pythonCommand.Source }
}
if (-not $python) {
    throw "Python is required to extract UTF-8 archive paths correctly"
}
$extractCode = @'
import os
import tarfile
from pathlib import Path

archive = Path(os.environ["ENVHEALTH_ARCHIVE"])
dest = Path(os.environ["ENVHEALTH_DEST"]).resolve()

with tarfile.open(archive, "r:gz") as tf:
    for member in tf.getmembers():
        target = (dest / member.name).resolve()
        if dest != target and dest not in target.parents:
            raise RuntimeError(f"Unsafe archive path: {member.name}")
    tf.extractall(dest)
'@
$env:ENVHEALTH_ARCHIVE = $tempArchive
$env:ENVHEALTH_DEST = $LocalRecordDir
$extractScript = Join-Path $env:TEMP "envhealth_extract_research_archive.py"
Set-Content -LiteralPath $extractScript -Value $extractCode -Encoding UTF8
& $python $extractScript
if ($LASTEXITCODE -ne 0) {
    throw "Archive extraction failed with exit code $LASTEXITCODE"
}

Write-Host "Done. Index files:"
Write-Host "  $LocalRecordDir\index.xlsx"
Write-Host "  $LocalRecordDir\index.csv"

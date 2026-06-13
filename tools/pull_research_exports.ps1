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
& tar -xzf $tempArchive -C $LocalRecordDir
if ($LASTEXITCODE -ne 0) {
    throw "Archive extraction failed with exit code $LASTEXITCODE"
}

Write-Host "Done. Index files:"
Write-Host "  $LocalRecordDir\index.xlsx"
Write-Host "  $LocalRecordDir\index.csv"

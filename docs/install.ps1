$ErrorActionPreference = "Stop"

$Repo = "ndugram/fasthttp-gui"
$BinName = "fasthttp-gui"

function Get-LatestRelease {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -UseBasicParsing
    return $response
}

function Get-AssetUrl {
    param($Release, $Pattern)
    $asset = $Release.assets | Where-Object { $_.name -match $Pattern } | Select-Object -First 1
    return $asset.browser_download_url
}

$Release = Get-LatestRelease
$Version = $Release.tag_name

if (-not $Version) {
    Write-Error "Failed to fetch latest release version"
    exit 1
}

Write-Host "Installing $BinName $Version for windows/x86_64..."

$Url = Get-AssetUrl -Release $Release -Pattern "x64.*\.msi"
if (-not $Url) {
    $Url = Get-AssetUrl -Release $Release -Pattern "x64.*setup.*\.exe"
}
if (-not $Url) {
    $Url = Get-AssetUrl -Release $Release -Pattern "\.msi$"
}
if (-not $Url) {
    Write-Error "No Windows installer found in release $Version"
    exit 1
}

$FileName = [System.IO.Path]::GetFileName($Url)
$TmpPath = Join-Path $env:TEMP $FileName

Write-Host "Downloading: $Url"
Invoke-WebRequest -Uri $Url -OutFile $TmpPath -UseBasicParsing

Write-Host "Running installer..."
if ($FileName -match "\.msi$") {
    Start-Process msiexec.exe -ArgumentList "/i", "`"$TmpPath`"", "/passive" -Wait
} else {
    Start-Process $TmpPath -ArgumentList "/passive" -Wait
}

Remove-Item $TmpPath -Force
Write-Host "Installation complete"

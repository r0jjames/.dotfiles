<#
  vdi-apply-keymap.ps1 - install the Roj F-free keymap inside a Windows VDI.

  Run this INSIDE the Citrix Windows VDI (Path B fallback). The preferred
  path is JetBrains Settings Sync (Path A) - see intellij/README.md - which
  needs no script. Use this only if you are not using account sync.

Close IntelliJ before running. The config is overwritten when the IDE exits.  Usage (PowerShell in the VDI):
    powershell -ExecutionPolicy Bypass -File .\vdi-apply-keymap.ps1

  If the dotfiles repo is PRIVATE, raw.githubusercontent will 404. Either:
    - make the file reachable (public repo / gist / internal URL), or
    - pass -Url with a tokenised raw link, or
    - copy keymap-windows.xml in by hand and pass -LocalPath instead.
#>
param(
  [string]$Url = "https://raw.githubusercontent.com/r0jjames/.dotfiles/main/intellij/keymap-windows.xml",
  [string]$LocalPath = "",
  [string]$KeymapName = "roj-keymap"
)
$ErrorActionPreference = "Stop"

$jb = Join-Path $env:APPDATA "JetBrains"
if (-not (Test-Path $jb)) {
  throw "No '$jb' - launch IntelliJ once so it creates its config dir, then re-run."
}
$dirs = Get-ChildItem $jb -Directory | Where-Object { $_.Name -match "IntelliJIdea|IdeaIC" }
if (-not $dirs) {
  throw "No IntelliJ config dir under '$jb' - launch IntelliJ once, then re-run."
}

if ($LocalPath) {
  $xml = Get-Content -Raw -Path $LocalPath
} else {
  $xml = (Invoke-WebRequest -Uri $Url -UseBasicParsing).Content
}

foreach ($d in $dirs) {
  $km = Join-Path $d.FullName "keymaps"
  New-Item -ItemType Directory -Force -Path $km | Out-Null
  $dest = Join-Path $km "$KeymapName.xml"
  Set-Content -Path $dest -Value $xml -Encoding UTF8
  Write-Host "Installed keymap -> $dest"
}

Write-Host ""
Write-Host "Done. Now open IntelliJ -> Settings -> Keymap -> pick '$KeymapName'."
Write-Host "Then check the keymap for any red 'conflict' marks and adjust if needed."

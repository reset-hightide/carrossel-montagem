# Instala a skill carrossel-montagem no Claude Code (Windows). Rode no PowerShell:
#   powershell -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Claude = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
New-Item -ItemType Directory -Force -Path "$Claude\skills", "$Claude\commands", "$Claude\carrossel-marcas", "$HOME\Posts" | Out-Null
$Dest = "$Claude\skills\carrossel-montagem"
if (Test-Path $Dest) { New-Item -ItemType Directory -Force -Path "$Claude\skills-backup" | Out-Null; Move-Item $Dest "$Claude\skills-backup\carrossel-montagem.$(Get-Date -Format yyyyMMddHHmmss)" }
Copy-Item -Recurse "$Here\skill" $Dest
Copy-Item "$Here\commands\post.md" "$Claude\commands\post.md" -Force
Write-Host "skill instalada e comando /post criado"

$Venv = "$HOME\.venvs\post"
if (-not (Test-Path "$Venv\Scripts\python.exe")) { py -3 -m venv $Venv }
& "$Venv\Scripts\python.exe" -m pip install -q --upgrade pip
& "$Venv\Scripts\python.exe" -m pip install -q -r "$Here\requirements.txt"
Write-Host "venv pronto em $Venv"

$Desktop = [Environment]::GetFolderPath("Desktop")
Set-Content -Path "$Desktop\Novo carrossel.bat" -Value "@echo off`r`ncd /d %USERPROFILE%`r`nclaude --chrome `"/post`"`r`n"
Write-Host "atalho criado na Area de Trabalho: Novo carrossel.bat"

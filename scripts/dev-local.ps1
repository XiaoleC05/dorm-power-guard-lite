# DormGuard local dev (Windows PowerShell)
# Usage: .\scripts\dev-local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$EnvFile = Join-Path $Backend ".env"
$EnvExample = Join-Path $Backend ".env.local.example"

if (-not (Test-Path $EnvFile)) {
    if (-not (Test-Path $EnvExample)) {
        Write-Host "[ERROR] Missing backend\.env.local.example" -ForegroundColor Red
        exit 1
    }
    Copy-Item $EnvExample $EnvFile
    Write-Host "Created backend\.env from .env.local.example" -ForegroundColor Yellow
}

$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($docker) {
    Set-Location $Root
    Write-Host "Starting local MySQL (docker compose -f docker-compose.dev.yml)..." -ForegroundColor Cyan
    docker compose -f docker-compose.dev.yml up -d
    Write-Host "Waiting for MySQL..." -ForegroundColor Cyan
    Start-Sleep -Seconds 8
} else {
    Write-Host "[WARN] Docker not found. Ensure MySQL is on localhost:3306" -ForegroundColor Yellow
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python not found" -ForegroundColor Red
    exit 1
}

Set-Location $Backend
$venv = Join-Path $Backend "venv"
if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) {
    Write-Host "Creating venv and installing deps..." -ForegroundColor Cyan
    & python -m venv venv
    & (Join-Path $venv "Scripts\pip.exe") install -r requirements.txt
}

Write-Host "Starting DormGuard API http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "Health: http://127.0.0.1:8000/health" -ForegroundColor Gray
Write-Host "Oxelia51 gateway: http://localhost:8080/api/tools/dormguard/proxy/health" -ForegroundColor Gray
& (Join-Path $venv "Scripts\python.exe") run.py

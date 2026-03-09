# ─────────────────────────────────────────────────────────
# GoldLine Agent — Eval Suite Demo (PowerShell)
# Runs all tests (unit + LLM behavioral evals) and produces
# an HTML report you can open in any browser.
#
# Usage:
#   .\scripts\demo_evals.ps1              # full suite
#   .\scripts\demo_evals.ps1 -Unit        # unit tests only (no API keys)
#   .\scripts\demo_evals.ps1 -Evals       # LLM evals only
# ─────────────────────────────────────────────────────────
param(
    [switch]$Unit,
    [switch]$Evals
)

$ReportDir = "reports"
$ReportFile = "$ReportDir\eval-report.html"

if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir | Out-Null
}

$MarkerFlag = @()
$Label = "all tests (unit + LLM evals)"

if ($Unit) {
    $MarkerFlag = @("-m", "not eval")
    $Label = "unit tests only"
} elseif ($Evals) {
    $MarkerFlag = @("-m", "eval")
    $Label = "LLM behavioral evals only"
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Yellow
Write-Host "  GoldLine Agent - Eval Suite Demo" -ForegroundColor Yellow
Write-Host "  Running: $Label" -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Yellow
Write-Host ""

uv run pytest tests/ @MarkerFlag -v --tb=short --html="$ReportFile" --self-contained-html

Write-Host ""
Write-Host "------------------------------------------------------"
Write-Host "  Report saved: $ReportFile" -ForegroundColor Green
Write-Host "  Opening in browser..." -ForegroundColor Green
Write-Host "------------------------------------------------------"

Start-Process $ReportFile

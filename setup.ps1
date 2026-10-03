# =========================================================
# AMINOHYEAH TROUBLESHOOT TOOL - AUTO INSTALLER & RUNNER
# =========================================================

# 1. Semak & Install Python jika tiada
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python tidak dijumpai. Memasang Python..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

$baseUrl = "https://raw.githubusercontent.com/Amin-Ohyeah/Troubleshoot-Tools/main"
\(workDir = "\)env:TEMP\troubleshoot"

if (-not (Test-Path $workDir)) {
    New-Item -ItemType Directory -Path $workDir | Out-Null
}

Write-Host "`n[+] Mengunduh fail Aminohyeah Troubleshoot..." -ForegroundColor Cyan

$files = @("main.py", "checkdevice.py", "devicedetails.py", "networkdetails.py")
foreach (\(f in\)files) {
    Invoke-RestMethod -Uri "\(baseUrl/\)f" -OutFile "$workDir\$f"
}

Write-Host "[+] Menyemak modul Python..." -ForegroundColor Yellow
python -m pip install psutil py-cpuinfo --quiet --disable-pip-version-check

Set-Location $workDir
Clear-Host
python main.py

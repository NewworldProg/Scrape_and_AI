Write-Host "Starting N8N..." -ForegroundColor Cyan
Write-Host "N8N will be available at: http://localhost:5678" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop N8N" -ForegroundColor Gray
Write-Host ""

# Set N8N data directory to current project
$env:N8N_USER_FOLDER = Join-Path $PSScriptRoot ".n8n"

# Start only local project n8n
$localN8nCmd = Join-Path $PSScriptRoot "node_modules\.bin\n8n.cmd"

if (Test-Path $localN8nCmd) {
    & $localN8nCmd start
}
elseif (Get-Command npx -ErrorAction SilentlyContinue) {
    npx --no-install n8n start
}
else {
    Write-Error "Local n8n nije pronađen. Pokreni install_n8n.ps1 da instaliraš project-local n8n."
    exit 1
}

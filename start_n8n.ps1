Write-Host "Starting N8N..." -ForegroundColor Cyan
Write-Host "N8N will be available at: http://localhost:5678" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop N8N" -ForegroundColor Gray
Write-Host ""

# Set N8N data directory to current project
$env:N8N_USER_FOLDER = "E:\Repoi\Sa gita\Scrape_and_AI-main\.n8n"

# Start N8N
n8n start

param(
    [string]$ProjectRoot = $PWD.Path,
    [string]$OutputDir = "n8n"
)

# N8N All Workflows Generator
# Creates exact replicas of all N8N workflows with dynamic paths

Write-Host @"

                N8N WORKFLOW REPLICA GENERATOR                 
                   Generate Exact Workflow Copies                       

"@ -ForegroundColor Cyan

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host "Output: $ProjectRoot\$OutputDir" -ForegroundColor Yellow
Write-Host ""

# Create output directory if it doesn't exist
$outputPath = Join-Path $ProjectRoot $OutputDir
if (-not (Test-Path $outputPath)) {
    New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
    Write-Host "Created output directory: $outputPath" -ForegroundColor Green
}

Write-Host "Generating exact replicas of all N8N workflows..." -ForegroundColor Magenta
Write-Host ""

# Generate each workflow
try {
    Write-Host "1. Generating Conditional Workflow..." -ForegroundColor Yellow
    & (Join-Path $ProjectRoot "generate_conditional_workflow.ps1") -ProjectRoot $ProjectRoot -OutputDir $OutputDir
    Write-Host "   ✅ Conditional workflow replica generated" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "2. Generating Chat AI Workflow..." -ForegroundColor Yellow
    & (Join-Path $ProjectRoot "generate_chat_ai_workflow.ps1") -ProjectRoot $ProjectRoot -OutputDir $OutputDir
    Write-Host "   ✅ Chat AI workflow replica generated" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "3. Generating Cover Letter Workflow..." -ForegroundColor Yellow
    & (Join-Path $ProjectRoot "generate_cover_letter_workflow.ps1") -ProjectRoot $ProjectRoot -OutputDir $OutputDir
    Write-Host "   ✅ Cover letter workflow replica generated" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "4. Generating Database Cleanup Workflow..." -ForegroundColor Yellow
    & (Join-Path $ProjectRoot "generate_database_cleanup_workflow.ps1") -ProjectRoot $ProjectRoot -OutputDir $OutputDir
    Write-Host "   ✅ Database cleanup workflow replica generated" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "=== ALL WORKFLOW REPLICAS GENERATED SUCCESSFULLY ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Generated replica files:" -ForegroundColor White
    Write-Host "📄 n8n_workflow_conditional.json (12 nodes)" -ForegroundColor Gray
    Write-Host "📄 n8n_chat_ai_workflow.json (12 nodes)" -ForegroundColor Gray
    Write-Host "📄 n8n_ai_cover_letter_workflow.json (4 nodes)" -ForegroundColor Gray
    Write-Host "📄 n8n_database_cleanup_workflow.json (3 nodes)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "All replicas configured with paths: $ProjectRoot" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Start N8N: n8n start" -ForegroundColor Gray
    Write-Host "2. Import all .json files from: $outputPath" -ForegroundColor Gray
    Write-Host "3. Activate workflows as needed" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🎉 Perfect replicas ready for your Upwork automation!" -ForegroundColor Magenta
}
catch {
    Write-Host "❌ Error generating workflow replicas: $_" -ForegroundColor Red
    exit 1
}

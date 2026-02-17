param(
    [string]$ProjectRoot = $PWD.Path,
    [string]$OutputDir = "n8n"
)

# N8N AI Cover Letter Workflow Generator
# Creates exact replica of the AI Cover Letter workflow with dynamic paths

Write-Host "=== N8N AI Cover Letter Workflow Generator ===" -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host "Output: $ProjectRoot\$OutputDir" -ForegroundColor Yellow
Write-Host ""

# Normalize path for JSON (double backslashes for JSON escaping)
$pathForJson = $ProjectRoot.Replace('\', '\\')

# Create output directory if it doesn't exist
$outputPath = Join-Path $ProjectRoot $OutputDir
if (-not (Test-Path $outputPath)) {
    New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
}

# Generate the complete AI cover letter workflow using hashtable
$coverLetterWorkflow = [ordered]@{
    name = "AI Cover Letter Generator - Scheduled"
    nodes = @(
        @{
            "__comment" = "======== node for triggering workflow every 5 minutes =============="
            "works" = "interval field takes arguments like minutes, hours, days etc."
            parameters = @{
                rule = @{
                    interval = @(
                        @{
                            field = "minutes"
                            minutesInterval = 5
                        }
                    )
                }
            }
            id = "ai-trigger-1"
            name = "Every 5 Minutes"
            type = "n8n-nodes-base.scheduleTrigger"
            typeVersion = 1.1
            position = @(140, 300)
        },
        @{
            "__comment" = "======== node for getting latest job without cover letter =============="
            "works" = "gets latest job without cover letter using UpworkDatabase class"
            parameters = @{
                command = "powershell -ExecutionPolicy Bypass -File `"$pathForJson\\run_scripts\\run_get_latest_job_without_cover_letter.ps1`""
                workingDirectory = $pathForJson
            }
            id = "get-latest-job-1"
            name = "Get Latest Job Without Cover Letter"
            type = "n8n-nodes-base.executeCommand"
            typeVersion = 1
            position = @(340, 300)
        },
        @{
            "__comment" = "======== node for calling trained local AI model to generat cover letter =============="
            "works" = "goes in folder of program and runs the PowerShell script to generate cover letter using local AI model"
            parameters = @{
                command = "powershell -ExecutionPolicy Bypass -File `"$pathForJson\\run_scripts\\run_smart_cover_letter.ps1`""
                workingDirectory = $pathForJson
            }
            id = "ai-generator-1"
            name = "Smart AI Cover Letter"
            type = "n8n-nodes-base.executeCommand"
            typeVersion = 1
            position = @(540, 300)
        },
        @{
            "__comment" = "======== node for refreshing dashboard after cover letter generation =============="
            parameters = @{
                command = "powershell -ExecutionPolicy Bypass -File `"$pathForJson\\run_scripts\\run_generate_and_open_dashboard.ps1`""
                workingDirectory = $pathForJson
            }
            id = "ai-dashboard-1"
            name = "Refresh Dashboard"
            type = "n8n-nodes-base.executeCommand"
            typeVersion = 1
            position = @(740, 300)
        }
    )
    pinData = @{}
    settings = @{}
    staticData = @{}
    tags = @()
    triggerCount = 0
    updatedAt = "2025-10-27T19:20:00.000Z"
    versionId = "001"
}

# Convert to JSON and save - build connections manually for proper format
Write-Host "1. Creating AI cover letter workflow..." -ForegroundColor Green

# Build proper JSON structure manually
$jsonParts = @()
$jsonParts += '{'
$jsonParts += '    "name": "AI Cover Letter Generator - Scheduled",'

# Add nodes section
$nodesJson = ($coverLetterWorkflow.nodes | ConvertTo-Json -Depth 10) -replace '^', '    ' -replace '(?m)^', '    '
$jsonParts += '    "nodes": ' + $nodesJson + ','

# Add connections manually with proper format
$jsonParts += '    "connections": {'
$connections = @(
    '"Every 5 Minutes": { "main": [[ { "node": "Get Latest Job Without Cover Letter", "type": "main", "index": 0 } ]] }',
    '"Get Latest Job Without Cover Letter": { "main": [[ { "node": "Smart AI Cover Letter", "type": "main", "index": 0 } ]] }',
    '"Smart AI Cover Letter": { "main": [[ { "node": "Refresh Dashboard", "type": "main", "index": 0 } ]] }'
)
for ($i = 0; $i -lt $connections.Length; $i++) {
    $comma = if ($i -lt $connections.Length - 1) { ',' } else { '' }
    $jsonParts += "        $($connections[$i])$comma"
}
$jsonParts += '    },'

# Add metadata
$jsonParts += '    "pinData": {},'
$jsonParts += '    "settings": {},'
$jsonParts += '    "staticData": {},'
$jsonParts += '    "tags": [],'
$jsonParts += '    "triggerCount": 0,'
$jsonParts += '    "updatedAt": "2025-10-27T19:20:00.000Z",'
$jsonParts += '    "versionId": "001"'
$jsonParts += '}'

$jsonContent = $jsonParts -join "`n"
$outputFile = Join-Path $outputPath "n8n_ai_cover_letter_workflow.json"
$jsonContent | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "Created: n8n_ai_cover_letter_workflow.json" -ForegroundColor White

Write-Host ""
Write-Host "=== GENERATION COMPLETE ===" -ForegroundColor Cyan
Write-Host "Created AI cover letter workflow in: $outputPath" -ForegroundColor Green
Write-Host "All paths configured for: $ProjectRoot" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Start N8N: n8n start" -ForegroundColor Gray
Write-Host "2. Import this .json file" -ForegroundColor Gray  
Write-Host "3. Activate workflow" -ForegroundColor Gray
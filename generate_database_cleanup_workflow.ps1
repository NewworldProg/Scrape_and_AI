param(
    [string]$ProjectRoot = $PWD.Path,
    [string]$OutputDir = "n8n"
)

# N8N Database Cleanup Workflow Generator
# Creates exact replica of the Database Cleanup workflow with dynamic paths

Write-Host "=== N8N Database Cleanup Workflow Generator ===" -ForegroundColor Cyan
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

# Generate the complete database cleanup workflow using hashtable
$cleanupWorkflow = [ordered]@{
    name = "Simple Database Cleanup"
    nodes = @(
        @{
            parameters = @{}
            id = "0b3de4a8-c4c4-4f7f-9b9b-0d7f8e9c2a1b"
            name = "Manual Trigger"
            type = "n8n-nodes-base.manualTrigger"
            typeVersion = 1
            position = @(240, 300)
        },
        @{
            parameters = @{
                rule = @{
                    interval = @(
                        @{
                            field = "hours"
                            hoursInterval = 6
                        }
                    )
                }
            }
            id = "1c4e5a9d-d5d5-5f8f-ac4c-1e8f9f0d3c2c"
            name = "Schedule Trigger"
            type = "n8n-nodes-base.scheduleTrigger"
            typeVersion = 1.1
            position = @(240, 480)
        },
        @{
            parameters = @{
                command = "python `"$pathForJson\\scripts\\simple_n8n_cleanup.py`""
                options = @{}
            }
            id = "2d5f6b0e-e6e6-6f9f-bd5d-2f9f0f1e4d3d"
            name = "Run Cleanup"
            type = "n8n-nodes-base.executeCommand"
            typeVersion = 1
            position = @(460, 390)
        }
    )
    pinData = @{}
    settings = @{
        executionOrder = "v1"
    }
    staticData = $null
    tags = @(
        @{
            id = "database"
            name = "database"
        },
        @{
            id = "maintenance"
            name = "maintenance"
        }
    )
    triggerCount = 2
    updatedAt = "2025-11-10T14:40:00.000Z"
    versionId = "2"
}

# Convert to JSON and save - build connections manually for proper format
Write-Host "1. Creating database cleanup workflow..." -ForegroundColor Green

# Build proper JSON structure manually
$jsonParts = @()
$jsonParts += '{'
$jsonParts += '    "name": "Simple Database Cleanup",'

# Add nodes section
$nodesJson = ($cleanupWorkflow.nodes | ConvertTo-Json -Depth 10) -replace '^', '    ' -replace '(?m)^', '    '
$jsonParts += '    "nodes": ' + $nodesJson + ','

# Add connections manually with proper format
$jsonParts += '    "connections": {'
$connections = @(
    '"Manual Trigger": { "main": [[ { "node": "Run Cleanup", "type": "main", "index": 0 } ]] }',
    '"Schedule Trigger": { "main": [[ { "node": "Run Cleanup", "type": "main", "index": 0 } ]] }'
)
for ($i = 0; $i -lt $connections.Length; $i++) {
    $comma = if ($i -lt $connections.Length - 1) { ',' } else { '' }
    $jsonParts += "        $($connections[$i])$comma"
}
$jsonParts += '    },'

# Add metadata
$jsonParts += '    "pinData": {},'
$jsonParts += '    "settings": { "executionOrder": "v1" },'
$jsonParts += '    "staticData": null,'
$jsonParts += '    "tags": ['
$jsonParts += '        { "id": "database", "name": "database" },'
$jsonParts += '        { "id": "maintenance", "name": "maintenance" }'
$jsonParts += '    ],'
$jsonParts += '    "triggerCount": 2,'
$jsonParts += '    "updatedAt": "2025-11-10T14:40:00.000Z",'
$jsonParts += '    "versionId": "2"'
$jsonParts += '}'

$jsonContent = $jsonParts -join "`n"
$outputFile = Join-Path $outputPath "n8n_database_cleanup_workflow.json"
$jsonContent | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "Created: n8n_database_cleanup_workflow.json" -ForegroundColor White

Write-Host ""
Write-Host "=== GENERATION COMPLETE ===" -ForegroundColor Cyan
Write-Host "Created database cleanup workflow in: $outputPath" -ForegroundColor Green
Write-Host "All paths configured for: $ProjectRoot" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Start N8N: n8n start" -ForegroundColor Gray
Write-Host "2. Import this .json file" -ForegroundColor Gray  
Write-Host "3. Activate workflow" -ForegroundColor Gray
# Chat Database Cleanup Script Runner
# Standalone cleanup script for N8N Chat AI Workflow
# Removes duplicate chat sessions without interfering with parser

$projectRoot = Split-Path $PSScriptRoot -Parent

# Set UTF-8 encoding for Windows console
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Chat Database Cleanup Starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

try {
    # Change to project directory
    Set-Location $projectRoot
    
    # Activate virtual environment if it exists
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-Host "Activating virtual environment..." -ForegroundColor Yellow
        & "venv\Scripts\Activate.ps1"
    }
    
    # Run cleanup script directly with Start-Process for proper isolation
    Write-Host "Running chat database cleanup..." -ForegroundColor Yellow
    $process = Start-Process -FilePath "python" -ArgumentList "scripts\cleanup_chat_database.py" -PassThru -NoNewWindow -Wait -RedirectStandardOutput "temp_cleanup_output.txt" -RedirectStandardError "temp_cleanup_error.txt"
    
    # Read and display output
    if (Test-Path "temp_cleanup_output.txt") {
        $output = Get-Content "temp_cleanup_output.txt" -Raw -Encoding UTF8
        if ($output) {
            Write-Host $output
        }
        Remove-Item "temp_cleanup_output.txt" -Force -ErrorAction SilentlyContinue
    }
    
    # Check for errors
    if (Test-Path "temp_cleanup_error.txt") {
        $errors = Get-Content "temp_cleanup_error.txt" -Raw -Encoding UTF8
        if ($errors -and $errors.Trim()) {
            Write-Host "Errors:" -ForegroundColor Red
            Write-Host $errors -ForegroundColor Red
        }
        Remove-Item "temp_cleanup_error.txt" -Force -ErrorAction SilentlyContinue
    }
    
    if ($process.ExitCode -eq 0) {
        Write-Host "Chat database cleanup completed successfully!" -ForegroundColor Green
        exit 0
    }
    else {
        Write-Host "Chat database cleanup failed with exit code: $($process.ExitCode)" -ForegroundColor Red
        exit $process.ExitCode
    }
    
}
catch {
    Write-Host "Error during chat database cleanup: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Chat Database Cleanup Finished" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
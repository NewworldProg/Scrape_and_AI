param(
    [Parameter(Mandatory=$true)][string]$ScriptPath,
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments
)
Write-Host "Running: $ScriptPath" -ForegroundColor Cyan
& "E:\Repoi\Sa gita\Scrape_and_AI-main\venv\Scripts\Activate.ps1"
Set-Location "E:\Repoi\Sa gita\Scrape_and_AI-main"
if ($Arguments) { & $ScriptPath @Arguments } else { & $ScriptPath }

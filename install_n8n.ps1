# takes parameters from the command line to determine
# dry run, force reinstall, workflows only, and install path with default path "."
param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$WorkflowsOnly,
    [string]$InstallPath = "."
)

# Enhanced N8N Scrape and AI Automation System Installer
# Version 2.0 - Complete Installation with Node.js Dependencies
# log that installer is starting
# give it neon color (foreground cyan)
Write-Host @"

                N8N SCRAPE & AI AUTOMATION SYSTEM                 
                    Enhanced Auto-Installer                       

"@ -ForegroundColor Cyan
# log if dry run is activated which means no changes will be made just checking if steps would succeed
if ($DryRun) {
    Write-Host " DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Setup paths
# inside var put Get_location function for checking current directory
$originalPath = Get-Location
# inside newBasePath var put Resolve-Path function for getting full path of install location = "."
$newBasePath = Resolve-Path $InstallPath
# make venvPath var Join-Path function newPath + "venv"
$venvPath = Join-Path $newBasePath "venv"

# log installation path that will be used
Write-Host " Installation Path: $newBasePath" -ForegroundColor Green
Write-Host ""

# log STEP 1: NODE.JS DEPENDENCIES
Write-Host " STEP 1: Installing Node.js Dependencies..." -ForegroundColor Magenta

# inside var script to check for Node.js + write log if found or not found
try {
    $nodeVersion = node --version
    Write-Host "   Node.js found: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "   Node.js not found! Please install Node.js first." -ForegroundColor Red
    exit 1
}

# inside dar script to check for npm  + write log if found or not found
try {
    $npmVersion = npm --version
    Write-Host "   npm found: $npmVersion" -ForegroundColor Green
}
catch {
    Write-Host "   npm not found!" -ForegroundColor Red
    exit 1
}

# Check for Chrome installation
Write-Host "`n🌐 Checking browser requirements..." -ForegroundColor Cyan

$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", 
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chromeFound = $false
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        Write-Host "   ✅ Chrome found: $path" -ForegroundColor Green
        $chromeFound = $true
        break
    }
}

if (-not $chromeFound) {
    Write-Host "   ❌ Chrome not found!" -ForegroundColor Red
    Write-Host "   📦 Chrome is REQUIRED for web scraping functionality" -ForegroundColor Yellow
    Write-Host "   🔗 Download Chrome: https://www.google.com/chrome/" -ForegroundColor Yellow
    Write-Host ""
    
    $continue = Read-Host "Continue installation without Chrome? Web scraping will NOT work. (y/N)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Host "❌ Installation cancelled. Please install Chrome first." -ForegroundColor Red
        exit 1
    }
    Write-Host "   ⚠️ Continuing without Chrome - web scraping disabled" -ForegroundColor Yellow
}
else {
    Write-Host "   🎯 Chrome verification passed" -ForegroundColor Green
}

# Install N8N locally in project (pin to compatible version)
$desiredN8nVersion = "1.46.0"
Write-Host "   Ensuring local N8N version: $desiredN8nVersion" -ForegroundColor Yellow

# Check if package.json exists by joining dir path and package.json if not makes one
# install local dependencies inside package.json if not in DryRun mode
$packageJsonPath = Join-Path $newBasePath "package.json"
if (Test-Path $packageJsonPath) {
    Write-Host "   Installing local Node.js dependencies (single pass)..." -ForegroundColor Yellow
    if (-not $DryRun) {
        Set-Location $newBasePath
        npm install --save-exact "n8n@$desiredN8nVersion"
        Write-Host "   Local dependencies installed" -ForegroundColor Green
        Write-Host "   Local N8N installed: $desiredN8nVersion" -ForegroundColor Green
    }
}
else {
    Write-Host "    No package.json found - creating with required dependencies..." -ForegroundColor Yellow
    if (-not $DryRun) {
        Set-Location $newBasePath
        
        # local dependencies that will be added to package.json
        $packageJson = @{
            name            = "scrape-ai-automation-system"
            version         = "1.0.0"
            description     = "Automated job scraping and notification system for Upwork"
            main            = "index.js"
            scripts         = @{
                start  = "node index.js"
                scrape = "node js_scrapers/upwork_scraper.js"
                test   = "echo Error: no test specified"
            }
            repository      = @{
                type = "git"
                url  = "https://github.com/username/scrape-ai-automation-system.git"
            }
            keywords        = @("upwork", "scraping", "automation", "notifications", "n8n")
            author          = "Your Name"
            license         = "MIT"
            dependencies    = @{
                "n8n"                = "$desiredN8nVersion"
                "puppeteer-core"     = "^21.0.0"
                "puppeteer"          = "^21.0.0"
                "selenium-webdriver" = "^4.15.0"
                "cheerio"            = "^1.0.0-rc.12"
                "fs-extra"           = "^11.1.1"
                "axios"              = "^1.6.0"
                "dotenv"             = "^16.3.1"
            }
            devDependencies = @{
                "nodemon" = "^3.0.0"
            }
            engines         = @{
                node = ">=18.0.0"
                npm  = ">=9.0.0"
            }
        }
        
        $packageJson | ConvertTo-Json -Depth 4 | Out-File -FilePath "package.json" -Encoding UTF8
        
        # Install dependencies after creating package.json
        npm install
        Write-Host "   Created package.json and installed dependencies" -ForegroundColor Green
    }
}

# STEP 2: PYTHON VIRTUAL ENVIRONMENT (if not workflows-only)
# if not workflows-only flag is set skip python venv setup
if (-not $WorkflowsOnly) {
    Write-Host "`n STEP 2: Python Virtual Environment..." -ForegroundColor Magenta
    # Check if venv exists
    # if force flag is set delete and recreate
    # if not force flag if venv exists skip creation and tell user that venv exists
    # create venv it it does not exist or force is set inside venvPath
    # activate venv and install packages from requirements.txt or common packages
    # 1. make activateScript with venvPath + Scripts\Activate.ps1
    # 2. activate venv
    # 3. install packages
    if (Test-Path $venvPath) {
        if ($Force) {
            Write-Host "  [DELETE] Removing existing environment..." -ForegroundColor Yellow
            if (-not $DryRun) {
                Remove-Item $venvPath -Recurse -Force
            }
        }
        else {
            Write-Host "   Virtual environment exists (use -Force to recreate)" -ForegroundColor Green
        }
    }
    if (-not (Test-Path $venvPath) -or $Force) {
        Write-Host "   Creating Python virtual environment..." -ForegroundColor Yellow
        if (-not $DryRun) {
            python -m venv $venvPath
            Write-Host "   Virtual environment created" -ForegroundColor Green
            
            # Install Python packages
            Write-Host "   Installing Python packages..." -ForegroundColor Yellow
            $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
            & $activateScript
            
            # Install packages from requirements.txt if exists
            $requirementsPath = Join-Path $newBasePath "requirements.txt"
            if (Test-Path $requirementsPath) {
                pip install -r $requirementsPath
            }
            else {
                # Install common packages
                pip install selenium beautifulsoup4 requests pandas numpy python-dotenv
            }
            
            Write-Host "   Python packages installed" -ForegroundColor Green
        }
    }
    
    # Create helper scripts
    if (-not $DryRun) {
        Write-Host "   Creating helper scripts..." -ForegroundColor Yellow
        
        # Create activate script with venvPath + Scripts\Activate.ps1 + your custom message
        $activateContent = @"
Write-Host "Activating Scrape and AI Automation System..." -ForegroundColor Cyan
& "$venvPath\Scripts\Activate.ps1"
Write-Host "Environment activated! Project: $newBasePath" -ForegroundColor Green
"@
        $activateContent | Out-File -FilePath "activate_env.ps1" -Encoding UTF8
        
        # Create run with venv script
        $runVenvContent = @"
param(
    [Parameter(Mandatory=`$true)][string]`$ScriptPath,
    [Parameter(ValueFromRemainingArguments=`$true)][string[]]`$Arguments
)
Write-Host "Running: `$ScriptPath" -ForegroundColor Cyan
& "$venvPath\Scripts\Activate.ps1"
Set-Location "$newBasePath"
if (`$Arguments) { & `$ScriptPath @Arguments } else { & `$ScriptPath }
"@
        $runVenvContent | Out-File -FilePath "run_with_venv.ps1" -Encoding UTF8
        
        # Create N8N launcher script
        $startN8nContent = @"
Write-Host "Starting N8N..." -ForegroundColor Cyan
Write-Host "N8N will be available at: http://localhost:5678" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop N8N" -ForegroundColor Gray
Write-Host ""

# Set N8N data directory to current project
`$env:N8N_USER_FOLDER = "$newBasePath\.n8n"

# Start local project N8N
`$localN8nCmd = Join-Path `$PSScriptRoot "node_modules\.bin\n8n.cmd"
if (Test-Path `$localN8nCmd) {
    & `$localN8nCmd start
}
elseif (Get-Command npx -ErrorAction SilentlyContinue) {
    npx --no-install n8n start
}
else {
    Write-Error "Local n8n nije pronađen. Pokreni install_n8n.ps1 da instaliraš project-local n8n."
    exit 1
}
"@
        $startN8nContent | Out-File -FilePath "start_n8n.ps1" -Encoding UTF8
        
        Write-Host "   Helper scripts created" -ForegroundColor Green
    }


}

# STEP 3: N8N WORKFLOWS generation using template system
Write-Host "`n STEP 3: N8N Workflow Generation..." -ForegroundColor Magenta

if (-not $DryRun) {
    Write-Host "   Generating N8N workflows with correct paths..." -ForegroundColor Yellow
    
    # Use the new comprehensive workflow generator system
    $allWorkflowsScript = Join-Path $newBasePath "generate_all_workflows.ps1"
    if (Test-Path $allWorkflowsScript) {
        # Run the master workflow generator
        & $allWorkflowsScript -ProjectRoot $newBasePath -OutputDir "n8n"
        Write-Host "   ✅ All N8N workflows generated successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️ Master generator not found - trying individual generators..." -ForegroundColor Yellow
        
        # Fallback: try individual generators
        $generators = @(
            "generate_conditional_workflow.ps1",
            "generate_chat_ai_workflow.ps1", 
            "generate_cover_letter_workflow.ps1",
            "generate_database_cleanup_workflow.ps1"
        )
        
        $generatedCount = 0
        foreach ($generator in $generators) {
            $generatorPath = Join-Path $newBasePath $generator
            if (Test-Path $generatorPath) {
                try {
                    & $generatorPath -ProjectRoot $newBasePath -OutputDir "n8n"
                    $generatedCount++
                    Write-Host "     ✅ Generated workflow from $generator" -ForegroundColor Gray
                }
                catch {
                    Write-Host "     ❌ Failed to generate from $generator" -ForegroundColor Red
                }
            }
        }
        
        if ($generatedCount -gt 0) {
            Write-Host "   ✅ Generated $generatedCount workflow(s) using individual generators" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️ No workflow generators found - creating basic n8n directory" -ForegroundColor Yellow
            $n8nDir = Join-Path $newBasePath "n8n"
            if (-not (Test-Path $n8nDir)) {
                New-Item -ItemType Directory -Path $n8nDir -Force | Out-Null
                Write-Host "   Created n8n/ directory" -ForegroundColor Green
            }
        }
    }
}
else {
    Write-Host "   [DRY RUN] Would generate N8N workflows using template system" -ForegroundColor Cyan
}

# STEP 4: FINAL SETUP AND SUMMARY
# log installation complete and summary of steps done
Write-Host "`n Installation Complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host " Summary:" -ForegroundColor White
Write-Host " Node.js dependencies installed" -ForegroundColor Gray
Write-Host " N8N installed locally (project-only)" -ForegroundColor Gray
if (-not $WorkflowsOnly) {
    Write-Host " Python virtual environment ready" -ForegroundColor Gray
    Write-Host " Helper scripts created" -ForegroundColor Gray
}

Write-Host "`n Next Steps:" -ForegroundColor Yellow
Write-Host "1. Start N8N: .\start_n8n.ps1" -ForegroundColor White
Write-Host "2. Import workflows from the .json files" -ForegroundColor White
if (-not $WorkflowsOnly) {
    Write-Host "3. Activate Python environment: .\activate_env.ps1" -ForegroundColor White
}

Write-Host "`n 🎉 Enjoy your Scrape and AI Automation System!" -ForegroundColor Magenta

# Return to original location
Set-Location $originalPath

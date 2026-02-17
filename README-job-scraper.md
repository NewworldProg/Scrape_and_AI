# 🔍 Job Scraper Workflow

**File**: `n8n_workflow_conditional.json`  
**Purpose**: Automated job scraping with Chrome debug mode bypass  
**Trigger**: can be triggered manualy or scheduled    

---

## 🎯 How It Works

This workflow scrapes job listings from any webpage by using Chrome debug mode to bypass anti-automation protection.

### 🔄 Workflow Steps

```
Start
  ↓
Check Chrome Status (Port 9222)
  ↓
IF Chrome Ready?
  ├─ YES → Wait for Human Navigation (20s)
  └─ NO  → Start Chrome → Wait 6s → Check Again
  ↓
Run JavaScript Scraper (Puppeteer)
  ↓
Save HTML to Database
  ↓
Parse HTML to Extract Job Details
  ↓
Import Jobs to Database
  ↓
Generate & Open Dashboard
```

### 📁 Files Used

| File | Purpose |
|------|---------|
| `run_check_chrome_n8n.ps1` | Check if Chrome debug mode is running |
| `run_start_chrome_simple.ps1` | Start Chrome in debug mode (port 9222) |
| `run_js_scraper.ps1` | Execute Puppeteer job scraper |
| `run_save_html_to_db.ps1` | Save scraped HTML to database |
| `run_parse_html_only.ps1` | Parse HTML and extract job data |
| `run_import_jobs_to_db.ps1` | Import parsed jobs to database |
| `run_generate_and_open_dashboard.ps1` | Create job dashboard |

### 🤖 Core Components

#### **JavaScript Scraper**
- **File**: `js_scrapers/browser_connect_puppeteer.js`
- **Function**: Connects to Chrome debug session and scrapes page HTML
- **Port**: 9222 (dedicated for job scraping)

#### **HTML Parser**
- **File**: `scripts/data_parser.py` 
- **Function**: Extracts job title, description, budget, skills from HTML
- **Output**: Structured job data

#### **Database Manager**
- **File**: `data/database_manager.py`
- **Function**: Manages job storage in SQLite database
- **Tables**: `jobs`, `html_snapshots`

#### **Dashboard Generator**
- **File**: `dashboard_generate/generate_dashboard_enhanced.py`
- **Function**: Creates interactive HTML dashboard with job stats
- **Output**: `dashboard.html`

---

## 🛠️ Troubleshooting

### Chrome Connection Issues
```powershell
# Check if port is in use
netstat -ano | findstr :9222

# Kill Chrome processes
taskkill /F /IM chrome.exe

# Restart Chrome debug
chrome.exe --remote-debugging-port=9222 --user-data-dir="chrome_profile"
```

### No Jobs Found
- Verify Chrome is logged in to target site
- Check if page structure changed (update parser)
- Ensure proper navigation before scraping starts

### Database Errors
- Check write permissions for database file
- Verify SQLite database integrity
- Clear old HTML snapshots if database is large

---

## 📊 Expected Output

After successful execution:
- **Jobs Database**: New job entries in `upwork_data.db`
- **HTML Snapshots**: Raw HTML saved for debugging
- **Dashboard**: Updated `dashboard.html` with latest jobs
- **Console Logs**: Detailed execution logs in n8n

The dashboard provides:
- Job count statistics
- Recent job listings
- Cover letter status tracking
- Filter and search capabilities
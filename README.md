# 🤖 Scrape and AI Automation System

**Complete automated system for web scraping and AI automation with intelligent chat responses, content generation, and data processing**

## ⚠️ **BEFORE YOU START**

**Starting AI models use base/untrained models with fallback logic:**
- **Phase Detection**: Uses base BERT (lower accuracy)  
- **Chat Responses**: Uses base GPT-2 (less contextual)
- **Cover Letters**: Uses base GPT-2 (generic responses)

**For better performance, train custom models using the training data in:**
- [`ai/phase_detector_trainer/`](ai/phase_detector_trainer/) - BERT phase detection training
- [`ai/chat_bot_trainer/`](ai/chat_bot_trainer/) - GPT-2 chat response training  
- [`ai/cover_letter_trainer/`](ai/cover_letter_trainer/) - GPT-2 cover letter training

📖 **[See AI Training Guide](README-ai-training.md)** for detailed instructions.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-16+-green.svg)
![n8n](https://img.shields.io/badge/n8n-workflow-orange.svg)
![BERT](https://img.shields.io/badge/ML-BERT-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

##  How It Works

This system uses **n8n workflows** to orchestrate automated web scraping and AI automation tasks:

```
n8n Frontend → PowerShell Scripts → Python/JavaScript Code
```

### 🎯 **4 Independent Workflows**

| Workflow | Description | README |
|----------|-------------|---------|
| **Web Scraper** | Automated web scraping with Chrome debug mode | [📖 README-job-scraper.md](README-job-scraper.md) |
| **AI Cover Letter Generator** | AI-powered personalized cover letter generation | [📖 README-cover-letter.md](README-cover-letter.md) |
| **Chat AI Assistant** | Smart chat responses with BERT + GPT-2 | [📖 README-chat-ai.md](README-chat-ai.md) |
| **Database Cleanup** | Automated database maintenance | [📖 README-database-cleanup.md](README-database-cleanup.md) |

### ⚙️ **How Scripts Execute**

1. **n8n Workflow** triggers on schedule or manual activation
2. **PowerShell Script** (`run_scripts/`) executes with parameters
3. **Python/JavaScript Code** (`scripts/`, `ai/`, `js_scrapers/`) performs the actual work
4. **Database Storage** (`data/`) saves results
5. **Dashboard Generation** (`dashboard_generate/`) creates HTML reports

---

## 📁 Project Structure

```
📦 UpworkNotif/
├── 🎯 N8N Workflow System
│   ├── 🔧 generate_all_workflows.ps1        # Master workflow generator
│   ├── 🔧 generate_conditional_workflow.ps1  # Job scraping pipeline generator  
│   ├── 🔧 generate_chat_ai_workflow.ps1     # Chat AI processing generator
│   ├── 🔧 generate_cover_letter_workflow.ps1 # Cover letter AI generator
│   ├── 🔧 generate_database_cleanup_workflow.ps1 # Database maintenance generator
│   ├── 📄 n8n_workflow_conditional.json    # Original workflow templates
│   ├── 📄 n8n_chat_ai_workflow.json        # Original chat AI workflow
│   ├── 📄 n8n_ai_cover_letter_workflow.json # Original cover letter workflow
│   ├── 📄 n8n_database_cleanup_workflow.json # Original cleanup workflow
│   └── 📁 n8n/                              # Generated workflows (auto-created)
│       ├── n8n_workflow_conditional.json    # → Generated with correct paths
│       ├── n8n_chat_ai_workflow.json        # → Generated with correct paths
│       ├── n8n_ai_cover_letter_workflow.json # → Generated with correct paths
│       └── n8n_database_cleanup_workflow.json # → Generated with correct paths
│
├── 📦 Installation & Setup
│   ├── 🔧 install_n8n.ps1                   # Auto-installer with template-based workflows
│   ├── 🚀 start_n8n.ps1                     # N8N launcher with project config
│   ├── 🐍 activate_env.ps1                  # Python environment activator
│   ├── ⚙️ run_with_venv.ps1                 # Script runner in virtual environment
│   ├── 📋 INSTALLATION_GUIDE.md             # Detailed installation instructions
│   └── 📄 requirements.txt                  # Python dependencies
│
├── 🎮 Automation Scripts
│   ├── 📁 run_scripts/                      # PowerShell automation runners (19 files)
│   │   ├── run_check_chrome_n8n.ps1         # Chrome status checker (port 9222)
│   │   ├── run_check_chrome_chat.ps1        # Chat Chrome status (port 9223)
│   │   ├── run_start_chrome_simple.ps1      # Chrome automation starter
│   │   ├── run_start_chrome_chat_simple.ps1 # Chat Chrome starter
│   │   ├── run_js_scraper.ps1               # JavaScript scraper runner
│   │   ├── run_chat_scraper.ps1             # Chat scraper runner
│   │   ├── run_save_html_to_db.ps1          # HTML database saver
│   │   ├── run_parse_html_only.ps1          # HTML parser
│   │   ├── run_chat_parser.ps1              # Chat parser runner
│   │   ├── run_import_jobs_to_db.ps1        # Job data importer
│   │   ├── run_generate_and_open_dashboard.ps1 # Dashboard generator
│   │   ├── run_generate_and_open_chat_dashboard.ps1 # Chat dashboard
│   │   ├── run_smart_cover_letter.ps1       # AI cover letter generator
│   │   ├── run_detect_phase_standalone.ps1  # Phase detection runner
│   │   ├── run_generate_response.ps1        # Response generator
│   │   ├── run_get_latest_job_without_cover_letter.ps1 # Job selector
│   │   └── run_cleanup_chat_database.ps1    # Chat database cleanup
│   └── 📁 scripts/                          # Python core scripts (20+ files)
│       ├── cleanup_job_database.py          # Main database cleanup
│       ├── cleanup_chat_database.py         # Chat database cleanup
│       ├── data_parser.py                   # Data parsing utilities
│       ├── chat_parser.py                   # Chat data parser
│       ├── phase_detector.py                # Job phase detection
│       ├── standalone_phase_detector.py     # Standalone phase detector
│       ├── smart_chat_response.py           # AI chat response generator
│       ├── smart_cover_letter_generator.py  # AI cover letter generator
│       ├── save_html_to_db.py               # HTML database operations
│       ├── parse_html_only.py               # HTML parsing only
│       ├── import_jobs_to_db.py             # Job import operations
│       ├── get_latest_job_without_cover_letter.py # Job selection
│       ├── chat_dashboard_generator.py      # Chat dashboard creation
│       ├── n8n_database_cleanup.py          # N8N specific cleanup
│       ├── n8n_database_saver.py            # N8N database operations
│       └── upwork_data.db                   # SQLite database
│
├── 🧠 AI & Machine Learning
│   ├── 📁 ai/                               # AI models and training
│   │   ├── 📁 chat_bot_trainer/             # GPT-2 chat training
│   │   ├── 📁 cover_letter_trainer/         # GPT-2 cover letter training
│   │   ├── 📁 phase_detector_trainer/       # BERT phase detection training
│   │   ├── 📁 local_ai/                     # Local AI implementations
│   │   ├── 📁 openai/                       # OpenAI integration
│   │   ├── 📁 training/                     # General training utilities
│   │   ├── 📁 training_data/                # Training datasets
│   │   ├── convert_training_data.py         # Data conversion utilities
│   │   ├── test_trained_model.py            # Model testing script
│   │   └── training_data.txt                # Text training data
│   └── 📁 trained_models/                   # Trained ML models (~440 MB)
│
├── 🕸️ Web Scraping
│   └── 📁 js_scrapers/                      # JavaScript browser automation
│       ├── browser_connect_chat.js          # Chat browser connector
│       ├── browser_connect_puppeteer.js     # Puppeteer scraper
│       ├── smart_browser_connect.js         # Smart browser connection
│       ├── universal_browser_connect.js     # Universal browser connector
│       ├── package.json                     # JS scraper dependencies
│       └── node_modules/                    # JS scraper packages
│
├── 💾 Data & Storage
│   ├── 📁 data/                             # Main data storage
│   ├── 📁 dashboard_generate/               # Dashboard generation scripts
│   ├── 📄 chat_data.db                     # Chat SQLite database
│   ├── 📄 temp_ai_suggestions.json         # Temporary AI data
│   ├── 📄 temp_selected_job.json           # Temporary job selection
│   └── 📁 cookies/                          # Browser session data
│
├── 🌐 Browser Automation
│   ├── 📁 chrome_profile/                   # Chrome profile for job scraping
│   └── 📁 chrome_profile_chat/              # Chrome profile for chat monitoring
│
├── 📚 Documentation
│   ├── 📄 README-job-scraper.md            # Job scraper workflow guide
│   ├── 📄 README-chat-ai.md                # Chat AI workflow guide
│   ├── 📄 README-cover-letter.md           # Cover letter workflow guide
│   ├── 📄 README-database-cleanup.md       # Database cleanup guide
│   ├── 📄 README-ai-training.md            # AI training guide
│   ├── 📄 PATH_INSTALLATION_GUIDE.md       # Path configuration guide
│   └── 📁 docs/                             # Additional documentation
│
└── 📦 Dependencies
    ├── 📁 venv/                             # Python virtual environment (~1.2 GB)
    ├── 📁 node_modules/                     # Node.js packages (~250 MB)
    ├── 📁 __pycache__/                      # Python cache files
    ├── 📄 package.json                      # Node.js dependencies
    ├── 📄 package-lock.json                 # Node.js dependency lock
    └── 📁 .git/                             # Git repository data
```

**Total Size:** ~3-4 GB (including all dependencies and models)

---

## ⚖️ Legal Disclaimer

**IMPORTANT: Read before using this software**

### 🎯 Development Context
This project was developed as **contracted work** for a specific client under a work-for-hire agreement. The code is published for **portfolio and educational purposes only**.

### 🚫 Terms of Use
By accessing or using this code, you agree to the following terms:

1. **No Liability**: The developer(s) of this software are **NOT responsible** for:
   - How this software is used by third parties
   - Any violations of terms of service of third-party platforms
   - Data loss, account suspension, legal issues, or any damages arising from use
   - Compliance with applicable laws and regulations in your jurisdiction

2. **Use at Your Own Risk**: This software is provided "AS IS" without warranty of any kind. Users assume **full responsibility** for:
   - Compliance with platform Terms of Service
   - Compliance with automation/scraping policies of any platforms used
   - Any consequences resulting from use of this software
   - Proper configuration and security of their systems

3. **No Endorsement**: This project does **NOT** constitute:
   - Encouragement to violate any terms of service
   - Legal advice or compliance guidance
   - A recommendation to use automation on any platform

4. **Educational Purpose**: This code is shared for:
   - Portfolio demonstration of technical skills
   - Educational reference for ML/automation techniques
   - Code review and learning purposes

### ⚠️ Platform Terms Compliance
**WARNING**: Automated interaction with websites may violate their Terms of Service. Before using this software:
- Review platform Terms of Service and API usage policies
- Ensure compliance with all applicable platform policies
- Consider using official APIs instead of web scraping where available
- Obtain proper authorization before automating any platform interactions

### 🔒 Data Privacy & Security
Users are responsible for:
- Securing their own credentials and authentication tokens
- Proper handling of any personal or sensitive data
- Compliance with GDPR, CCPA, and other privacy regulations
- Not committing sensitive data (cookies, tokens, profiles) to version control

### 📞 Contact
For questions about this disclaimer or the project's development context, contact the repository owner through GitHub Issues.

---

## 📄 License

MIT License - see LICENSE file for details.

**Note**: The MIT License applies to the code itself. It does NOT grant permission to violate any third-party terms of service or applicable laws.


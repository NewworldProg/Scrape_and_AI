# 📦 Installation Guide - Scrape & AI Automation System

## ✅ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 5 GB free | 10 GB free |
| **Python** | 3.8+ | 3.10+ |
| **Node.js** | 16+ | 18+ |
| **Chrome** | Required | Latest version |

---

## 🚀 Quick Installation

### **1. Clone Repository**

```powershell
git clone https://github.com/NewworldProg/WorkFlow.git
cd WorkFlow
```

---

### **2. Run Automated Installer**

The `install_n8n.ps1` script handles everything automatically:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_n8n.ps1
```

This installs:
- ✅ Node.js dependencies (Puppeteer, Selenium, etc.)
- ✅ N8N workflow engine (v1.46.0)
- ✅ Python virtual environment
- ✅ Python packages from requirements.txt
- ✅ Helper scripts for activation and running
- ✅ N8N workflows with correct paths

---

### **3. Advanced Installation Options**

#### **Workflows Only (skip Python setup):**
```powershell
powershell -ExecutionPolicy Bypass -File .\install_n8n.ps1 -WorkflowsOnly
```

#### **Force Reinstall (delete and recreate everything):**
```powershell
powershell -ExecutionPolicy Bypass -File .\install_n8n.ps1 -Force
```

#### **Dry Run (preview without making changes):**
```powershell
powershell -ExecutionPolicy Bypass -File .\install_n8n.ps1 -DryRun
```

#### **Custom Installation Path:**
```powershell
powershell -ExecutionPolicy Bypass -File .\install_n8n.ps1 -InstallPath "C:\MyPath"
```

---

## 📂 What Gets Created

After installation, you'll have:

```
WorkFlow/
├── venv/                          # Python virtual environment
├── node_modules/                  # Node.js packages
├── .n8n/                          # N8N data directory
├── n8n/                           # Generated workflows
├── activate_env.ps1               # Python env activation
├── start_n8n.ps1                  # N8N launcher
├── run_with_venv.ps1              # Run scripts with venv
└── [all other project files]
```

---

## 🚀 Next Steps After Installation

### **1. Start N8N**
```powershell
.\start_n8n.ps1
```
Access at: `http://localhost:5678`

### **2. Import Workflows in N8N**
1. Open http://localhost:5678
2. Go to **Workflows** → **Import from File**
3. Import JSON files from the `n8n/` folder

---

## 🔧 Troubleshooting

### **Issue: "Chrome not found"**
**Solution:** Install Chrome from https://www.google.com/chrome/
The installer will warn you if Chrome is missing.

### **Issue: "Python not found"**
**Solution:** Install Python 3.8+ from https://www.python.org/
Make sure to check "Add Python to PATH" during installation.

### **Issue: "Node.js not found"**
**Solution:** Install Node.js 16+ from https://nodejs.org/

### **Issue: Script execution blocked**
**Solution:** Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
```

### **Issue: "Port already in use"**
**Solution:** Kill existing processes:
```powershell
Get-Process node | Stop-Process -Force
Get-Process n8n | Stop-Process -Force
```

---

## 📚 Additional Resources

- **Main README:** [README.md](README.md)
- **N8N Documentation:** [n8n.io](https://n8n.io)
- **Python Setup:** [README-ai-training.md](README-ai-training.md)
- **Chat AI:** [README-chat-ai.md](README-chat-ai.md)
- **Job Scraper:** [README-job-scraper.md](README-job-scraper.md)

---

## ✅ Installation Complete!

You now have a fully configured Scrape & AI Automation System ready to use!

**🎉 All scripts are portable and work from any directory.**

---

**Version:** 3.0  
**Last Updated:** 2026-02-17  
**Tested On:** Windows 10/11, Python 3.8-3.11, Node.js 16-18

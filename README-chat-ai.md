# 🤖 Chat AI Assistant Workflow

**File**: `n8n_chat_ai_workflow.json`  
**Purpose**: Intelligent chat response generation with BERT + GPT-2  
**Trigger**: can be triggered manualy, scheduled (monitor mode)     

---

## 🎯 How It Works

This workflow monitors chat conversations and generates intelligent responses using a combination of BERT for phase detection and GPT-2 for response generation.

### 🔄 Workflow Steps

```
Start Chat Session
  ↓
Check Chrome Chat Status (Port 9223)
  ↓
IF Chrome Ready?
  ├─ YES → Wait for Chat Navigation (45s)
  └─ NO  → Start Chrome Chat → Wait 6s → Check Again
  ↓
Run Chat Scraper (Puppeteer)
  ↓
Parse Chat Messages to Database
  ↓
🧠 STEP 1: BERT Phase Detection (Standalone)
  └─ Detect Conversation Phase + Confidence Score
      └─ Updates database with phase information
  ↓
🤖 STEP 2: Response Generation (Database-driven)
  └─ Generate Multiple Response Options
      ├─ Template Mode (3 quick options)
      ├─ Hybrid Mode (AI-enhanced template)  
      ├─ Pure AI Mode (full GPT-2 generation)
      └─ Summary Mode (template + context summary)
  ↓
Generate Interactive Dashboard with Click-to-Copy Options
```

### 📁 Files Used

| File | Purpose |
|------|---------|
| `run_check_chrome_chat.ps1` | Check Chrome chat status (port 9223) |
| `run_start_chrome_chat_simple.ps1` | Start Chrome chat profile |
| `run_chat_scraper.ps1` | Execute chat scraper |
| `run_chat_parser.ps1` | Parse chat HTML to database |
| `run_detect_phase_standalone.ps1` | 🆕 BERT phase detection only |
| `run_generate_response.ps1 -Mode all` | 🆕 Generate all response types |
| `run_generate_and_open_chat_dashboard.ps1` | Create interactive dashboard |

---

## 🧠 AI Architecture (Optimized v4.0)

### **Two-Stage Processing**
1. **Phase Detection**: Standalone BERT analysis → Database storage
2. **Response Generation**: Database-driven → No duplicate ML calls

### **BERT Phase Detection Model**
- **File**: `ai/standalone_phase_detector.py`
- **Model**: BERT-base-uncased (110M parameters)
- **Training**: 53 labeled Upwork conversations
- **Accuracy**: 100% on training set, 75-93% production confidence
- **Location**: `ai/trained_models/phase_classifier_v1/`

### **8 Conversation Phases**
| Phase | Keywords | Next Action |
|-------|----------|-------------|
| `initial_response` | apply, application, interested | Ask Job Details |
| `ask_job_details` | project, task, what, need | Language Confirmation |
| `language_confirmation` | language, english, dutch | Rate Discussion |
| `rate_negotiation` | rate, price, per word, budget | Deadline & Samples |
| `deadline_samples` | deadline, when, sample | Structure Clarification |
| `structure_clarification` | structure, format, seo, keywords | Contract Acceptance |
| `contract_acceptance` | contract, agreement, accept, start | Work Begins |
| `knowledge_check` | test, quiz, prove, demonstrate | 🚨 Human Review Required |

---

## 🎨 Response Generation Modes

### **4 Response Generation Options**

#### **1. Template Mode** (⚡ ~0.1s)
- **File**: Built into `ai/smart_chat_response.py`
- **Output**: 3 pre-written professional responses for current phase
- **Use Case**: Fast, consistent, professional responses

#### **2. Hybrid Mode** (🔄 ~2s)  
- **Process**: Template base + AI personalization
- **Output**: 1 AI-enhanced response with job-specific context
- **Use Case**: Balanced approach with AI creativity

#### **3. Pure AI Mode** (🤖 ~3s)
- **Model**: Custom trained GPT-2 (`ai/trained_models/final_chat_model/`)
- **Output**: 1 fully AI-generated response
- **Use Case**: Creative, unique responses

#### **4. Summary Mode** (📊 ~2s)
- **Process**: Template + AI-generated conversation summary
- **Output**: 1 contextually aware response
- **Use Case**: Template structure with conversation understanding

### **All Modes Combined** (🎯 ~7-8s)
```powershell
# Default n8n workflow execution
.\run_generate_response.ps1 -Mode all

# Generates 6 total options: 3 + 1 + 1 + 1
```

---

## 🗄️ Database Structure

```sql
-- Chat sessions with phase information
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY,
    session_start TEXT,
    phase TEXT,                    -- Current conversation phase
    phase_confidence REAL,         -- BERT confidence score (0-1)
    phase_updated_at TEXT,         -- Last phase detection timestamp
    total_messages INTEGER,
    status TEXT
);

-- Individual chat messages
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    speaker TEXT,
    message TEXT,
    timestamp TEXT,
    message_order INTEGER,
    FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
);
```

---

## 🎯 Interactive Dashboard

### **Dashboard Features**
- **File**: `chat_dashboard.html`
- **Generator**: `scripts/chat_dashboard_generator.py`
- **Updates**: Real-time after each workflow execution

### **Dashboard Sections**
```
┌─────────────────────────────────────────────┐
│ 🎯 Current Phase: Rate Discussion          │
│ 🔬 Confidence: 78.3% (BERT Model)         │
│ ➡️  Next Phase: Deadline & Samples         │
├─────────────────────────────────────────────┤
│ 📝 Template Options (3):                   │
│   [Copy] "Sounds good! What's deadline?"   │
│   [Copy] "Great! When do you need this?"   │
│   [Copy] "Perfect! Deadline and sample?"   │
├─────────────────────────────────────────────┤
│ 🤖 Hybrid AI (1):                          │
│   [Copy] "Thank you! What's the deadline?" │
├─────────────────────────────────────────────┤
│ 💭 Pure AI (1):                            │
│   [Copy] "Could we discuss the timeline?"  │
├─────────────────────────────────────────────┤
│ 📋 Summary AI (1):                         │
│   [Copy] "Based on our discussion..."      │
└─────────────────────────────────────────────┘
```

### **Click-to-Copy Functionality**
- **JavaScript**: Built-in clipboard API
- **Feedback**: Visual confirmation when text copied
- **Mobile Support**: Touch-friendly buttons

---

## ⚙️ Chrome Chat Profile Setup

### **Dedicated Chrome Profile**
- **Port**: 9223 (separate from job scraping)
- **Profile**: `chrome_profile_chat/`
- **Purpose**: Isolated environment for chat monitoring

### **Setup Commands**
```powershell
# Start Chrome chat profile
chrome.exe --remote-debugging-port=9223 --user-data-dir="chrome_profile_chat"

# Test connection
Invoke-WebRequest -Uri "http://localhost:9223/json/version"
```

### **Manual Setup Required**
1. Open Chrome with chat profile
2. Login to chat platform
3. Navigate to active conversation
4. Trigger n8n workflow manually
5. System takes over monitoring

---

## 🛠️ Advanced Configuration

### **Phase Detection Tuning**
```python
# In ai/standalone_phase_detector.py
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for ML prediction
FALLBACK_TO_KEYWORDS = True  # Use keyword detection if ML fails
```

### **Response Generation Parameters**
```python
# In ai/smart_chat_response.py
GPT2_TEMPERATURE = 0.8      # Creativity level (0.0-1.0)
GPT2_MAX_LENGTH = 150       # Maximum response length
GPT2_TOP_P = 0.9           # Nucleus sampling parameter
```

### **Custom Model Training**
```powershell
# Train phase classifier on new data
python ai/train_phase_classifier.py

# Train custom GPT-2 chat model
python ai/train_chat_gpt2.py
```

---

## 🛠️ Troubleshooting

### **Chrome Connection Issues**
```powershell
# Check chat Chrome status
.\run_check_chrome_chat.ps1

# Expected output: {"chrome_ready": true}
```

### **Phase Detection Problems**
```python
# Test phase detection manually
python ai/standalone_phase_detector.py

# Check model exists
Test-Path "ai/trained_models/phase_classifier_v1"
```

### **Low Confidence Scores**
- **Issue**: Phase confidence below 70%
- **Solution**: Add more training data to `ai/phase_training_data.json`
- **Fallback**: System automatically uses keyword detection

### **Repetitive GPT-2 Responses**
```python
# Increase temperature for more creativity
GPT2_TEMPERATURE = 0.9

# Or use template mode for consistent professional responses
.\run_generate_response.ps1 -Mode template
```

### **Database Connection Issues**
```python
# Test database connection
from data.chat_database_manager import ChatDatabase
db = ChatDatabase()
print(f"Database path: {db.db_path}")
print(f"Sessions count: {len(db.get_all_sessions())}")
```

---

## 📊 Performance Metrics

### **Processing Speed**
- **Phase Detection**: ~0.5s (BERT inference)
- **Template Generation**: ~0.1s (instant)
- **Hybrid Generation**: ~2s (template + GPT-2)
- **Pure AI Generation**: ~3s (full GPT-2)
- **Summary Generation**: ~2s (context + template)
- **Total Workflow**: ~10-15s (scrape → detect → generate → dashboard)

### **Accuracy Metrics**
- **Phase Detection**: 75-93% confidence in production
- **Response Relevance**: High (based on phase-appropriate templates)
- **Professional Tone**: Consistent across all modes
- **Context Awareness**: Strong in hybrid and summary modes

### **Resource Usage**
- **Memory**: ~2GB (BERT + GPT-2 models loaded)
- **CPU**: Moderate during inference, low at rest
- **Disk**: ~500MB for models, ~5MB for chat database
- **Network**: Minimal (only for Chrome debug connection)
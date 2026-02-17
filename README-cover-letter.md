# 📝 Cover Letter Generator Workflow

**File**: `n8n_ai_cover_letter_workflow.json`  
**Purpose**: AI-powered personalized cover letter generation  
**Trigger**: can be triggered manualy or scheduled     

---

## 🎯 How It Works

This workflow automatically generates personalized cover letters for new job postings using fine-tuned AI models.

### 🔄 Workflow Steps

```
Start
  ↓
Get Latest Job Without Cover Letter
  ↓
Generate Smart AI Cover Letter
  ↓
Save Cover Letter to Database
  ↓
Update Job Dashboard
```

### 📁 Files Used

| File | Purpose |
|------|---------|
| `run_get_latest_job_without_cover_letter.ps1` | Find job needing cover letter |
| `run_smart_cover_letter.ps1` | Generate AI-powered cover letter |
| `run_import_jobs_to_db.ps1` | Save cover letter to database |
| `run_generate_and_open_dashboard.ps1` | Update job dashboard |

### 🤖 Core Components

#### **AI Cover Letter Generator**
- **File**: `scripts/smart_cover_letter_generator.py`
- **Function**: Uses fine-tuned GPT-2 model to generate personalized cover letters
- **Input**: Job title, description, requirements
- **Output**: Personalized cover letter text

#### **Database Manager**
- **File**: `data/database_manager.py`
- **Function**: Manages cover letter storage and job updates
- **Tables**: `jobs`, `cover_letters`

#### **Fine-tuned Model**
- **Location**: `trained_models/advanced_cover_letter_model/final/`
- **Type**: GPT-2 fine-tuned on successful cover letters
- **Size**: ~355M parameters

---

## 🧠 AI Model Details

### Model Architecture
- **Base**: GPT-2 Medium (355M parameters)
- **Fine-tuning**: Trained on successful cover letter examples
- **Special Tokens**: Job-specific markers for better context understanding
- **Output Length**: 150-300 words (optimized for cover letters)


## ⚙️ Configuration Options

### AI Provider Selection
The system supports multiple AI providers:

```python
# In smart_cover_letter_generator.py
PREFERRED_PROVIDER = "local_gpt2"  # or "openai"

# For OpenAI (optional)
OPENAI_API_KEY = "your-api-key-here"
```

### Model Paths
```python
# Local fine-tuned model
LOCAL_MODEL_PATH = "trained_models/advanced_cover_letter_model/final/"

# Fallback to base model if fine-tuned not available
FALLBACK_MODEL = "gpt2"
```

---

## 🗄️ Database Structure

```sql
-- Cover letters table
CREATE TABLE cover_letters (
    id INTEGER PRIMARY KEY,
    job_id INTEGER,
    ai_provider TEXT,
    cover_letter_text TEXT,
    generated_on TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs (id)
);

-- Jobs table (updated with cover letter flag)
UPDATE jobs SET has_cover_letter = 1 WHERE id = ?;
```

---

## 🎯 Cover Letter Quality Features

### Personalization Elements
- **Job-specific keywords**: Extracted from job description
- **Skills matching**: Highlights relevant experience
- **Company research**: Generic but professional tone
- **Call to action**: Encouraging next steps

### Template Structure
```
1. Professional greeting
2. Opening statement with job title reference
3. Skills and experience highlights (2-3 sentences)
4. Specific interest in the role/company
5. Professional closing with call to action
---

## 🛠️ Troubleshooting

### Model Not Found
```python
# Check if fine-tuned model exists
import os
model_path = "trained_models/advanced_cover_letter_model/final/"
print(f"Model exists: {os.path.exists(model_path)}")

# Train new model if needed
python ai/train_cover_letter_model.py
```

### Generic Responses
- **Issue**: Cover letters too generic or repetitive
- **Solution**: Retrain model with more diverse examples
- **Alternative**: Adjust temperature parameter (increase for more creativity)

### Database Connection Issues
```powershell
# Check database permissions
Test-Path "upwork_data.db"

# Verify jobs without cover letters exist
python -c "from data.database_manager import JobDatabase; db = JobDatabase(); print(db.get_latest_job_without_cover_letter())"
```

### OpenAI API Issues (if using OpenAI)
```python
# Test API connection
import openai
openai.api_key = "your-key"
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt="Write a cover letter for a developer position",
    max_tokens=100
)
```

---

## 📊 Performance Metrics

### Generation Speed
- **Local GPT-2**: ~3-5 seconds per cover letter
- **OpenAI API**: ~2-3 seconds per cover letter (with internet)
- **Batch Processing**: Can handle 10+ jobs in sequence

### Quality Indicators
- **Uniqueness**: Each cover letter uses job-specific keywords
- **Length**: Optimized 150-300 words for readability
- **Professional Tone**: Maintained across all generations
- **Relevance**: Skills and experience matched to job requirements

### Database Impact
- **Storage**: ~1-2KB per cover letter
- **Query Performance**: Indexed by job_id for fast retrieval
- **Backup**: Cover letters preserved for future reference
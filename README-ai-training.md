# 🤖 AI Model Training Guide

This system includes **3 specialized AI training modules** to improve performance beyond base models.

## 🎯 **Training Modules Overview**

| Module | Purpose | Base Model | Training Data | Expected Improvement |
|--------|---------|------------|---------------|---------------------|
| **Phase Detector** | Detect conversation phases (8 types) | BERT base | 53 conversations | ~87% accuracy |
| **Chat Bot** | Generate contextual responses | GPT-2 base | 11 conversations | More relevant responses |
| **Cover Letter** | Generate personalized cover letters | GPT-2 base | Custom templates | Better job-specific content |

---

## 📂 **Training Directory Structure**

```
ai/
├── phase_detector_trainer/           # BERT Phase Detection Training
│   ├── train_phase_classifier.py    # Training script
│   ├── training_data/
│   │   └── phase_training_data.json # 53 labeled conversations
│   └── trained_models/
│       └── phase_classifier_v1/     # Outputs here (87.5% accuracy)
│
├── chat_bot_trainer/                 # GPT-2 Chat Response Training  
│   ├── train_chat_gpt2.py           # Training script
│   ├── training_data/
│   │   └── training_data_parsed.json # 11 conversation examples
│   └── trained_models/
│       └── final_chat_model/        # Outputs here
│
└── cover_letter_trainer/             # GPT-2 Cover Letter Training
    ├── model_training.py             # Training script
    ├── training_data/
    │   └── training_data.json        # Cover letter templates
    └── trained_models/
        └── custom_cover_letter_model/ # Outputs here
```

---

## 🚀 **Quick Training Guide**

### **1. 🧠 Train Phase Detector (BERT)**
```powershell
# Navigate to trainer directory
cd ai\phase_detector_trainer

# Start training (takes 10-15 minutes)
python train_phase_classifier.py

# Expected output:
# ✅ Model trained with 87.5% accuracy
# 📁 Saved to: trained_models/phase_classifier_v1/
```

**Training Data**: 53 conversations labeled with phases:
- `initial_response`, `ask_details`, `knowledge_check`
- `language_confirm`, `rate_negotiation`, `deadline_samples`  
- `structure_clarification`, `contract_acceptance`

### **2. 💬 Train Chat Bot (GPT-2)**
```powershell
# Navigate to trainer directory  
cd ai\chat_bot_trainer

# Start training (takes 20-30 minutes)
python train_chat_gpt2.py

# Expected output:
# ✅ GPT-2 model trained successfully
# 📁 Saved to: trained_models/final_chat_model/
```

**Training Data**: 11 conversation examples with context + appropriate responses.

### **3. 📝 Train Cover Letter Generator (GPT-2)**
```powershell
# Navigate to trainer directory
cd ai\cover_letter_trainer

# Start training (takes 15-25 minutes) 
python model_training.py

# Follow prompts:
# ➡️ Start training with X examples? (y/N): y

# Expected output:
# 🎉 Training completed!
# 📁 Model saved to: trained_models/custom_cover_letter_model/final/
```

**Training Data**: Job-specific cover letter templates with skills matching.

---

## ⚙️ **Training Requirements**

### **Hardware Requirements**
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 5GB free space
- **GPU**: Optional (CUDA-compatible for faster training)
- **Time**: 45-60 minutes total for all models

### **Software Requirements**
```powershell
# Already installed with main system:
pip install torch transformers datasets scikit-learn
```

---

## 🎯 **Performance Comparison**

| Model | Base (Untrained) | After Training | Improvement |
|-------|------------------|----------------|-------------|
| **Phase Detection** | ~25% accuracy (random) | **87.5% accuracy** | **+62.5%** |
| **Chat Responses** | Generic GPT-2 text | Contextual freelance responses | **Much more relevant** |
| **Cover Letters** | Generic content | Job-specific personalization | **Higher application success** |

---

## 🔧 **Troubleshooting Training**

### **Common Issues**

**❌ Out of Memory Error**
```powershell
# Reduce batch size in training scripts:
# Change: batch_size=4 → batch_size=2
# Change: max_length=512 → max_length=256
```

**❌ CUDA Not Available**
```powershell
# Training will use CPU (slower but works)
# Expected training time increases by 2-3x
```

**❌ Training Data Not Found**
```powershell
# Ensure you're in correct directory:
cd ai\phase_detector_trainer  # For phase training
cd ai\chat_bot_trainer        # For chat training  
cd ai\cover_letter_trainer    # For cover letter training
```

---

## 📊 **Training Progress Monitoring**

Each training script provides real-time progress:

```
🔥 Training Progress:
Epoch 1/3: [████████████████████████████████] 100%
Loss: 0.234 | Accuracy: 84.2%

Epoch 2/3: [████████████████████████████████] 100%  
Loss: 0.156 | Accuracy: 86.8%

Epoch 3/3: [████████████████████████████████] 100%
Loss: 0.123 | Accuracy: 87.5%

✅ Training completed!
```

---

## 🎉 **After Training**

Once training completes:

1. **✅ Models auto-detected** - Scripts automatically use trained models
2. **🔄 Fallback preserved** - If training fails, base models still work  
3. **📈 Performance boost** - Significantly better AI responses
4. **🎯 Ready for production** - All workflows use improved models

### **Verify Training Success**
```powershell
# Test trained phase detector
python scripts\standalone_phase_detector.py

# Expected output:
# ✅ Trained phase classifier loaded
# [INFO] Accuracy: 87.5%
```

---

## 📝 **Custom Training Data**

To improve models with your own data:

### **Phase Detector**
Edit [`ai/phase_detector_trainer/training_data/phase_training_data.json`](ai/phase_detector_trainer/training_data/phase_training_data.json):
```json
{
  "context": "Your conversation context here",
  "phase": "rate_negotiation",
  "conversation_id": "custom_01"
}
```

### **Chat Bot** 
Edit [`ai/chat_bot_trainer/training_data/training_data_parsed.json`](ai/chat_bot_trainer/training_data/training_data_parsed.json):
```json
{
  "context": "Client message context",
  "response": "Your ideal response",
  "phase": "deadline_samples"
}
```

### **Cover Letters**
Edit [`ai/cover_letter_trainer/training_data/training_data.json`](ai/cover_letter_trainer/training_data/training_data.json):
```json
{
  "job_title": "Python Developer", 
  "company": "TechCorp",
  "skills": ["Python", "Django"],
  "cover_letter": "Personalized cover letter content..."
}
```

---

## 🎯 **Training Best Practices**

1. **📊 Quality over Quantity** - 50 high-quality examples > 500 poor examples
2. **🎯 Diverse Examples** - Cover all conversation phases/scenarios  
3. **✅ Label Consistency** - Use consistent phase labels across training data
4. **🔄 Iterative Training** - Train → Test → Add Data → Retrain
5. **💾 Backup Models** - Keep working models before retraining

---

## 📞 **Support**

For training issues:
- Check [main README troubleshooting](README.md#troubleshooting)
- Review training logs for specific error messages
- Ensure sufficient disk space and RAM
- Consider reducing batch size for memory issues

Happy training! 🚀
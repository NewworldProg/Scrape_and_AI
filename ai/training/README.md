# AI Model Training for Cover Letters

This module provides functionality for training custom GPT-2 models specifically for generating professional cover letters.

## 🚀 Training Workflow

### Current Data Sources

1. **Primary Source**: `ai/training_data.txt` (Noel Angeles iGaming cover letter)
2. **Converted Data**: `ai/training_data.json` (3 training examples)
3. **Conversion Script**: `ai/convert_training_data.py`

### Step-by-Step Process

```bash
# 1. Convert text data to JSON format (if needed)
cd ai
python convert_training_data.py

# 2. Choose your training approach:

# Option A: Basic Training (hardcoded examples)
cd training/examples
python train_basic.py

# Option B: Advanced Training (uses training_data.json)
cd training/examples  
python train_advanced.py

# 3. Use trained model
# Update ai/local_ai/config.json with your model path
```

## 📊 What Gets Trained

- **Base Model**: GPT-2 (CPU-optimized)
- **Training Data**: 3 professional cover letter examples
- **Output**: Custom model fine-tuned for cover letter generation
- **Format**: Structured prompt format with job title, company, skills

## 🎯 Current Training Examples

1. **iGaming Content Writer** (from Noel Angeles)
   - Real professional cover letter
   - 10+ years experience
   - Bilingual (English/Dutch)
   - SEO expertise

2. **Content Writer** (generated example)
   - Digital marketing focus
   - SEO and social media skills

3. **Technical Writer** (generated example)
   - Software documentation
   - API and user guide expertise

## 🔧 Training Configuration

### CPU-Only Training
- **Device**: Forced CPU for maximum compatibility
- **Batch Size**: 1-2 (optimized for CPU)
- **Training Time**: 5-30 minutes per epoch
- **Memory**: Low memory usage (works on any system)

### Training Parameters
- `base_model`: "gpt2" (default), "gpt2-medium", "gpt2-large"
- `num_epochs`: 3-5 (more epochs = better results)
- `learning_rate`: 5e-5 (recommended)
- `batch_size`: 1-2 (CPU optimized)
- `save_steps`: 500 (checkpoint frequency)

## 📁 File Structure

```
ai/
├── training_data.txt          # Source: Noel Angeles cover letter
├── training_data.json         # Converted: 3 training examples
├── convert_training_data.py   # Conversion script
├── model_training.py          # Main training class
└── training/
    ├── README.md              # This file
    └── examples/
        ├── train_basic.py     # Basic training (hardcoded data)
        ├── train_advanced.py  # Advanced training (uses JSON)
        └── evaluate_model.py  # Model evaluation
```

## 🎯 Installation

### 1. Install Dependencies (if not already installed)
```bash
pip install transformers datasets torch
```

### 2. Run Training
```bash
# Navigate to examples directory
cd ai/training/examples

# Option 1: Basic training (2 hardcoded examples)
python train_basic.py

# Option 2: Advanced training (uses training_data.json with 3 examples)
python train_advanced.py
```

### 3. Use Trained Model
Update `ai/local_ai/config.json`:
```json
{
  "model_name": "./trained_models/your_model_name/final",
  "max_tokens": 500,
  "temperature": 0.7
}
```

## Training Parameters

- `base_model`: Base GPT-2 model ("gpt2", "gpt2-medium", "gpt2-large")
- `num_epochs`: Number of training epochs (3-10 recommended)
- `learning_rate`: Learning rate (5e-5 recommended)
- `batch_size`: Batch size (1-4 recommended for CPU training)
- `save_steps`: Save model every N steps

## 🔄 Data Flow

```
training_data.txt (Noel's cover letter)
         ↓
convert_training_data.py (conversion script)
         ↓
training_data.json (3 structured examples)
         ↓
train_advanced.py (loads JSON data)
         ↓
CoverLetterTrainer (trains GPT-2 model)
         ↓
./trained_models/model_name/final/ (saved model)
         ↓
Update local_ai/config.json (use trained model)
         ↓
LocalAIProvider (generates cover letters with trained model)
```

## 🚀 Recommended Workflow

1. **Start Here**: `python train_advanced.py` (uses real cover letter data)
2. **Evaluate**: `python evaluate_model.py` (check improvements)
3. **Deploy**: Update `ai/local_ai/config.json` with model path
4. **Test**: Generate cover letters through GUI or directly
5. **Iterate**: Add more training data and retrain for better results

## Model Export

Trained models are automatically saved in the `output_dir` with:
- Model weights and tokenizer
- Training metadata (JSON file)
- Logs and checkpoints

## 📖 Training Examples Explained

### `train_basic.py`
- **Data Source**: Hardcoded training examples (2 examples)
- **Use Case**: Quick testing and demonstration
- **Training Time**: ~5-10 minutes
- **Examples**: Python Developer, Data Scientist

### `train_advanced.py` 
- **Data Source**: `ai/training_data.json` (3 examples)
- **Use Case**: Production training with real data
- **Training Time**: ~10-20 minutes  
- **Features**: Data splitting, validation, evaluation
- **Includes**: Noel Angeles real cover letter + generated examples

### `evaluate_model.py`
- **Purpose**: Compare base model vs trained model
- **Output**: Performance comparison and metrics
- **Usage**: Run after training to validate improvements

## Integration with Local AI Provider

After training a model, you can use it with the existing `LocalAIProvider`:

### 1. Update Local AI Config

Edit `ai/local_ai/config.json`:

```json
{
  "model_name": "./trained_models/advanced_cover_letter_model/final",
  "max_tokens": 500,
  "temperature": 0.7,
  "cache_dir": null
}
```

### 2. Use in Your Application

```python
from ai.local_ai import LocalAIProvider

# Will automatically load your trained model
provider = LocalAIProvider()

# Generate cover letters with your custom model
job_data = {
    "title": "Content Writer", 
    "company": "Tech Corp",
    "skills": ["Writing", "SEO"]
}
cover_letter = provider.generate_cover_letter(job_data)
```

The local AI provider will automatically detect and load your trained model from the specified path.

---

**Ready to train your custom cover letter model? Start with `python train_advanced.py`!** 🚀

## Troubleshooting

## ⚠️ Troubleshooting

### Memory Issues
- Reduce batch size to 1
- Close other applications
- Use base "gpt2" instead of "gpt2-medium"

### Slow Training
- Normal on CPU (be patient!)
- Expected: 5-30 minutes per epoch
- Use fewer epochs for testing

### Model Not Loading
- Check model path in `local_ai/config.json`
- Ensure training completed successfully
- Verify model files exist in output directory

### Poor Cover Letter Quality
- Train for more epochs (5-10)
- Add more diverse training examples
- Use larger base model (gpt2-medium)

## 📋 Requirements
- Python 3.8+
- transformers
- datasets  
- torch
- Minimum 4GB RAM
- 2-5GB free disk space for models
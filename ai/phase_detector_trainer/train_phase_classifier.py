"""
Phase Classification Model Training
Trains a model to detect conversation phases with labels
"""
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertModel
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import os
from datetime import datetime

# Set UTF-8 encoding
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Phase label that will be used for classification
PHASE_LABELS = [
    'initial_response',
    'ask_details', 
    'knowledge_check',
    'language_confirm',
    'rate_negotiation',
    'deadline_samples',
    'structure_clarification',
    'contract_acceptance'
]
# Mapping phase labels to IDs and vice versa
PHASE_TO_ID = {phase: idx for idx, phase in enumerate(PHASE_LABELS)}
ID_TO_PHASE = {idx: phase for phase, idx in PHASE_TO_ID.items()}


class PhaseDataset(Dataset):
    """Dataset for conversation phase classification"""
    # initialize dataset with contexts, phases, tokenizer, and max length
    def __init__(self, contexts, phases, tokenizer, max_length=256):
        self.contexts = contexts # this will be input for text for training model
        self.phases = phases # this will be offered output for model answers
        self.tokenizer = tokenizer
        self.max_length = max_length
    # return length of dataset
    def __len__(self):
        return len(self.contexts)
    # seting up looper for model training
    # 1. get one context argument from contexts list
    # 2. get corresponding phase label
    # 3. tokenize context using tokenizer
    # 4. loop return dictionary of input ids, attention mask, and label
    def __getitem__(self, idx):
        context = str(self.contexts[idx]) # get one context argument
        phase = self.phases[idx] # get phase corresponding to argument
        # tokenize context
        encoding = self.tokenizer.encode_plus(
            context,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        # return dictionary of input ids, attention mask, and label
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(PHASE_TO_ID[phase], dtype=torch.long)
        }


class PhaseClassifier(nn.Module):
    """BERT-based phase classifier"""
    # setup phase model untrained, BERT as base of
    # 1. model
    # 2. dropout layer
    # 3. linear classifier layer it classifies embeings of BERT into n_classes
            # which are in this case 8 phase labels
    def __init__(self, n_classes=8, dropout=0.3):
        super(PhaseClassifier, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, n_classes)
    # forward it to model and return output
    # 1. get input ids from __getitem__
    # 2. get attention mask from __getitem__
    # 3. pass them to BERT model
    # 4. get pooled output from BERT outputs
    # 5. apply dropout
    # 6. pass through classifier layer and return output, output is logits for each class
            # logits are raw scores of embeddings and and classifier will convert them to probabilities
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        pooled_output = outputs.pooler_output
        output = self.dropout(pooled_output)
        return self.classifier(output)

# load training data from JSON file
# 1. open file path to train data
# 2. load it as json
# 3. extract contexts and phases into separate lists
# 4. log it how many training examples are loaded
# 5. log phase distribution
# 6. return contexts and phases lists
def load_training_data(file_path):
    """Load phase training data from JSON"""
    # open file path to train data
    print(f"[INFO] Loading training data from {file_path}...")
    # load it as json
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # extract from data and make lists
    # context
    contexts = [item['context'] for item in data]
    # phase
    phases = [item['phase'] for item in data]
    # log it how many training examples are loaded
    print(f"[OK] Loaded {len(contexts)} training examples")
    print(f"[INFO] Phase distribution:")
    # loop through phase labels and count how many of them are in phases list
    # to check if model will be trained on every phase and on every phase equally
    for phase in PHASE_LABELS:
        count = phases.count(phase)
        print(f"  - {phase}: {count} examples")
    # return contexts and phases lists
    return contexts, phases

# train the model
# input model, train_loader, val_loader, epochs, learning_rate, device
# 1. loop through epochs
# 2. load model to device
# 3. optimizer AdamW - how do I fix my mistakes
# 4. criterion CrossEntropyLoss - how many mistakes have I made
# 5. training phase
# 6. validation phase
# 7. save best model based on validation accuracy
def train_model(model, train_loader, val_loader, epochs=10, learning_rate=2e-5, device='cpu'):
    """Train the phase classification model"""
    # log every loop
    print(f"\n[INFO] Training model for {epochs} epochs...")
    print(f"[INFO] Device: {device}")

    # move model to device
    model = model.to(device)
    # how do I fix my mistakes
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    # how many mistakes have I made
    criterion = nn.CrossEntropyLoss()
    
    best_val_acc = 0.0

    # loop through epochs
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        # loop through batches in train_loader
        # train_loader is DataLoader object that holds PhaseDataset
        for batch in train_loader:
            # in each batch get
            # input ids
            input_ids = batch['input_ids'].to(device)
            # attention mask
            attention_mask = batch['attention_mask'].to(device)
            # labels
            labels = batch['label'].to(device)
            # how do I fix my mistakes is reset after each fix, 
            # gradient is magnitude of mistake and direction of fix
            optimizer.zero_grad()
            # pass input ids and attention mask to model and put output to var
            outputs = model(input_ids, attention_mask)
            # calculate mistakes and put to var
            loss = criterion(outputs, labels)
            # step backwards to see where mistakes were made
            loss.backward()
            # update model parameters to fix mistakes
            optimizer.step()
            # accumulate loss and correct predictions
            train_loss += loss.item()
            # statistics for accuracy
            _, predicted = torch.max(outputs, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        # calculate training accuracy and average loss
        train_acc = 100 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        
        # now run model for validation
        with torch.no_grad():
            # batch is cluster of data from val_loader
            for batch in val_loader:
                # cluster of data
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['label'].to(device)
                # staats for accuracy
                outputs = model(input_ids, attention_mask)
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        # calculate validation accuracy
        val_acc = 100 * val_correct / val_total
        
        print(f"Epoch {epoch+1}/{epochs}:")
        print(f"  Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            print(f"  [BEST] New best validation accuracy: {val_acc:.2f}%")
    # after all epochs return trained model
    return model

# evaluate the model
# init model, test_loader, device
# 1. set model to eval mode
# 2. loop through test_loader batches dont need gradients, not training
# 3. compare true phases and predicted phases
# 4. print classification report, confusion matrix, overall accuracy
def evaluate_model(model, test_loader, device='cpu'):
    """Evaluate model and show classification report"""
    print("\n[INFO] Evaluating model...")
    # set model to eval mode
    model.eval()
    all_preds = []
    all_labels = []
    # loop through test_loader batches dont need gradients, not training
    with torch.no_grad():
        for batch in test_loader:
            # batch cluster of data
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            # stats for accuracy
            outputs = model(input_ids, attention_mask)
            _, predicted = torch.max(outputs, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Convert to phase names
    pred_phases = [ID_TO_PHASE[p] for p in all_preds]
    true_phases = [ID_TO_PHASE[l] for l in all_labels]
    # Convert predictions and true labels to phase names
    print("\n=== Classification Report ===")
    # compare true phases and predicted phases
    # target names are phase labels, zero_division=0 to avoid errors
    print(classification_report(true_phases, pred_phases, target_names=PHASE_LABELS, zero_division=0))
    # confusion matrix where are most mistakes made
    print("\n=== Confusion Matrix ===")
    cm = confusion_matrix(true_phases, pred_phases, labels=PHASE_LABELS)
    print("Labels:", PHASE_LABELS)
    print(cm)
    # calculate overall accuracy
    accuracy = 100 * sum([1 for p, t in zip(all_preds, all_labels) if p == t]) / len(all_labels)
    print(f"\n[RESULT] Overall Accuracy: {accuracy:.2f}%")
    
    return accuracy

# save the trained model and tokenizer
# input model, tokenizer, save_dir, metadata
# 1. create save directory if not exists
def save_model(model, tokenizer, save_dir, metadata=None):
    """Save trained model and tokenizer"""
    # log save_dir that is chosen
    print(f"\n[INFO] Saving model to {save_dir}...")
    # create save directory if not exists
    os.makedirs(save_dir, exist_ok=True)
    
    # Save model inside save_dir by the name phase_classifier.pth
    torch.save(model.state_dict(), os.path.join(save_dir, 'phase_classifier.pth'))
    
    # Save tokenizer
    tokenizer.save_pretrained(save_dir)
    
    # Save metadata
    if metadata is None:
        metadata = {}
    
    metadata.update({
        'phase_labels': PHASE_LABELS,
        'phase_to_id': PHASE_TO_ID,
        'id_to_phase': ID_TO_PHASE,
        'model_type': 'bert-base-uncased',
        'n_classes': len(PHASE_LABELS),
        'trained_at': datetime.now().isoformat()
    })
    # save metadata as JSON file
    with open(os.path.join(save_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    # log it
    print(f"[OK] Model saved successfully!")

# main to orchestrate training process
def main():
    """Main training function"""
    print("=" * 60)
    print("PHASE CLASSIFICATION MODEL TRAINING")
    print("=" * 60)
    
    # Configuration
    # 1. define data file path
    DATA_FILE = os.path.join(os.path.dirname(__file__), "training_data", "phase_training_data.json")
    # 2. define save directory
    SAVE_DIR = os.path.join(os.path.dirname(__file__), 'trained_models', 'phase_classifier_v1')
    # 3. define batch size, how many data points will be processed together
    BATCH_SIZE = 4
    # 4. define number of epochs
    EPOCHS = 20
    # 5. define learning rate
    LEARNING_RATE = 2e-5
    # 6. define test size
    TEST_SIZE = 0.15  # Smaller test set for small dataset
    
    # hardware device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[INFO] Using device: {device}")
    
    # Load data
    contexts, phases = load_training_data(DATA_FILE)
    
    # Split data for training and testing
    train_contexts, test_contexts, train_phases, test_phases = train_test_split(
        contexts, phases, test_size=TEST_SIZE, random_state=42, stratify=phases
    )
    
    print(f"\n[INFO] Data split:")
    print(f"  Train: {len(train_contexts)} examples")
    print(f"  Test: {len(test_contexts)} examples")
    
    # Initialize tokenizer
    print(f"\n[INFO] Loading BERT tokenizer...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    # Create datasets
    # train dataset
    train_dataset = PhaseDataset(train_contexts, train_phases, tokenizer)
    # test dataset
    test_dataset = PhaseDataset(test_contexts, test_phases, tokenizer)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    # Initialize model
    print(f"\n[INFO] Initializing model...")
    model = PhaseClassifier(n_classes=len(PHASE_LABELS))
    
    # Train model
    model = train_model(
        model, train_loader, test_loader,
        epochs=EPOCHS, learning_rate=LEARNING_RATE, device=device
    )
    
    # Evaluate model
    accuracy = evaluate_model(model, test_loader, device=device)
    
    # Save model
    metadata = {
        'training_samples': len(train_contexts),
        'test_samples': len(test_contexts),
        'accuracy': accuracy,
        'epochs': EPOCHS,
        'batch_size': BATCH_SIZE,
        'learning_rate': LEARNING_RATE
    }
    save_model(model, tokenizer, SAVE_DIR, metadata)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Model saved to: {SAVE_DIR}")
    print(f"Final accuracy: {accuracy:.2f}%")


if __name__ == "__main__":
    main()

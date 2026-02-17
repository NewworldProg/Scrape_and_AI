"""
GPT-2 Chat Model Training Script - Optimized Version
Trains GPT-2 model on processed JSON chat data
"""
import os
import json
import torch
from datetime import datetime
from transformers import (
    GPT2LMHeadModel, 
    GPT2Tokenizer, 
    DataCollatorForLanguageModeling,
    Trainer, 
    TrainingArguments
)
from torch.utils.data import Dataset
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configure ML tracking directories
def setup_ml_tracking_dirs(output_dir):
    """Setup wandb and mlflow directories in output folder"""
    wandb_dir = os.path.join(output_dir, "wandb")
    mlruns_dir = os.path.join(output_dir, "mlruns")
    
    os.makedirs(wandb_dir, exist_ok=True)
    os.makedirs(mlruns_dir, exist_ok=True)
    
    # Set environment variables
    os.environ["WANDB_DIR"] = wandb_dir
    os.environ["MLFLOW_TRACKING_URI"] = f"file://{mlruns_dir}"
    os.environ["WANDB_CACHE_DIR"] = os.path.join(wandb_dir, "cache")
    
    print(f"📊 ML tracking configured: wandb={wandb_dir}, mlruns={mlruns_dir}")


class JSONChatDataset(Dataset):
    """Loads JSON chat data, validates metadata, and creates tokenized training examples."""
    # setup components that will be used in methods for data loading and processing
    def __init__(self, tokenizer, json_path=None, block_size=512):
        # setup tokenizer 
        self.tokenizer = tokenizer
        # setup block size
        self.block_size = block_size
        
        # call function to find training file if not provided
        if json_path is None:
            json_path = self._find_training_file()

        # get JSON data from path and put it inside data var 
        print(f"📂 Loading processed chat data from: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        # call function that validates metadata & conversations
        self._validate_json()

        # Extract fom data
        # put in var metadata about training data
        self.metadata = self.data["metadata"]
        # put in var training conversations inside data called by _build_examples
        self.conversations = self.data["training_conversations"]
        print(f"💬 Loaded {len(self.conversations)} training conversations")

        # Convert conversations to tokenized examples
        self.examples = self._build_examples()
    # function that validates metadata & conversations
    def _validate_json(self):
        """Checks JSON structure and consistency using self.data."""
        # inside self.data check if metadata field exists
        if "metadata" not in self.data:
            raise ValueError("JSON missing 'metadata' field")
        # inside self.data check if training_conversations field exists
        if "training_conversations" not in self.data:
            raise ValueError("JSON missing 'training_conversations' field")
        # inside self.data check if training_conversations is not empty
        if len(self.data["training_conversations"]) == 0:
            raise ValueError("No conversations found in training data")
        
        print(f"✅ JSON validation passed: {len(self.data['training_conversations'])} conversations found")
    # function that finds best available training file
    #1. first try to load ai/training_data/parsed_data"
    #2. if not found look for default file chat_conversations_v1_parsed.json
    #3. if not found look for any json file in that dir and use first one
    def _find_training_file(self):
        """Find the best available training file"""
        # try to find files inside parsed_data_dir
        parsed_data_dir = "ai/chat_bot_trainer/training_data"
        # if parsed_data_dir does not exist raise error
        if not os.path.exists(parsed_data_dir):
            raise FileNotFoundError(f"Directory not found: {parsed_data_dir}")
        
        # Look for available JSON files and pick first one
        json_files = [f for f in os.listdir(parsed_data_dir) if f.endswith('.json')]
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in {parsed_data_dir}")
        
        # Use first available JSON file
        training_file = os.path.join(parsed_data_dir, json_files[0])
        print(f"🎯 Using training file: {os.path.basename(training_file)}")
        return training_file 
    # function that builds tokenized examples from conversations that are inside data
    #1. loops through self.data inside conversations key and extracts formatted_training_text
    #2. tokenizes text with truncation and max length
    #3. appends input ids to examples for model to read
    def _build_examples(self):
        # placeholder for examples
        examples = []
        # loops through self.data dictionary conversations
        for convo in self.conversations:
            # inside conversations look for formatted_training_text field
            # field contains the full text formated for training
            text = convo["formatted_training_text"]
            # print conversation id and exchange count
            print(f"📝 Processing conversation {convo['id']}: {convo['exchange_count']} exchanges")
            # print preview of formatted training text
            print(f"   Preview: {text[:150]}...")
            # tokenize text with truncation and max length
            tokens = self.tokenizer(
                text,
                truncation=True,
                max_length=self.block_size,
                return_tensors="pt"
            )
            # append input ids to examples for model to read
            examples.append(tokens["input_ids"].squeeze())
        # log created examples
        print(f"🎯 Created {len(examples)} tokenized training examples")
        return examples
    # functions required by Dataset class
    def __len__(self):
        return len(self.examples)
    # function to get item at index
    def __getitem__(self, idx):
        return self.examples[idx]
    # function to get metadata
    def get_metadata(self):
        return self.metadata
class ChatGPT2Trainer:
    """Handles loading GPT-2, training on dataset, and returning training metadata."""
    # setup components for training
    def __init__(self, model_name="gpt2", output_dir="ai/chat_bot_trainer/trained_models"):
        # setup model
        self.model_name = model_name
        # setup output directory
        self.output_dir = output_dir
        # create output directories if they don't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "final_chat_model"), exist_ok=True)
        
        # Setup ML tracking in output directory
        setup_ml_tracking_dirs(output_dir)
        
        # setup hardware device that will be used for training
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # log what hardware device being used
        print(f"🔧 Using device: {self.device}")
    # function to load model and tokenizer
    # 1. Load tokenizer and model
    # 2. Add special tokens to tokenizer
    # 3. Resize model embeddings to match tokenizer
    # 4. Move model to hardware device
    def load_model(self, special_tokens):
        """Loads tokenizer and model, adds special tokens."""
        print(f"🤖 Loading model: {self.model_name}")
        # Load tokenizer from pretrained model
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
        # add special tokens to tokenizer
        added = self.tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})
        # set pad token to eos token
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print(f"➕ Added {added} special tokens")
        # load based model that will be trained (fine-tuned)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
        # resize token embeddings to match new tokenizer size with special tokens
        self.model.resize_token_embeddings(len(self.tokenizer))
        # move model to hardware device
        self.model.to(self.device)
        
        print(f"📊 Model loaded. Vocab size: {len(self.tokenizer)}")
    # function that runs training
    #1. asks user confirmation before starting training
    #2. sets up data collator for language modeling
    #3. configures training arguments
    #4. initializes Trainer and starts training
    def train(self, dataset, epochs=5, batch_size=1, lr=2e-5):
        """Runs the actual GPT-2 training."""
        print("🚀 Starting model training...")
        print(f"📋 Training parameters: epochs={epochs}, batch_size={batch_size}, lr={lr}")
        print(f"📊 Training on {len(dataset)} examples")
        
        # Ask user confirmation
        user_input = input("\n➡️  Continue with training? (y/N): ").lower().strip()
        if user_input != 'y':
            print("⏸️  Training cancelled.")
            return None
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        # args for training
        args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=lr,
            save_steps=50,
            save_total_limit=2,
            logging_steps=5,
            warmup_steps=20,
            logging_dir=os.path.join(self.output_dir, "logs"),
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_drop_last=False,
            report_to=[]  # Disable all external tracking (wandb, mlflow, etc.)
        )
        # Initialize Trainer
        trainer = Trainer(
            model=self.model,
            args=args,
            data_collator=data_collator,
            train_dataset=dataset
        )
        # log training start
        print(f"🔥 Training for {epochs} epochs on {len(dataset)} examples...")
        # start training
        trainer.train()

        # inside save_path var put path and name of model
        save_path = os.path.join(self.output_dir, "final_chat_model", "trained_chat_model_1.0")
        os.makedirs(save_path, exist_ok=True)
        # save model to save_path 
        trainer.save_model(save_path)
        # save tokenizer to save_path
        self.tokenizer.save_pretrained(save_path)
        
        print(f"✅ Model training completed!")
        print(f"🎯 Final model saved to: {save_path}")

        # Return training metadata
        metadata = {
            "model_name": "trained_chat_model_1.0",
            "base_model": self.model_name,
            "model_path": save_path,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": lr,
            "device": str(self.device),
            "vocab_size": len(self.tokenizer),
            "num_examples": len(dataset),
            "training_data_metadata": dataset.get_metadata(),
            "trained_on": datetime.now().isoformat(),
            "special_tokens": ["<|client|>", "<|freelancer|>", "<|startoftext|>", "<|endoftext|>"]
        }
        
        # inside save_path, save metadata
        metadata_path = os.path.join(save_path, "training_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Training metadata saved to: {metadata_path}")
        
        return metadata


def main(json_path=None):
    special_tokens = ["<|client|>", "<|freelancer|>", "<|startoftext|>", "<|endoftext|>"]

    try:
        print(f"\n🎯 Starting GPT-2 training from processed JSON data")
        if json_path:
            print(f"📄 Using provided file: {json_path}")

        # Step 1: Prepare tokenizer
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        # Step 2: Build dataset (auto-finds file if json_path=None)
        dataset = JSONChatDataset(tokenizer, json_path)

        # Step 3: Train model
        trainer = ChatGPT2Trainer()
        trainer.load_model(special_tokens)

        metadata = trainer.train(
            dataset, 
            epochs=8, 
            batch_size=1, 
            lr=2e-5
        )

        if metadata:
            print("\n🎉 Training completed successfully!")
            print(f"🎯 Trained model available at: {metadata['model_path']}")
            print(f"🚀 Ready to use trained model!")
            return True
        else:
            print("\n❌ Training was cancelled or failed!")
            return False

    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 Training successful!' if success else '❌ Training failed!'}")
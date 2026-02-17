"""
AI Model Training Module
========================
Provides functionality for training custom AI models for cover letter generation
"""

import json
import logging
import torch
from pathlib import Path
from typing import Dict, List, Optional, Any
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

logger = logging.getLogger(__name__)

# class to hold functions that will train custom models
#1. model name
#2. output directory
#3. load base model function
#4. placeholder for model
#5. placeholder for tokenizer
#6. device setup for training
class CoverLetterTrainer:
    """Trainer for fine-tuning GPT-2 models on cover letter data"""
    # attributes that will be used in training
    def __init__(self, base_model: str = "gpt2", output_dir: str = None, training_data_dir: str = None):
        """Initialize CoverLetterTrainer with training data path"""
        self.base_model = base_model
        
        # Set default output directory
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(__file__),  # ai/cover_letter_trainer/
                'trained_models'            # ai/cover_letter_trainer/trained_models/
            )
        
        self.output_dir = Path(output_dir)
        
        # Set default path to training_data.json
        if training_data_dir is None:
            training_data_dir = os.path.join(
                os.path.dirname(__file__),  # ai/cover_letter_trainer/
                'training_data'             # ai/cover_letter_trainer/training_data/
            )
        
        self.training_data_dir = Path(training_data_dir)
        
        # Initialize model components (will be loaded later)
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Create directories if they don't exist
        self.output_dir.mkdir(exist_ok=True)
        self.training_data_dir.mkdir(exist_ok=True)

        # logging info
        logger.info(f"Initialized trainer with base model: {base_model}")
        logger.info(f"Using device: {self.device} (CPU-only training)")

    def load_training_data(self, filename: str = "training_data.json") -> List[Dict[str, Any]]:
        """Load training data from JSON file"""
        data_file = self.training_data_dir / filename
        
        if not data_file.exists():
            logger.warning(f"Training data file not found: {data_file}")
            raise FileNotFoundError(f"Training data file not found: {data_file}")
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            logger.info(f"Loaded {len(training_data)} training examples from {filename}")
            return training_data
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            raise


# ======== 🧱 load base model ======
    # function that takes initialized model and tokenizer and loads them to device
    # 1. load model from transformers
    # 2. load tokenizer from transformers
    # 3. move model to device
    def load_base_model(self):
        """Load the base GPT-2 model and tokenizer"""
        try:
            # logging info
            logger.info(f"Loading base model: {self.base_model}")
            # setup tokenizer from transformers
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.base_model)
            # setup model from transformers
            self.model = GPT2LMHeadModel.from_pretrained(self.base_model)

            # Add padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Move model to device
            self.model.to(self.device)
            # log success
            logger.info("Base model loaded successfully")
            # log error if loading fails
        except Exception as e:
            logger.error(f"Error loading base model: {e}")
            raise
# ======== 🧱 function to load base model ======

# ======== 🔨📝 prepare data for model training ==========
# takes training_data parameter which is a list of dicts
#1. loop through each example in training data
#2. in example find elements: job title, company, skills, cover letter in each example
#3. format elements with tags <JOB_TITLE>, <COMPANY>, <SKILLS>, <COVER_LETTER>, <END>
#4. tokenize elements with truncation, padding, max_length, return_tensors="pt"
#5. create dataset from tokenized data and give them input_ids, attention_mask, labels
    def prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Dataset:

        try:
            # logging info
            logger.info(f"Preparing {len(training_data)} training examples")
            # array to hold formatted texts
            formatted_texts = []
            # loop through each example in training data
            for example in training_data:
                # in each example find
                # job title
                job_title = example.get('job_title', 'Unknown Position')
                # company
                company = example.get('company', 'Unknown Company')
                # job skills (join and comma-separated)
                skills = ', '.join(example.get('skills', []))
                # cover letter
                cover_letter = example.get('cover_letter', '')

                # Create a formatted training example 
                # tags <JOB_TITLE>, <COMPANY>, <SKILLS>, <COVER_LETTER>, <END>
                # tags help model understand structure
                formatted_text = f"""<JOB_TITLE>{job_title}<COMPANY>{company}<SKILLS>{skills}<COVER_LETTER>{cover_letter}<END>"""
                # append to to formatted_texts list
                formatted_texts.append(formatted_text)

            # tokenizer setup
            #1. add formatted_texts from above
            #2. truncation, padding, max_length
            #3. return_tensors="pt"
            tokenized_data = self.tokenizer(
                formatted_texts, # list of formatted texts
                truncation=True, # truncate texts longer than max_length
                padding=True, # pad texts to max_length
                max_length=512,
                return_tensors="pt" # make PyTorch matrices instead of lists
            )

            # Create dataset from tokenized data (formatted_texts)
            # 1. input_ids for adding data to model
            # 2. attention_mask excludes padding from attention
            # 3. labels (same as input_ids for language modeling)
            dataset = Dataset.from_dict({
                # tokenized words presented as ids
                'input_ids': tokenized_data['input_ids'], 
                 # shows which tokens are real and which are padding
                'attention_mask': tokenized_data['attention_mask'],
                 # label what should the model predict (same as input_ids)
                'labels': tokenized_data['input_ids'].clone()
            })
            # log success
            logger.info("Training data prepared successfully")
            return dataset

        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise
# ======== 🏋️🤖 train model with prepared data ==========
    # function that makes pipeline to train model
    #1. load training data, name of trained model, num_epochs, learning_rate, batch_size, save_steps
    #2. try to load base model, tokenizer and training data and log
    #3. set up training arguments for Trainer
    #4. set up data collator for language modeling
    #5. set up Trainer with model, args, train_dataset, data_collator
    #6. start training with trainer.train()
    #7. save final model and tokenizer inside chosen dir
    #8. save training metadata to json file
    def train_model(
        self,
        training_data: List[Dict[str, Any]], # list of training examples
        model_name: str = "custom_cover_letter_model", # name of the model that will be saved after training
        num_epochs: int = 3, # number of times the model will see the entire training dataset
        learning_rate: float = 5e-5, # how quickly the model learns
        batch_size: int = 2,  # number of examples trained at the same time reduced for CPU
        save_steps: int = 500
    ):
        try:
            # load base model if not already loaded
            if self.model is None or self.tokenizer is None:
                self.load_base_model()
            # logging info
            logger.info(f"Starting training with {len(training_data)} examples")

            # Prepare training data
            train_dataset = self.prepare_training_data(training_data)

            # Set up training arguments
            #1. output_dir for saving model checkpoints
            #2. num_train_epochs for number of epochs
            #3. per_device_train_batch_size for how many examples to process at the same time
            #4. learning_rate for how quickly the model changes its weights
            #5. save_steps for how often to save model checkpoints
            #6. logging_steps for how often to log training progress
            training_args = TrainingArguments(
                output_dir=self.output_dir / model_name, # directory to save model checkpoints
                num_train_epochs=num_epochs, # number of epochs
                per_device_train_batch_size=batch_size, # batch size
                learning_rate=learning_rate, # learning rate
                save_steps=save_steps, # steps between saves
                save_total_limit=2, # total number of checkpoints to keep
                logging_steps=100, # steps between logging
                logging_dir=self.output_dir / model_name / "logs",
                report_to=None,  # Disable wandb logging
                overwrite_output_dir=True,
                no_cuda=True,  # Force CPU training
            )

            # library that compacts data for model training
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,
            )

            # library that handles the training loop
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                data_collator=data_collator,
            )

            # Start training
            logger.info("Training started...")
            trainer.train()

            # Save the final model 
            # path: output_dir/model_name/final
            final_model_path = self.output_dir / model_name / "final"
            # create directory if it doesn't exist
            trainer.save_model(final_model_path)
            # also save tokenizer
            self.tokenizer.save_pretrained(final_model_path)

            # Save training metadata
            metadata = {
                "base_model": self.base_model,
                "training_examples": len(training_data),
                "epochs": num_epochs,
                "learning_rate": learning_rate,
                "batch_size": batch_size,
                "model_path": str(final_model_path)
            }
            # save metadata to json file
            with open(final_model_path / "training_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Training completed! Model saved to: {final_model_path}")
            return final_model_path

        except Exception as e:
            logger.error(f"Error during training: {e}")
            raise
#========  ✅🈴🤔 evaluate model ========
    def evaluate_model(self, test_data: List[Dict[str, Any]], model_path: str):
        
# =====================> later add evaluation metrics
        try:
            # logging info
            logger.info("Loading trained model for evaluation")

            # Load the trained model
            model = GPT2LMHeadModel.from_pretrained(model_path)
            tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            model.to(self.device)
            model.eval()

            results = []
            # loop through test data
            for example in test_data:
                job_title = example.get('job_title', 'Unknown Position')
                company = example.get('company', 'Unknown Company')
                skills = ', '.join(example.get('skills', []))

                # prompt to generate cover letter
                prompt = f"<JOB_TITLE>{job_title}<COMPANY>{company}<SKILLS>{skills}<COVER_LETTER>"
                # tokenize prompt
                inputs = tokenizer(prompt, return_tensors='pt').to(self.device)
                # generate cover letter
                with torch.no_grad():
                    outputs = model.generate(
                        inputs['input_ids'],
                        attention_mask=inputs['attention_mask'],
                        max_length=inputs['input_ids'].shape[1] + 200,
                        temperature=0.7,
                        do_sample=True,
                        top_p=0.9,
                        top_k=30,
                        num_return_sequences=1,
                        pad_token_id=tokenizer.eos_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                        no_repeat_ngram_size=2
                    )
                # decode generated text
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                generated_cover_letter = generated_text.replace(prompt, '').strip()
                # append results
                results.append({
                    'job_title': job_title,
                    'company': company,
                    'generated_cover_letter': generated_cover_letter
                })

            logger.info(f"Evaluation completed for {len(results)} examples")
            return results

        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            raise

# ==== MAIN EXECUTION BLOCK ====
if __name__ == "__main__":
    import os
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Cover Letter Trainer")
    print("=" * 50)

    try:
        # Initialize trainer
        trainer = CoverLetterTrainer()
        print(f"✅ Trainer initialized")
        print(f"📂 Training data directory: {trainer.training_data_dir}")
        print(f"📂 Output directory: {trainer.output_dir}")
        
        # Check if training data exists
        training_data_file = trainer.training_data_dir / "training_data.json"
        if not training_data_file.exists():
            print(f"❌ Training data not found: {training_data_file}")
            print("💡 Please create training_data.json file in the training_data directory")
            exit(1)
        
        # Load training data
        training_data = trainer.load_training_data()
        print(f"✅ Loaded {len(training_data)} training examples")
        
        # Show sample data
        if training_data:
            sample = training_data[0]
            print(f"\n📋 Sample training example:")
            print(f"   Job Title: {sample.get('job_title', 'N/A')}")
            print(f"   Company: {sample.get('company', 'N/A')}")
            print(f"   Skills: {sample.get('skills', [])}")
            print(f"   Cover Letter Length: {len(sample.get('cover_letter', ''))} characters")
        
        # Ask user if they want to start training
        response = input(f"\n➡️  Start training with {len(training_data)} examples? (y/N): ")
        
        if response.lower() == 'y':
            print("\n🔥 Starting model training...")
            
            # Start training
            final_model_path = trainer.train_model(
                training_data=training_data,
                model_name="custom_cover_letter_model",
                num_epochs=3,
                learning_rate=5e-5,
                batch_size=2
            )
            
            print(f"\n🎉 Training completed!")
            print(f"📁 Model saved to: {final_model_path}")
            
        else:
            print("❌ Training cancelled")
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("💡 Make sure training_data.json exists in ai/cover_letter_trainer/training_data/")
    except Exception as e:
        print(f"❌ Training failed: {e}")
        logging.error(f"Training failed: {e}")
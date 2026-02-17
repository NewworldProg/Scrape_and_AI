"""
Advanced Model Training Example
===============================
Advanced training with validation and evaluation
"""

import json
import logging
from pathlib import Path
from ai.model_training import CoverLetterTrainer

# logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# function that will load training data
def load_training_data(file_path: str) -> list:
    """Load training data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

# function to split data into training and validation sets
def split_data(data: list, train_ratio: float = 0.8):
    """Split data into training and validation sets"""
    split_idx = int(len(data) * train_ratio)
    return data[:split_idx], data[split_idx:]

def main():
    # Load data from file (you can replace with your data file)
    data_file = Path(__file__).parent.parent.parent / "training_data.json"
    # if file does not exist log error and ask to create it
    if not data_file.exists():
        logger.error(f"Training data file not found: {data_file}")
        logger.info("Please create training_data.json with your cover letter examples")
        return

    # Load and split data
    all_data = load_training_data(data_file)
    train_data, val_data = split_data(all_data)
    # Log data for info
    logger.info(f"Loaded {len(all_data)} examples")
    logger.info(f"Training: {len(train_data)}, Validation: {len(val_data)}")

    # Initialize trainer with larger model
    trainer = CoverLetterTrainer(
        base_model="gpt2-medium",  # Larger model for better results
        output_dir="./trained_models"
    )

    try:
        # Train with advanced parameters
        logger.info("Starting advanced model training...")
        model_path = trainer.train_model(
            training_data=train_data,
            model_name="advanced_cover_letter_model",
            num_epochs=5,  # More epochs for better training
            batch_size=2,  # Smaller batch size for CPU
            learning_rate=3e-5,  # Slightly lower learning rate
            save_steps=200  # Save more frequently
        )

        logger.info(f"Training completed! Model saved to: {model_path}")

        # Evaluate on validation data
        if val_data:
            logger.info("Evaluating model on validation data...")
            evaluation_results = trainer.evaluate_model(val_data, model_path)

            # Save evaluation results
            output_dir = Path(model_path)
            with open(output_dir / "evaluation_results.json", 'w') as f:
                json.dump(evaluation_results, f, indent=2)

            logger.info("Evaluation completed and saved")

        # Save training configuration
        config = {
            "base_model": "gpt2-medium",
            "epochs": 5,
            "batch_size": 4,
            "learning_rate": 3e-5,
            "training_examples": len(train_data),
            "validation_examples": len(val_data)
        }

        with open(Path(model_path) / "training_config.json", 'w') as f:
            json.dump(config, f, indent=2)

        logger.info("Training configuration saved")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()
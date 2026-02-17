"""
Model Evaluation Script
=======================
Evaluate trained models on test data
"""

import json
import logging
from pathlib import Path
from ai.model_training import CoverLetterTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_test_data(file_path: str) -> list:
    """Load test data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def evaluate_and_compare(base_model_path: str, trained_model_path: str, test_data: list):
    """Compare base model vs trained model performance"""
    trainer = CoverLetterTrainer()

    logger.info("Evaluating base model...")
    base_results = trainer.evaluate_model(test_data, base_model_path)

    logger.info("Evaluating trained model...")
    trained_results = trainer.evaluate_model(test_data, trained_model_path)

    # Compare results
    comparison = []
    for i, (base, trained) in enumerate(zip(base_results, trained_results)):
        comparison.append({
            "example": i + 1,
            "job_title": base["job_title"],
            "company": base["company"],
            "base_model_length": len(base["generated_cover_letter"]),
            "trained_model_length": len(trained["generated_cover_letter"]),
            "base_cover_letter": base["generated_cover_letter"][:200] + "...",
            "trained_cover_letter": trained["generated_cover_letter"][:200] + "..."
        })

    return comparison

def main():
    # Paths - adjust these to your model locations
    base_model = "gpt2"  # Base GPT-2 model
    trained_model = "./trained_models/advanced_cover_letter_model/final"

    # Test data file
    test_file = Path(__file__).parent.parent.parent / "test_data.json"

    if not Path(trained_model).exists():
        logger.error(f"Trained model not found: {trained_model}")
        return

    if not test_file.exists():
        logger.error(f"Test data file not found: {test_file}")
        logger.info("Please create test_data.json with evaluation examples")
        return

    # Load test data
    test_data = load_test_data(test_file)
    logger.info(f"Loaded {len(test_data)} test examples")

    try:
        # Evaluate models
        comparison = evaluate_and_compare(base_model, trained_model, test_data)

        # Save results
        output_file = Path(trained_model).parent / "model_comparison.json"
        with open(output_file, 'w') as f:
            json.dump(comparison, f, indent=2)

        logger.info(f"Evaluation completed! Results saved to: {output_file}")

        # Print summary
        print("\n=== EVALUATION SUMMARY ===")
        print(f"Tested {len(comparison)} examples")
        print(f"Results saved to: {output_file}")

        # Calculate average lengths
        base_avg = sum(c["base_model_length"] for c in comparison) / len(comparison)
        trained_avg = sum(c["trained_model_length"] for c in comparison) / len(comparison)

        print(".1f")
        print(".1f")

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise

if __name__ == "__main__":
    main()
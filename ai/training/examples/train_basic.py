"""
Basic Model Training Example
============================
Simple example of training a custom cover letter model
"""

import json
import logging
from pathlib import Path
from ai.model_training import CoverLetterTrainer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Sample training data
    training_data = [
        {
            "job_title": "Python Developer",
            "company": "Tech Corp",
            "skills": ["Python", "Django", "React"],
            "cover_letter": """Dear Hiring Manager,

I am excited to apply for the Python Developer position at Tech Corp. With my expertise in Python, Django, and React, I am confident I can contribute effectively to your team.

I have extensive experience developing web applications using Python and Django, creating responsive user interfaces with React, and working in agile development environments. My technical background and problem-solving abilities make me well-suited for this role.

I would welcome the opportunity to discuss how my background and enthusiasm can contribute to the success of your projects at Tech Corp.

Best regards,
[Your Name]"""
        },
        {
            "job_title": "Data Scientist",
            "company": "DataTech Inc",
            "skills": ["Python", "Machine Learning", "SQL"],
            "cover_letter": """Dear Hiring Manager,

I am writing to express my interest in the Data Scientist position at DataTech Inc. My background in Python, Machine Learning, and SQL makes me an ideal candidate for this role.

Throughout my career, I have successfully applied machine learning techniques to solve complex business problems, built predictive models using Python and scikit-learn, and optimized database queries for improved performance. I am passionate about using data to drive insights and make informed decisions.

I would be thrilled to bring my analytical skills and technical expertise to your innovative team at DataTech Inc.

Best regards,
[Your Name]"""
        }
    ]

    # Initialize trainer
    trainer = CoverLetterTrainer(
        base_model="gpt2",
        output_dir="./trained_models"
    )

    try:
        # Train the model
        logger.info("Starting model training...")
        model_path = trainer.train_model(
            training_data=training_data,
            model_name="basic_cover_letter_model",
            num_epochs=2,  # Quick training for demo
            batch_size=1,  # Smaller batch size for CPU
            learning_rate=5e-5
        )

        logger.info(f"Training completed! Model saved to: {model_path}")

        # Save training data for reference
        output_dir = Path(model_path)
        with open(output_dir / "training_data.json", 'w') as f:
            json.dump(training_data, f, indent=2)

        logger.info("Training data saved alongside model")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()
"""
Local AI Provider Module
========================
Provides local AI-powered cover letter generation using GPT-2
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
import os
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# variable to hold loading libraries
logger = logging.getLogger(__name__)

# Local AI Provider Class
# it will initialize local AI from config.json
# make pipeline to generate letters
class LocalAIProvider:
    """Local AI provider for cover letter generation using GPT-2"""

    def __init__(self, config_path: Optional[str] = None):
        # path for calling config.json
        self.config_path = config_path or Path(__file__).parent / "config.json"
        # load config with function bellow
        self.config = self._load_config()
        # variable for model from config inside load_model
        self.model = None
        # variable for tokenizer from config inside load_model
        self.tokenizer = None
        # load model
        self._load_model()

    # ======== 🧱 function to load config file with model variables =======
    def _load_config(self) -> Dict[str, Any]:
        try:
            # if json config file exists load the configuration
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # else fallback to default configuration
                return {
                    "model_name": "gpt2",
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "cache_dir": None
                }
            # if error return empty dict
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    # ======== 🧱 function to load model ======

    # ======= 🧱🤖 function to load model ======
    def _load_model(self):
        try:
            # from config get model name
            model_name = self.config.get('model_name', 'gpt2')
            # from config get cache dir
            cache_dir = self.config.get('cache_dir')
            # log info
            logger.info(f"Loading GPT-2 model: {model_name}")

            # ==========🧊 Load tokenizer ======
            self.tokenizer = GPT2Tokenizer.from_pretrained(
                model_name, # tokenizer for model that is used
                cache_dir=cache_dir, # cache directory for model
                padding_side='left' # set padding to left
            )

            # if no pad token fallback to eos token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            self.model = GPT2LMHeadModel.from_pretrained(
                model_name, # model name from config
                cache_dir=cache_dir # cache directory for model
            )

            # Set to evaluation mode
            self.model.eval()

            # Move to CPU (for weaker systems)
            self.device = torch.device('cpu')
            # Move model to the device
            self.model.to(self.device)

            # Log successful model loading
            logger.info(f"GPT-2 model loaded successfully on {self.device}")
        # log error if loading fails
        except Exception as e:
            logger.error(f"Error loading GPT-2 model: {e}")
            self.model = None
            self.tokenizer = None
    # ======= 🧱🤖 function to load model ======

    # ======= ✍️🤖prompt to generate cover letter ======
    def generate_cover_letter(self, job_data: Dict[str, Any]) -> str:
        # function that returns a bool after checking if self.model and self.tokenizer are loaded
        # if not
        if not self.is_available():
        # use template fallback    
            return self._generate_template_cover_letter(job_data)

        try:
            import torch
            # extract job details from job_data
            job_title = job_data.get('title', 'Unknown Position')
            company = job_data.get('company', 'Unknown Company')
            description = job_data.get('description', 'No description available')
            skills = job_data.get('skills', [])
            # extract skills string
            skills_str = ', '.join(skills) if skills else 'various technologies'

            # in variable put the prompt for the LLM model
            prompt = f"I am an experienced {job_title} with expertise in {skills_str}. "

            # tokenize prompt with self.tokenizer which was loaded in load_model
            inputs = self.tokenizer(
                prompt,
                return_tensors='pt',
                truncation=True,
                max_length=128
            ).to(self.device)
            # output it to device

            # class that generates text
            # calls function generate and gets output
            with torch.no_grad():
                outputs = self.model.generate(
                    # tokenized input ids which look like [[123,456,789]]
                    inputs['input_ids'], 
                    # attention mask diversing which tokens to pay attention to
                    attention_mask=inputs['attention_mask'], 
                    # maxlength of output tokens, including prompt + 50 tokens
                    max_length=inputs['input_ids'].shape[1] + 50,  # Short generation
                    # how much creativity to use when generating
                    temperature=0.7,
                    # use top-k sampling
                    do_sample=True,
                    # use nucleus sampling
                    top_p=0.9,
                    top_k=30,
                    # use typical sampling
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=2
                )

            # Decode returned tokens and clean up
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            ai_summary = generated_text[len(prompt):].strip()

            # Clean up the AI summary (take first 1-2 sentences)
            sentences = ai_summary.split('.')
            clean_summary = '. '.join(sentences[:2]).strip()
            if clean_summary and not clean_summary.endswith('.'):
                clean_summary += '.'

            logger.info(f"AI summary exists: {bool(clean_summary)}")

            # inside variable put the cover starting text
            # than add the AI generated summary or fallback text if summary is empty
            cover_letter = f"""Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}. With my expertise in {skills_str}, I am excited to bring my skills and experience to your team.

{clean_summary or "I have extensive experience in software development and am passionate about creating innovative solutions."}

Based on the job description, I understand you are looking for someone who can contribute effectively to your projects involving {description[:100]}... My technical background and problem-solving abilities make me well-suited for this role.

I would welcome the opportunity to discuss how my background and enthusiasm can contribute to the success of your projects at {company}.

Thank you for considering my application.

Best regards,
[Your Name]"""

            logger.info(f"Generated enhanced GPT-2 cover letter for job: {job_title}")
            return cover_letter.strip()

        except Exception as e:
            logger.error(f"Error generating GPT-2 cover letter: {e}")
            return self._generate_template_cover_letter(job_data)

    # the fallback template function
    def _generate_template_cover_letter(self, job_data: Dict[str, Any]) -> str:
        """Generate a template-based cover letter as fallback"""
        job_title = job_data.get('title', 'Unknown Position')
        company = job_data.get('company', 'Unknown Company')
        description = job_data.get('description', 'No description available')
        skills = job_data.get('skills', [])

        skills_str = ', '.join(skills) if skills else 'various technologies'

        # Create a more professional template
        cover_letter = f"""Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}. With my expertise in {skills_str}, I am excited to bring my skills and experience to your team.

Based on the job description, I understand you are looking for someone who can contribute effectively to {description[:100]}... My background in {skills_str} makes me well-suited for this role.

I have extensive experience working with {skills_str}, and I am confident that my technical skills and problem-solving abilities would be valuable assets to your organization.

I would welcome the opportunity to discuss how my background and enthusiasm for technology can contribute to the success of your projects.

Thank you for considering my application. I look forward to the possibility of contributing to {company}.

Best regards,
[Your Name]"""

        return cover_letter.strip()

    def is_available(self) -> bool:
        return self.model is not None and self.tokenizer is not None
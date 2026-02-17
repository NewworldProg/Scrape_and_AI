"""
OpenAI Provider Module
======================
Provides OpenAI-powered cover letter generation
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

logger = logging.getLogger(__name__)

class OpenAIProvider:

    # ======= 🧱 function to initialize OpenAI provider ======
    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        # path for calling config.json
        self.config_path = config_path or Path(__file__).parent / "config.json"
        self.config = self._load_config()
        # get api key from parameter, config, or env variable
        self.api_key = api_key or self.config.get('api_key') or os.getenv('OPENAI_API_KEY')

        if OPENAI_AVAILABLE and self.api_key:
            openai.api_key = self.api_key

    # from config file load configuration
    def _load_config(self) -> Dict[str, Any]:

        try:
            # load config if file exists
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # else Default configuration
                return {
                    "api_key": None,
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "system_prompt": "You are a professional cover letter writer. Generate compelling, personalized cover letters for job applications."
                }
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def generate_cover_letter(self, job_data: Dict[str, Any]) -> str:
        # check if OpenAI library is installed
        # error message if not
        if not OPENAI_AVAILABLE:
            return "OpenAI library not available. Please install with: pip install openai"

        # check if API key is configured
        # error message if not
        if not self.api_key:
            return "OpenAI API key not provided. Set OPENAI_API_KEY environment variable or provide in config."

        try:
            # check if job data is scraped correctly
            job_title = job_data.get('title', 'Unknown Position')
            company = job_data.get('company', 'Unknown Company')
            description = job_data.get('description', 'No description available')
            skills = job_data.get('skills', [])

            # Create prompt for cover letter generation
            # takes scraped job data to generate letter
            prompt = f"""
Write a professional cover letter for the following job:

Job Title: {job_title}
Company: {company}
Description: {description}
Required Skills: {', '.join(skills) if skills else 'Not specified'}

Please write a compelling cover letter that:
- Highlights relevant experience and skills
- Shows enthusiasm for the role and company
- Is professional and well-structured
- Is approximately 300-400 words

Cover Letter:
"""
            # generate cover letter using OpenAI ChatCompletion
            response = openai.ChatCompletion.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": self.config.get('system_prompt', 'You are a professional cover letter writer.')},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get('max_tokens', 1000),
                temperature=self.config.get('temperature', 0.7)
            )

            cover_letter = response.choices[0].message.content.strip()
            logger.info(f"Generated cover letter for job: {job_title}")
            return cover_letter

        except Exception as e:
            logger.error(f"Error generating cover letter with OpenAI: {e}")
            return f"Error generating cover letter: {str(e)}"

    def is_available(self) -> bool:
        """Check if OpenAI is available and configured"""
        return OPENAI_AVAILABLE and bool(self.api_key)
"""
AI Module for Upwork Notification System
========================================
Provides AI-powered functionality for job processing and communication
"""

# Import available modules
from .local_ai import LocalAIProvider
from .openai import OpenAIProvider

__all__ = ['LocalAIProvider', 'OpenAIProvider']
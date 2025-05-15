"""
ConfRAG project configuration file

This file contains all constant configurations used in the project, which are centrally managed for easy maintenance and configuration.
"""

import os

# API Key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')

# Model Configuration
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 1000

# Website crawling configuration
MAX_WEBSITES = 5  # Maximum number of websites
DEFAULT_USER_AGENT = '*'  # Default User Agent

# File path
KEYWORD_PROMPT_PATH = "reproduceDataset/PromptGetKeyWord.txt"
FULL_CONTEXT_PROMPT_PATH = "reproduceDataset/PromptForFullContext.txt"
SUMMARIZING_PROMPT_PATH = "reproduceDataset/PromptSummarizingNew.txt"
TEST_PROMPT_PATH = "generateResult/TestPrompt.txt"

CACHE_SIZE = 1024  # LRU cache size

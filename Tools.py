"""
Tools module for handling OpenAI API interactions and JSON processing.

This module provides utilities for:
1. Chatting with GPT models using OpenAI API
2. Cleaning and parsing JSON strings
"""

# Standard library imports
import json
import os
from typing import Union, List, Dict, Tuple

# Third-party imports
from openai import OpenAI

# Environment variables
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')

def chatWithGPT(
    messages: Union[str, List[Dict[str, str]]],
    model: str = "gpt-4",
    temperature: float = 0.1,
    max_tokens: int = 1000
) -> Tuple[str, bool]:
    """Chat with GPT model and get response.
    
    This function handles communication with OpenAI's GPT models. It supports both
    single string messages and structured message lists.

    Parameters
    ----------
    messages : Union[str, List[Dict[str, str]]]
        Input messages for the chat. Can be either a string or a list of message dictionaries
        containing 'role' and 'content' keys.
    model : str, optional
        The model to use, by default "gpt-4".
    temperature : float, optional
        Controls randomness of the output, by default 0.1.
    max_tokens : int, optional
        Maximum number of tokens to generate, by default 1000.
        
    Returns
    -------
    Tuple[str, bool]
        A tuple containing:
        - response_text (str): The generated response from GPT
        - success_status (bool): Boolean indicating if the API call was successful
    """
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )
    
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
        
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60
        )
        return response.choices[0].message.content, True
    except Exception as e:
        return str(e), False

def jsonClean(s1: str, keys: List[str] = None) -> Tuple[Dict, bool]:
    """Clean and parse JSON string.
    
    This function handles cleaning and parsing of JSON strings, with support for
    markdown-formatted JSON and required key validation.

    Parameters
    ----------
    s1 : str
        Input JSON string to clean and parse.
    keys : List[str], optional
        List of required keys that must be present in the JSON, by default None.
        
    Returns
    -------
    Tuple[Dict, bool]
        A tuple containing:
        - parsed_data (Dict): The parsed JSON data or error message
        - success_status (bool): Boolean indicating if parsing was successful
    """
    try:
        # Remove markdown formatting if present
        if '```json' in s1:
            s1 = s1.split('```json')[1]
            s1 = s1.split('```')[0]
        
        # Clean the string
        s2 = s1.replace('\\n', '')
        s3 = s2.replace('```json', '').replace('```', '')
        s4 = s3.replace('\\', '')
        
        # Remove surrounding quotes if present
        if s4.startswith('"') and s4.endswith('"'):
            s4 = s4[1:-1]
            
        data = json.loads(s4)
        
        # Validate required keys if specified
        if keys is not None:
            for key in keys:
                if key not in data:
                    return f"Key {key} not in data", False
                    
        return data, True
    except Exception as e:
        return str(e), False

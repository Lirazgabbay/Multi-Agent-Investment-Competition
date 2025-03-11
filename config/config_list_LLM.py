import os
from dotenv import load_dotenv

load_dotenv()
api_key_open_AI = os.getenv('OPENAI_API_KEY')
# config_LLM.py - Configuration file for the Language Learning Model (LLM) API
CONFIG_LLM_GPT = [
    {
        'model': 'gpt-3.5-turbo',
        'api_key': api_key_open_AI
    }
]
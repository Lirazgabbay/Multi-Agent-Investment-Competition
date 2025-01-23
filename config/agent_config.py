"""
    agent_config.py - Configuration file for the agents
"""
from config.available_functions import LIQUIDITY_AVAILABLE_FUNCTIONS, MARGIN_MULTIPLIER_AVAILABLE_FUNCTIONS, QUALITATIVE_AVAILABLE_FUNCTIONS
from config.config_list_LLM import CONFIG_LLM_GPT4
from config.system_messages import SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_LIQUIDITY_CONFIG, SYSTEM_MSG_QUALITATIVE_CONFIG

# Define the Technical Analysis Agents:

LIQUIDITY_CONFIG = {
    "name": "Liquidity_Analyst",
    "llm_config": {
        "config_list": CONFIG_LLM_GPT4,
        "temperature": 0.4,
        "functions": LIQUIDITY_AVAILABLE_FUNCTIONS
    },
    "system_message": SYSTEM_MSG_LIQUIDITY_CONFIG
}

HISTORICAL_MARGIN_MULTIPLIER_CONFIG = {
    "name": "Historical_Margin_Multiplier_Analyst",
    "llm_config": {
        "config_list": CONFIG_LLM_GPT4,
        "temperature": 0.4,
        "functions": MARGIN_MULTIPLIER_AVAILABLE_FUNCTIONS
    },
    "system_message": SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG
}

COMPETATIVE_MARGIN_MULTIPLIER_CONFIG = {
    "name": "Competative_Margin_Multiplier_Analyst",
    "llm_config": {
        "config_list": CONFIG_LLM_GPT4,
        "temperature": 0.4,
        "functions": MARGIN_MULTIPLIER_AVAILABLE_FUNCTIONS
    },
    "system_message": SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG
}


QUALITATIVE_CONFIG = {
    "name": "Qualitative_Analyst",
    "llm_config": {
        "config_list": CONFIG_LLM_GPT4,
        "temperature": 0.4,
        "functions" : QUALITATIVE_AVAILABLE_FUNCTIONS
    },
    "system_message": SYSTEM_MSG_QUALITATIVE_CONFIG
}


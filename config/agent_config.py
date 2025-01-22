"""
    agent_config.py - Configuration file for the agents
"""
from config.available_functions import LIQUIDITY_AVAILABLE_FUNCTIONS
from config.config_list_LLM import CONFIG_LLM_GPT4
from config.system_messages import SYSTEM_MSG_LIQUIDITY_CONFIG

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

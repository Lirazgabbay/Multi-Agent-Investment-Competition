"""
available_functions.py - Configuration file for define the available functions for the Liquidity Analyst agent
"""
from typing import Any, Dict

LIQUIDITY_AVAILABLE_FUNCTIONS : Dict[str, Dict[str, Any]] = {
     "quick_ratio": {
        "name": "quick_ratio",
        "description": "Calculate the quick ratio (Current Assets - Inventories) / Current Liabilities for a company in a specific year",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                },
                "year": {
                    "type": "string",
                    "description": "The year for which to calculate the quick ratio"
                }
            },
            "required": ["ticker", "year"]
        }
    }
}
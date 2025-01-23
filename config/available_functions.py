"""
available_functions.py - Configuration file for define the available functions for the Liquidity Analyst agent
"""
from typing import Any, Dict
from finance.LLM_get_financial import quick_ratio
from finance.profit_margin import gross_profit_margin, operational_profit_margin, net_profit_margin
from finance.profit_multipliers import (
    price_sales_ratio,
    price_to_EBIT_ratio,
    price_to_book_value_ratio,
    price_to_earnings_ratio,
    price_earnings_to_growth_ratio
)
from finance.LLM_get_qualitative import get_company_data, extract_businees_info

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


MARGIN_MULTIPLIER_AVAILABLE_FUNCTIONS: Dict[str, Dict[str, Any]] = {
    "gross_profit_margin": {
        "name": "gross_profit_margin",
        "description": "Calculate Gross Profit Margin (Gross Profit / Revenue) for a company ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["symbol"]
        }
    },
    "operational_profit_margin": {
        "name": "operational_profit_margin",
        "description": "Calculate Operating Profit Margin (Operating Income / Revenue) for a company ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["symbol"]
        }
    },
    "net_profit_margin": {
        "name": "net_profit_margin",
        "description": "Calculate Net Profit Margin (Net Income / Revenue) for a company ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["symbol"]
        }
    },
    "price_sales_ratio": {
        "name": "price_sales_ratio",
        "description": "Calculate Price/Sales ratio (Price divided by Total Revenue) for a company ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["symbol"]
        }
    },
    "price_to_EBIT_ratio": {
        "name": "price_to_EBIT_ratio",
        "description": "Calculate Price/EBIT ratio (Price divided by Earnings Before Interest and Taxes) for a company ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["symbol"]
        }
    },
    "price_to_book_value_ratio": {
        "name": "price_to_book_value_ratio",
        "description": "Calculate Price/Book Value ratio (Market Cap divided by Book Value) for a company ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["symbol"]
        }
    },
    "price_to_earnings_ratio": {
        "name": "price_to_earnings_ratio",
        "description": "Calculate Price/Earnings ratio (Market Cap divided by Net Income) for a company ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["symbol"]
        }
    },
    "price_earnings_to_growth_ratio": {
        "name": "price_earnings_to_growth_ratio",
        "description": "Calculate PEG ratio (Price/Earnings ratio divided by Annual EPS Growth rate) for a company ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["symbol"]
        }
    } 
}

QUALITATIVE_AVAILABLE_FUNCTIONS: Dict[str, Dict[str, Any]] = {
    "get_company_data": {
        "name": "get_company_data",
        "description": "Fetch API company data from Polygon.io API",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["ticker"]
        }
    },
    "extract_businees_info": {
        "name": "extract_businees_info",
        "description": "Extract strategic elements from company info dictionary",
        "parameters": {
            "type": "object",
            "properties": {
                "company_ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOG')"
                }
            },
            "required": ["company_ticker"]
        }
    }
}
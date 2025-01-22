"""
    LLM_get_financial.py - Functionsfor the Analyst agents
"""
from finance.balance_sheet_helpers import get_assets, get_inventory, get_liabilities

def quick_ratio(ticker: str, year: str) -> float|None:
    """
    Quick Ratio = (Current Assets - Inventories) / Current Liabilities
    """
    current_assets = get_assets(ticker, year)
    inventory = get_inventory(ticker, year)
    current_liabilities = get_liabilities(ticker, year)

    if current_assets is None or inventory is None or current_liabilities is None:
        return None
        
    return (current_assets - inventory) / current_liabilities if current_liabilities != 0 else 0


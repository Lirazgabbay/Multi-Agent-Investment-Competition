"""
agents_functions.py
This file contains wrapper functions that the agents will use to interact with the finance module. 
These functions will be called by the agents to get financial data and perform analysis.
"""
from finance.LLM_get_financial import get_related_companies
from finance.LLM_get_qualitative import extract_business_info, get_company_data
from finance.profit_margin import calculate_profit_margins
from finance.profit_multipliers import price_to_EBIT_ratio, ratios

def historical_func(symbols: list, years: list):
    """
    receives a list of symbols and a list of years and returns a dictionary with the historical data for each symbol

    returns:
        results: dictionary with the historical data for each symbol
    """
    results = {}

    for symbol in symbols:
        results[symbol] = {}
        for year in years:
            results[symbol][year] = {                
                "profit_margins": calculate_profit_margins(symbol, year),
                "price_to_EBIT_ratio": price_to_EBIT_ratio(symbol, year),
                "ratios": ratios(symbol, year),
            }

    return results


def competative_func(symbol: str, years: list[int]):
    """
    Receives a symbol and a list of years and returns a dictionary with the competitive data for the symbol.

    Returns:
        results: dictionary with the competitive data for the symbol.
    """
    results = {}
    related_companies = get_related_companies(symbol)
    
    if not related_companies:
        results[symbol] = {"error": "No related companies found"}
        return results  # Return early if no competitors are found

    related_company = related_companies[0]
    results[related_company] = {}
    results[symbol] = {}

    for year in years:
        results[related_company][year] = {
            "price_to_EBIT_ratio": price_to_EBIT_ratio(related_company, year),
            "ratios": ratios(related_company, year),
        }

        results[symbol][year] = {
            "price_to_EBIT_ratio": price_to_EBIT_ratio(symbol, year),
            "ratios": ratios(symbol, year),
        }

    return results


def qualitative_func(symbols: list):
    """
    receives a list of symbols and returns a dictionary with the qualitative data for each symbol
    
    returns:
        results: dictionary with the qualitative data for each symbol
    """
    results = {}

    for symbol in symbols:
        results[symbol] = {
            "business_info": extract_business_info(symbol),
            "company_data": get_company_data(symbol),
        }

    return results


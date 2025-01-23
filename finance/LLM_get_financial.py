"""
    LLM_get_financial.py - Functionsfor the Analyst agents
"""
import os
from dotenv import load_dotenv
import requests
from balance_sheet_helpers import get_assets, get_inventory, get_liabilities

def quick_ratio(ticker: str, year: str):
    """
    Quick Ratio = (Current Assets - Inventories) / Current Liabilities
    """
    current_assets = get_assets(ticker, year)
    inventory = get_inventory(ticker, year)
    current_liabilities = get_liabilities(ticker, year)

    if current_assets is None or inventory is None or current_liabilities is None:
        return None
        
    return (current_assets - inventory) / current_liabilities if current_liabilities != 0 else 0


def get_related_companies(ticker: str, n = 1) -> list:
    """
    Fetch up to n related tickers for the given ticker from Polygon.io.

    args: ticker: The stock symbol for which related tickers are requested (e.g., "AAPL").
            n: The maximum number of related tickers to return.
            api_key: Your Polygon.io API key.

    return: A list of related ticker symbols.
    """
    load_dotenv()
    api_key_polygon = os.getenv('POLYGON_API_KEY')
    url = f"https://api.polygon.io/v1/related-companies/{ticker}"
    params = {
        "apiKey": api_key_polygon
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(
            f"Polygon.io API request failed with status code "
            f"{response.status_code} and error: {response.text}"
        )

    data = response.json()
    print(data)

    top_n_competitors = []
    related_tickers = data.get("results", [])
    for ticker in related_tickers:
        top_n_competitors.append(ticker["ticker"])
        if len(top_n_competitors) >= n:
            break

    return top_n_competitors


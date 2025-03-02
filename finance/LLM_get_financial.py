"""
    LLM_get_financial.py - Functions for the Analyst agents
"""
import json
import os
from dotenv import load_dotenv
import requests
from database.api_utils import cached_api_request


def quick_ratio(symbol: str, year: int) -> str:
    """
    Fetches the Quick Ratio (TTM) for the given company ticker using FMP API.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        str: The Quick Ratio as a string, or an error message if unavailable.
    """
    response_text = cached_api_request(
        url=f"https://financialmodelingprep.com/api/v3/ratios/{symbol}",
        api_key_name="FMP_API_KEY",
        api_key_param="apikey",
        api_key_in_url=True,
        params={"period": "annual"}
    )
    try:
        data = json.loads(response_text)
        if data:
            for dict in data:
                if dict.get('calendarYear') == str(year):
                    quick_ratio_value = dict.get('quickRatio')
                    return str(quick_ratio_value)
            return "No data found for the specified year."
        else:
            return "No data returned for the specified ticker."
    except json.JSONDecodeError:
        return f"Failed to parse API response as JSON."
    return None



def get_related_companies(symbol: str, n: int = 1) -> list:
    """
    Fetch up to n related tickers for the given ticker from Polygon.io.

    args: ticker: The stock symbol for which related tickers are requested (e.g., "AAPL").
            n: The maximum number of related tickers to return.
            api_key: Your Polygon.io API key.

    return: A list of related ticker symbols.
    """
    response_text = cached_api_request(
        url=f"https://api.polygon.io/v1/related-companies/{symbol}",
        api_key_name="POLYGON_API_KEY",
        api_key_in_url=False,
        api_key_param="apiKey"
    )
 
    try:
        data = json.loads(response_text)
        top_n_competitors = []
        related_tickers = data.get("results", [])
        for ticker in related_tickers:
            top_n_competitors.append(ticker["ticker"])
            if len(top_n_competitors) >= n:
                break
        return top_n_competitors
    except json.JSONDecodeError:
        raise RuntimeError(f"Failed to parse Polygon.io API response as JSON")
    except Exception as e:
        raise RuntimeError(f"Error processing Polygon.io API response: {str(e)}")

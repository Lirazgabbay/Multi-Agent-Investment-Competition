"""
    LLM_get_qualitive.py - Functions for the qualitive Analyst agents
"""
# import yfinance as yf
import requests
import os
from dotenv import load_dotenv
import json

from database.api_utils import cached_api_request

def extract_business_info(symbol: str) -> dict:
    """
    Extracts strategic elements from company information using Polygon.io.

    Args:
        company_ticker (str): The stock ticker symbol.

    Returns:
        dict: A dictionary containing a business summary of the company.
    """
    response_text = cached_api_request(
        url=f"https://api.polygon.io/v3/reference/tickers/{symbol}",
        api_key_name="POLYGON_API_KEY",
        api_key_in_url=True,
        api_key_param="apiKey"
    )
    
    try:
        data = json.loads(response_text)
        result = {
            "businessDescription": data.get("results", {}).get("description", "No description available")
        }
        return json.dumps(result) 
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse API response as JSON"})
    except Exception as e:
        return json.dumps({"error": f"Error processing API response: {str(e)}"})


def get_company_data(symbol: str, limit: int = 2) -> dict:
    """
    Fetches recent news articles related to a company using Polygon.io API.

    Args:
        ticker (str): The stock ticker symbol.
        limit (int): The number of articles to retrieve (default: 2).

    Returns:
        dict: A dictionary containing news articles related to the company.
    """
    response_text = cached_api_request(
        url=f"https://api.polygon.io/v2/reference/news",
        api_key_name="POLYGON_API_KEY",
        api_key_in_url=True,
        api_key_param="apiKey",
        params={"ticker": symbol, "limit": limit}
    )

    try:
        data = json.loads(response_text)
        news = data.get("results", [])
        articles_info = {}

        for index, article in enumerate(news):
            articles_info[index + 1] = {
                "Title": article.get("title", "No title available"),
                "Description": article.get("description", "No description available"),
                "Published Date": article.get("published_utc", "No date available"),
                "Source": article.get("publisher", {}).get("name", "Unknown source"),
                "URL": article.get("article_url", "No URL available")
            }
        
        return json.dumps(articles_info)
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse API response as JSON"})
    except Exception as e:
        return json.dumps({"error": f"Error processing API response: {str(e)}"})

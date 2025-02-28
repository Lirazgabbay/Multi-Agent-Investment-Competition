"""
    LLM_get_qualitive.py - Functions for the qualitive Analyst agents
"""
# import yfinance as yf
import requests
import os
from dotenv import load_dotenv
import json

def extract_business_info(symbol: str) -> dict:
    """
    Extracts strategic elements from company information using Polygon.io.

    Args:
        company_ticker (str): The stock ticker symbol.

    Returns:
        dict: A dictionary containing a business summary of the company.
    """
    load_dotenv()
    api_key_polygon = os.getenv('POLYGON_API_KEY')
    url = f"https://api.polygon.io/v3/reference/tickers/{symbol}?apiKey={api_key_polygon}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        result= {
            "businessDescription": data.get("results", {}).get("description", "No description available")
        }
        return json.dumps(result) 
    
    return {"error": f"Failed to fetch company data. Status Code: {response.status_code}"}


def get_company_data(symbol: str, limit: int = 2) -> dict:
    """
    Fetches recent news articles related to a company using Polygon.io API.

    Args:
        ticker (str): The stock ticker symbol.
        limit (int): The number of articles to retrieve (default: 2).

    Returns:
        dict: A dictionary containing news articles related to the company.
    """
    load_dotenv()
    API_KEY_POLYGON = os.getenv('POLYGON_API_KEY')
    url = f"https://api.polygon.io/v2/reference/news?ticker={symbol}&limit={limit}&apiKey={API_KEY_POLYGON}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        news = response.json().get("results", [])
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
    
    return {"error": f"Failed to fetch news. Status Code: {response.status_code}"}
"""
    LLM_get_qualitive.py - Functions for the qualitive Analyst agents
"""
import yfinance as yf
import requests
import os
from dotenv import load_dotenv

def get_company_data(ticker):
    """
    Fetches API company data from Polygon.io API.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        dict: A dictionary containing news articles related to the company.

    """
    load_dotenv()
    api_key_polygon = os.getenv('POLYGON_API_KEY')
    news_url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}&limit=1&apiKey={api_key_polygon}"
    news = requests.get(news_url).json().get('results')
    articles_info = {}
    for index, news_dict in enumerate(news):
        title = news_dict['title']
        description = news_dict['description']
        insights = news_dict['insights']
        current_article = {'Title' : title, 'description': description, 'insights': insights}
        articles_info[index + 1] = current_article
    return articles_info


def extract_business_info(company_ticker):
   """
   Extract strategic elements from company info dictionary

    Args: 
        company_ticker (str): The stock ticker symbol.

    Returns:
        dict: A dictionary containing a business summary of the company.   
   """
   company_info = yf.Ticker(company_ticker).info
   business_info= {
       'longBusinessSummary': company_info.get('longBusinessSummary')
    }
   return business_info
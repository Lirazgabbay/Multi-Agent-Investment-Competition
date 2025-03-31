"""
judge_profit.py
functions for the profit judge of a stock in a defined period.
"""
import json
from datetime import datetime
import streamlit as st
from config.app_constants import START_YEAR, END_YEAR
from database.api_utils import cached_api_request

def get_historical_data(stock_symbol):
    """
    Get all historical data for a stock with caching using the api_utils system.
    
    Args:
        stock_symbol (str): the stock symbol to retrieve data for

    Returns:
        dict: the historical data for the stock  
    """
    response_text = cached_api_request(
        url=f"https://financialmodelingprep.com/api/v3/historical-price-full/{stock_symbol}",
        api_key_name="FMP_API_KEY",
        api_key_param="apikey",
        api_key_in_url=True,
        params={}
    )
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("Failed to parse API response as JSON")
        return None
    except Exception as e:
        print(f"Error processing API response: {str(e)}")
        return None
    

def find_closest_price(historical_data, target_date):
    """
    Find the closest available price to the target date.
    
    Args:
        historical_data (dict): the historical data for the stock
        target_date (str): the target date in YYYY-MM-DD format
    
    Returns:
        float: the closest price to the target date
    """
    if not historical_data or 'historical' not in historical_data:
        return None
    
    target = datetime.strptime(target_date, "%Y-%m-%d")
    closest_record = None
    min_days_diff = float('inf')
    
    for record in historical_data['historical']:
        record_date = datetime.strptime(record['date'], "%Y-%m-%d")
        days_diff = abs((target - record_date).days)
        
        if days_diff < min_days_diff:
            min_days_diff = days_diff
            closest_record = record
    
    if closest_record:
        return closest_record['close']
    
    return None


def judge_profit(stock: str, money_invested: float):
    """
    Judge the profit of a stock in a defined period.

    Args:
        stock: str: the stock symbol
        money_invested: float: the amount of money invested in the stock

    return: 
        float: the profit of the stock in the defined period
    """
    historical_data = get_historical_data(stock)
    
    if not historical_data:
        raise ValueError(f"Could not retrieve historical data for {stock}")
    
    start_year = st.session_state.get("START_YEAR", START_YEAR)
    end_year = st.session_state.get("END_YEAR", END_YEAR)
    start_date = f"{start_year}-12-31"
    end_date = f"{end_year}-12-31"
    
    start_stock_price = find_closest_price(historical_data, start_date)
    end_stock_price = find_closest_price(historical_data, end_date)

    if start_stock_price is None or end_stock_price is None:
        raise ValueError(f"Could not retrieve stock prices for {stock} around {start_date} or {end_date}")

    number_of_shares = int(money_invested / start_stock_price)    
    end_value = number_of_shares * end_stock_price
    profit = end_value - money_invested
    
    return profit

"""
judge_profit.py
functions for the profit judge of a stock in a defined period.
"""
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_constants import START_YEAR, END_YEAR
from dotenv import load_dotenv
from database.api_utils import cached_api_request

def get_historical_data(stock_symbol):
    """Get all historical data for a stock with caching using the api_utils system."""
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
    """Find the closest available price to the target date."""
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
        print(f"Found price from {closest_record['date']} (off by {min_days_diff} days)")
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
    
    start_date = f"{START_YEAR}-12-31"
    end_date = f"{END_YEAR}-12-31"
    
    start_stock_price = find_closest_price(historical_data, start_date)
    print(f"Start price for {stock} on {start_date}: ${start_stock_price}")
    
    end_stock_price = find_closest_price(historical_data, end_date)
    print(f"End price for {stock} on {end_date}: ${end_stock_price}")

    if start_stock_price is None or end_stock_price is None:
        raise ValueError(f"Could not retrieve stock prices for {stock} around {start_date} or {end_date}")
    
    number_of_shares = int(money_invested / start_stock_price)
    print(f"Number of shares purchased: {number_of_shares:.2f}")
    
    end_value = number_of_shares * end_stock_price
    profit = end_value - money_invested
    profit_percentage = (profit / money_invested) * 100
    
    print(f"Initial investment: ${money_invested:.2f}")
    print(f"Final value: ${end_value:.2f}")
    print(f"Profit: ${profit:.2f} ({profit_percentage:.2f}%)")
    
    return profit

if __name__ == "__main__":
    stock = "AAPL"
    money_invested = 10000
    
    try:
        profit = judge_profit(stock, money_invested)
        print(f"\nSummary: An investment of ${money_invested:.2f} in {stock} from {START_YEAR} to {END_YEAR}")
        print(f"would have yielded a profit of ${profit:.2f}")
    except Exception as e:
        print(f"Error calculating profit: {e}")

# Main changes:
# Previous: Made direct API calls to Financial Modeling Prep (FMP) with no caching mechanism
# New: Uses a caching system via cached_api_request to avoid repeated API calls for the same data
# added a new function get_historical_data to fetch all historical data for a stock with caching
# Having the full historical dataset allows for finding the closest available price when an exact date match isn't available
# Caching the entire historical dataset is more efficient than caching individual date queries

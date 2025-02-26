import os
from dotenv import load_dotenv
import requests

"""
    profit_multipliers.py - Functions to calculate profit multipliers for a company ticker symbol.
"""

def price_to_EBIT_ratio(symbol: str, year: int ) -> str:
    """
    Calculate the Price/EBIT ratio for a given company symbol using FMP API.

    Args:
        symbol (str): The stock ticker symbol (e.g., 'AAPL').
        yesr (int): The fiscal year for which to calculate the ratio.

    Returns:
        str: The Price/EBIT ratio, or None if data is unavailable.
    """
    load_dotenv()
    api_key = os.getenv('FMP_API_KEY')
    ebit = None 
    market_cap = None
    # Fetch market capitalization
    # https://financialmodelingprep.com/api/v3/historical-market-capitalization/AAPL?limit=500&from=2023-10-10&to=2023-12-10
    market_cap_url = f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{symbol}?limit=1&from={year}-01-01&to={year}-12-31&apikey={api_key}"
    market_cap_response = requests.get(market_cap_url)
    if market_cap_response.status_code == 200:
        market_cap_response = market_cap_response.json()
        market_cap = market_cap_response[0].get('marketCap')
    else:
        print(f"Failed to fetch market capitalization data. Status Code: {market_cap_response.status_code}")
        return None

    # Fetch EBIT
    income_statement_url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?limit=10&period=annual&apikey={api_key}"
    income_statement_response = requests.get(income_statement_url)
    if income_statement_response.status_code == 200:
        income_statement_data = income_statement_response.json()
        for dict in income_statement_data:
            if str(dict['calendarYear']) == str(year):
                ebit = dict['operatingIncome']
                break

    # Calculate Price/EBIT ratio
    if market_cap is not None and ebit is not None and ebit != 0:
        price_ebit_ratio = market_cap / ebit
        return str(price_ebit_ratio)
    else:
        print("Insufficient data to calculate Price/EBIT ratio.")
        return None


def ratios(symbol: str, year:int) -> dict:  
    """
    return all the ratios for a given company symbol: 
    - Price/Earnings ratio
    - Price/Book ratio
    - PEG ratio
    - Price/Sales ratio

    Args:
        symbol (str): Company ticker symbol (e.g., 'AAPL')
        
    Returns:
        float | None: The Price/Earnings ratio or None if data is unavailable
    """
    load_dotenv()
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("API key not found. Please set the FMP_API_KEY environment variable.")
        return None

    url = f"https://financialmodelingprep.com/api/v3/ratios/{symbol}?period=annual&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data:
            for entry in data:
                if str(entry.get('calendarYear') == str(year)):
                    price_to_earning = entry.get("priceEarningsRatio")
                    price_to_book = entry.get("priceToBookRatio")
                    price_earnings_to_growth = entry.get("priceEarningsToGrowthRatio")
                    price_to_sales_ratio = entry.get("priceToSalesRatio")
                    return {
                        "price_to_earning": price_to_earning,
                        "price_to_book": price_to_book,
                        "price_earnings_to_growth": price_earnings_to_growth,
                        "price_to_sales_ratio": price_to_sales_ratio
                    }
            print(f"No data returned for {symbol}.")
            return None
    else:
        print(f"Failed to fetch data. Status Code: {response.status_code}")
        return None

# def price_sales_ratio(symbol: str, year: int) -> float:
#     """
#     Fetches the Price-to-Sales (P/S) ratio for the given company symbol and year using the FMP API.

#     Args:
#         symbol (str): Company ticker symbol (e.g., 'AAPL').
#         year (int): The fiscal year for which to retrieve the P/S ratio.

#     Returns:
#         float | None: Price-to-Sales ratio, or None if data is not available.
#     """
#     load_dotenv()
#     api_key = os.getenv('FMP_API_KEY')
#     if not api_key:
#         print("API key not found. Please set the FMP_API_KEY environment variable.")
#         return None

#     url = f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}?apikey={api_key}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an error for HTTP failures
#         data = response.json()
#         if isinstance(data, list):
#             # Iterate through the response to find the matching year
#             for entry in data:
#                 if str(entry.get("calendarYear")) == str(year):
#                     return entry.get("priceToSalesRatio", None)
        
#         print(f"No data found for {symbol} in {year}.")
#         return None

#     except (requests.RequestException, KeyError, TypeError) as e:
#         print(f"Error fetching Price-to-Sales ratio: {e}")
#         return None

# def price_to_book_value_ratio(symbol: str, year: int) -> float:
#     """
#     Fetches the Price-to-Book (P/B) ratio for the given company symbol using FMP API.

#     Args:
#         symbol (str): Company ticker symbol (e.g., 'AAPL').
#         year (int): The fiscal year for which to retrieve the P/B ratio.

#     Returns:
#         float: The Price/Book Value ratio, or None if data is unavailable.
#     """
#     load_dotenv()
#     api_key = os.getenv('FMP_API_KEY')
#     if not api_key:
#         print("API key not found. Please set the FMP_API_KEY environment variable.")
#         return None

#     url = f"https://financialmodelingprep.com/api/v3/ratios/{symbol}?period=annual&apikey={api_key}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         if data:
#             for entry in data:
#                 if str(entry.get('calendarYear')) == str(year):
#                     pb_ratio = entry.get("priceToBookRatio")
#                     return pb_ratio
#             print(f"No data returned for {symbol}.")
#             return None
#     else:
#         print(f"Failed to fetch data. Status Code: {response.status_code}")
#         return None
    
# def price_to_earnings_ratio(symbol: str, year:int):
#     """
#     Calculate Price/Earnings ratio (Market Cap divided by Net Income).
    
#     Args:
#         symbol (str): Company ticker symbol (e.g., 'AAPL')
        
#     Returns:
#         float | None: The Price/Earnings ratio or None if data is unavailable
#     """
#     load_dotenv()
#     api_key = os.getenv('FMP_API_KEY')
#     if not api_key:
#         print("API key not found. Please set the FMP_API_KEY environment variable.")
#         return None

#     url = f"https://financialmodelingprep.com/api/v3/ratios/{symbol}?period=annual&apikey={api_key}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         if data:
#             for entry in data:
#                 if str(entry.get('calendarYear') == str(year)):
#                     pb_ratio = entry.get("priceEarningsRatio")
                    
#                     return pb_ratio
#             print(f"No data returned for {symbol}.")
#             return None
#     else:
#         print(f"Failed to fetch data. Status Code: {response.status_code}")
#         return None

# def price_earnings_to_growth_ratio(symbol: str, year:int) -> float:
#     """
#     Calculate PEG ratio (Price/Earnings ratio divided by Annual EPS Growth rate).
#     PEG = (P/E) / (EPS Growth Rate)
    
#     Args:
#         symbol (str): Company ticker symbol (e.g., 'AAPL')
#         year (int): The year for which the PEG ratio is calculated
        
#     Returns:
#         float | None: The PEG ratio or None if data is unavailable
#     """
    
#     load_dotenv()
#     api_key = os.getenv('FMP_API_KEY')
#     if not api_key:
#         print("API key not found. Please set the FMP_API_KEY environment variable.")
#         return None

#     url = f"https://financialmodelingprep.com/api/v3/ratios/{symbol}?period=annual&apikey={api_key}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         if data:
#             for entry in data:
#                 if str(entry.get('calendarYear') == str(year)):
#                     pb_ratio = entry.get("priceEarningsToGrowthRatio")
#                     return pb_ratio
#             print(f"No data returned for {symbol}.")
#             return None
#     else:
#         print(f"Failed to fetch data. Status Code: {response.status_code}")
#         return None

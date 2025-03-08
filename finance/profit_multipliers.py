"""
profit_multipliers.py - Functions to calculate profit multipliers for a company ticker symbol.
"""
import json
from database.api_utils import cached_api_request


def price_to_EBIT_ratio(symbol: str, year: int ) -> str:
    """
    Calculate the Price/EBIT ratio for a given company symbol using FMP API.

    Args:
        symbol (str): The stock ticker symbol (e.g., 'AAPL').
        yesr (int): The fiscal year for which to calculate the ratio.

    Returns:
        str: The Price/EBIT ratio, or None if data is unavailable.
    """
    ebit = None 
    market_cap = None
    # Fetch market capitalization
    market_cap_response_text = cached_api_request(
        url=f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{symbol}",
        api_key_name="FMP_API_KEY",
        api_key_param="apikey",
        api_key_in_url=True,
        params={
            "limit": 1,
            "from": f"{year}-01-01",
            "to": f"{year}-12-31"
        }
    )
    
    try:
        market_cap_data = json.loads(market_cap_response_text)
        if market_cap_data and len(market_cap_data) > 0:
            market_cap = market_cap_data[0].get('marketCap')
    except json.JSONDecodeError:
        print("Failed to parse market cap API response as JSON")
        return None
    except Exception as e:
        print(f"Error processing market cap API response: {str(e)}")
        return None

    # Fetch EBIT
    income_statement_response_text = cached_api_request(
        url=f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}",
        api_key_name="FMP_API_KEY",
        api_key_param="apikey",
        api_key_in_url=True,
        params={
            "limit": 10,
            "period": "annual"
        }
    )
    
    try:
        income_statement_data = json.loads(income_statement_response_text)
        for dict in income_statement_data:
            if str(dict['calendarYear']) == str(year):
                ebit = dict['operatingIncome']
                break
    except json.JSONDecodeError:
        print("Failed to parse income statement API response as JSON")
        return None
    except Exception as e:
        print(f"Error processing income statement API response: {str(e)}")
        return None

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
            for entry in data:
                if str(entry.get('calendarYear')) == str(year):
                    price_to_earning = entry.get("priceEarningsRatio")
                    price_to_book = entry.get("priceToBookRatio")
                    price_earnings_to_growth = entry.get("priceEarningsToGrowthRatio")
                    price_to_sales_ratio = entry.get("priceToSalesRatio")
                    result = {
                        "price_to_earning": price_to_earning,
                        "price_to_book": price_to_book,
                        "price_earnings_to_growth": price_earnings_to_growth,
                        "price_to_sales_ratio": price_to_sales_ratio
                    }
                    return json.dumps(result)
            print(f"No data returned for {symbol} in year {year}.")
            return None
    except json.JSONDecodeError:
        print("Failed to parse API response as JSON")
        return None
    except Exception as e:
        print(f"Error processing API response: {str(e)}")
        return None

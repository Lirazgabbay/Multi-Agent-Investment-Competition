"""
    profit_margin.py - Functions to calculate profit margins for a company ticker symbol.
"""
import json
from database.api_utils import cached_api_request

def fetch_income_statement(symbol: str, year: int) -> dict: 
    """
    Fetches the income statement data for the given company ticker and year using the FMP API.

    Args:
        symbol (str): The stock ticker symbol
        year (int): The year for which the income statement data is requested

    Returns:
        dict: dictionary containing the income statement data for the given year
    """
    response_text = cached_api_request(
        url=f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}",
        api_key_name="FMP_API_KEY",
        api_key_param="apikey",
        api_key_in_url=True
    )
    try:
        data = json.loads(response_text)
        for dict in data:
            if dict['calendarYear'] == str(year):
                return dict
        return None
    except json.JSONDecodeError:
        print("Failed to parse API response as JSON")
        return None
    except Exception as e:
        print(f"Error processing API response: {str(e)}")
        return None


def calculate_profit_margins(symbol: str, year: int) -> dict:
    """
    Calculates the profit margins for the given company ticker and year using the FMP API.

    Args:
        symbol (str): The stock ticker symbol
        year (int): The year for which the profit margins are calculated

    Returns:
        dict: dictionary containing the profit margins for the given year
    """
    data = fetch_income_statement(symbol, year)
    if data:
        revenue = data.get('revenue')
        gross_profit = data.get('grossProfit')
        operating_income = data.get('operatingIncome')
        net_income = data.get('netIncome')

        if revenue:
            gross_margin = (gross_profit / revenue) * 100 if gross_profit else None
            operating_margin = (operating_income / revenue) * 100 if operating_income else None
            net_margin = (net_income / revenue) * 100 if net_income else None

            result = {
                'Gross Profit Margin (%)': gross_margin,
                'Operating Profit Margin (%)': operating_margin,
                'Net Profit Margin (%)': net_margin
            }
            return json.dumps(result)
        else:
            return {"error": "Revenue is zero or undefined."}
    return {"error": "No data available for the given symbol and year."}

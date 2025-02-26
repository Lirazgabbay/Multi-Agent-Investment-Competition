"""
    profit_margin.py - Functions to calculate profit margins for a company ticker symbol.
"""

import os
from dotenv import load_dotenv
import requests

def fetch_income_statement(symbol: str, year: int) -> dict: 
    load_dotenv()
    api_key = os.getenv('FMP_API_KEY')
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for dict in data:
            if dict['calendarYear'] == str(year):
                return dict
    return None


# def calculate_profit_margins(symbol: str, year: int) -> dict:
#     data = fetch_income_statement(symbol, year)
#     if data:
#         revenue = data.get('revenue')
#         gross_profit = data.get('grossProfit')
#         operating_income = data.get('operatingIncome')
#         net_income = data.get('netIncome')

#         if revenue:
#             gross_margin = (gross_profit / revenue) * 100 if gross_profit else None
#             operating_margin = (operating_income / revenue) * 100 if operating_income else None
#             net_margin = (net_income / revenue) * 100 if net_income else None

#             return {
#                 'Gross Profit Margin (%)': gross_margin,
#                 'Operating Profit Margin (%)': operating_margin,
#                 'Net Profit Margin (%)': net_margin
#             }
#     return None

def calculate_profit_margins(symbol: str, year: int) -> dict:
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

            return {
                'Gross Profit Margin (%)': gross_margin,
                'Operating Profit Margin (%)': operating_margin,
                'Net Profit Margin (%)': net_margin
            }
        else:
            return {"error": "Revenue is zero or undefined."}
    return {"error": "No data available for the given symbol and year."}

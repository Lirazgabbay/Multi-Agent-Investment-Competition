"""
    balance_sheet_helpers.py - Helper functions to fetch balance sheet data for a company
"""
import pandas as pd
import yfinance as yf

def get_assets(ticker_symbol: str, year: str) -> float:
    """
    Get the assets of a company for a specific year.

    Parameters:
        ticker_symbol (str): The ticker symbol of the company (e.g., "AAPL" for Apple).
        year (str): The year for which to fetch the assets.

    Returns:
        current_assets (float): the Current assets of the company for the specified year.
    """
    ticker = yf.Ticker(ticker_symbol)
    try:
        balance_sheet = ticker.balance_sheet
        # Convert column headers to a list and look for the closest year
        available_years = [col[:4] for col in balance_sheet.columns.astype(str)]
        if year in available_years:
            year_column = balance_sheet.columns[available_years.index(year)]
            if "Current Assets" in balance_sheet.index:
                current_assets = balance_sheet.loc["Current Assets", year_column]
                return str(current_assets)
        return None
    
    except Exception as e:
        return None

def get_liabilities(ticker_symbol: str, year: str) -> float:
    """
    Get the current liabilities of a company for a specific year.

    Args:
        ticker_symbol (str): The ticker symbol of the company (e.g., "AAPL" for Apple).
        year (str): The year for which to fetch the liabilities.

    Returns:
        current_liabilities (float): the current liabilities of the company for the specified year.
    """
    ticker = yf.Ticker(ticker_symbol)
    try:
        balance_sheet = ticker.balance_sheet
        available_years = [col[:4] for col in balance_sheet.columns.astype(str)]
        if year in available_years:
            year_column = balance_sheet.columns[available_years.index(year)]
            # Check if "Total Liabilities Net Minority Interest" exists in the balance sheet
            if "Current Liabilities" in balance_sheet.index:
                current_liabilities = balance_sheet.loc["Current Liabilities", year_column]
                return str(current_liabilities) 
        return None
    except Exception as e:
        return None


def get_inventory(ticker_symbol: str, year: str) -> float:
    """
    Get the inventory value of a company for a specific year.

    Args:
        ticker_symbol (str): The ticker symbol of the company (e.g., "AAPL" for Apple).
        year (str): The year for which to fetch the inventory value.

    Returns:
        inventory_value (float): inventory value or None if data is unavailable.
    """
    ticker = yf.Ticker(ticker_symbol)
    try:
        balance_sheet = ticker.balance_sheet
        available_years = [col[:4] for col in balance_sheet.columns.astype(str)]
        
        if year in available_years:
            year_column = balance_sheet.columns[available_years.index(year)]
            # Check if "Inventory" exists in the balance sheet
            if "Inventory" in balance_sheet.index:
                inventory_value = balance_sheet.loc["Inventory", year_column]
                return str(inventory_value)
          
        return None
    except Exception as e:
        return None
    

def print_full_balance_sheet(ticker_symbol: str):
    """
    Print the complete balance sheet with all rows and columns visible.
    
    Args:
        ticker_symbol (str): The ticker symbol of the company (e.g., "AAPL" for Apple)
    """
    # Set pandas display options to show all rows and columns
    pd.set_option('display.max_rows', None)  # Show all rows
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', None)  # Auto-detect display width
    pd.set_option('display.max_colwidth', None)  # Show full content of each cell
    
    ticker = yf.Ticker(ticker_symbol)
    try:
        balance_sheet = ticker.balance_sheet
        print(f"\nFull Balance Sheet for {ticker_symbol}")
        print("-" * 50)
        print(balance_sheet)
        
    except Exception as e:
        print(f"Error fetching balance sheet for {ticker_symbol}: {e}")

def save_balance_sheet_to_csv(ticker_symbol: str):
    """
    Save the complete balance sheet to a CSV file.
    
    Args:
        ticker_symbol (str): The ticker symbol of the company (e.g., "AAPL" for Apple)
    """
    ticker = yf.Ticker(ticker_symbol)
    try:
        balance_sheet = ticker.balance_sheet
        filename = f"{ticker_symbol}_balance_sheet.csv"
        balance_sheet.to_csv(filename)
        print(f"Balance sheet saved to {filename}")
        
    except Exception as e:
        print(f"Error saving balance sheet for {ticker_symbol}: {e}")

# save_balance_sheet_to_csv("GOOG") 
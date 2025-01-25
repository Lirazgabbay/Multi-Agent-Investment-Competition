"""
    profit_margin.py - Functions to calculate profit margins for a company ticker symbol.
"""
import yfinance as yf

def gross_profit_margin(symbol: str):
   """
   Calculate Gross Profit Margin (Gross Profit / Revenue)
   Shows profitability after considering cost of goods sold (COGS).
   
   Args:
       symbol (str): Company ticker symbol (e.g., 'AAPL')
       
   Returns:
       float | None: Gross margin as a decimal or None if unavailable
   """
   ticker = yf.Ticker(symbol)
   try:
       # Try to get gross margin directly
       gross_margin = ticker.info.get('grossMargins')
       if gross_margin is not None:
           return str(gross_margin)
           
       # If not available, calculate manually
       gross_profit = ticker.info.get('grossProfits')
       total_revenue = ticker.info.get('totalRevenue')
       
       if gross_profit is None or total_revenue is None or total_revenue == 0:
           return None
           
       return str(gross_profit / total_revenue)
       
   except (KeyError, TypeError, ZeroDivisionError):
       return None
   

def operational_profit_margin(symbol: str):
    """
    Calculate Operating Profit Margin (Operating Income / Revenue).
    Shows how much profit a company makes from its core business operations.
    
    Args:
        symbol (str): Company ticker symbol (e.g., 'AAPL')
        
    Returns:
        float | None: Operating profit margin as a decimal or None if data is unavailable
    """
    ticker = yf.Ticker(symbol)
    try:
        # Try to get operating margin directly
        op_margin = ticker.info.get('operatingMargins')
        if op_margin is not None:
            return str(op_margin)
            
        # If not available, calculate manually
        operating_income = ticker.info.get('operatingIncome')
        total_revenue = ticker.info.get('totalRevenue')
        
        if operating_income is None or total_revenue is None or total_revenue == 0:
            return None
            
        return str(operating_income / total_revenue)
        
    except (KeyError, TypeError, ZeroDivisionError):
        return None


def net_profit_margin(symbol: str):
    """
    Calculate Net Profit Margin (Net Income / Revenue)
    Shows final profitability after all expenses, interest, and taxes.
    
    Args:
        symbol (str): Company ticker symbol (e.g., 'AAPL')
        
    Returns:
        float | None: Net profit margin as a decimal or None if unavailable
    """
    ticker = yf.Ticker(symbol)
    try:
        # Try to get net margin directly
        net_margin = ticker.info.get('profitMargins')
        if net_margin is not None:
            return net_margin
            
        # If not available, calculate manually
        net_income = ticker.info.get('netIncomeToCommon')
        total_revenue = ticker.info.get('totalRevenue')
        
        if net_income is None or total_revenue is None or total_revenue == 0:
            return None
            
        return str(net_income / total_revenue)
        
    except (KeyError, TypeError, ZeroDivisionError):
        return None
import yfinance as yf
"""
    profit_multipliers.py - Functions to calculate profit multipliers for a company ticker symbol.
"""
def price_sales_ratio(symbol: str):
    """
    Calculate Price/Sales ratio (Price divided by Total Revenue).
    Args:
        symbol (str): Company ticker symbol (e.g., 'AAPL')
    Returns:
        float | None: Price/Sales ratio or None if data is not available
    """
    ticker = yf.Ticker(symbol) 
    try:
        price = ticker.info.get("marketCap", None)
        if price is None:
            return None

        financials = ticker.financials
        if "Total Revenue" not in financials.index:
            return None
        
        total_revenue = financials.loc["Total Revenue"].iloc[0]
        if total_revenue == 0:
            return None
        
        price_sales = price / total_revenue
        return str(price_sales)
    except Exception as e:
        print(f"Error calculating Price-to-Sales ratio for {symbol}: {e}")
        return None


def price_to_EBIT_ratio(symbol: str):
    """
    Calculate Price/EBIT ratio (Price divided by Earnings Before Interest and Taxes).
    
    Args:
        symbol (str): Company ticker symbol (e.g., 'AAPL')
        
    Returns:
        float | None: The Price/EBIT ratio or None if data is unavailable
    """
    ticker = yf.Ticker(symbol)
    try:
        ebit = ticker.info['ebitda'] 
        price = ticker.info['marketCap']
        
        if ebit is None or ebit == 0:
            return None
            
        return str(price / ebit)
        
    except (KeyError, TypeError, ZeroDivisionError):
        return None
    

def price_to_book_value_ratio(symbol: str):
    """
    Calculate Price/Book Value ratio (Market Cap divided by Book Value).
    
    Args:
        symbol (str): Company ticker symbol (e.g., 'AAPL')
        
    Returns:
        float | None: The Price/Book Value ratio or None if data is unavailable
    """
    ticker = yf.Ticker(symbol)
    try:
        # First try to get P/B directly from yfinance
        pb_ratio = ticker.info.get('priceToBook')
        if pb_ratio is not None:
            return str(pb_ratio)
            
        # If priceToBook is not available, calculate it manually
        market_cap = ticker.info.get('marketCap')
        book_value = ticker.info.get('bookValue')
        
        if market_cap is None or book_value is None or book_value == 0:
            return None
            
        return str(market_cap / book_value)
        
    except (KeyError, TypeError, ZeroDivisionError):
        return None
    
    
def price_to_earnings_ratio(symbol: str):
    """
    Calculate Price/Earnings ratio (Market Cap divided by Net Income).
    
    Args:
        symbol (str): Company ticker symbol (e.g., 'AAPL')
        
    Returns:
        float | None: The Price/Earnings ratio or None if data is unavailable
    """
    ticker = yf.Ticker(symbol)
    try:
        # First try to get P/E directly from yfinance
        pe_ratio = ticker.info.get('trailingPE')
        if pe_ratio is not None:
            return pe_ratio
            
        # If not available, calculate manually
        market_cap = ticker.info.get('marketCap')
        net_income = ticker.info.get('netIncomeToCommon')
        
        if market_cap is None or net_income is None or net_income == 0:
            return None
            
        return str(market_cap / net_income)
        
    except (KeyError, TypeError, ZeroDivisionError):
        return None
        
    
def price_earnings_to_growth_ratio(symbol: str):
    """
    Calculate PEG ratio (Price/Earnings ratio divided by Annual EPS Growth rate).
    PEG = (P/E) / (EPS Growth Rate)
    
    Args:
        symbol (str): Company ticker symbol (e.g., 'AAPL')
        
    Returns:
        float | None: The PEG ratio or None if data is unavailable
    """
    ticker = yf.Ticker(symbol)
    try:
        # Try to get PEG ratio directly from yfinance
        peg_ratio = ticker.info.get('pegRatio')
        if peg_ratio is not None:
            return peg_ratio
            
        # If not available, calculate manually
        pe_ratio = price_to_earnings_ratio(symbol)
        growth_rate = ticker.info.get('earningsGrowth')
        
        if pe_ratio is None or growth_rate is None or growth_rate == 0:
            return None
            
        # Convert growth rate to percentage
        if abs(growth_rate) > 1:
            growth_rate = growth_rate / 100
            
        return str(pe_ratio / growth_rate)
        
    except (KeyError, TypeError, ZeroDivisionError):
        return None

# def explore_ticker_info(symbol: str):
#     """
#     Print all available fields in ticker.info for a given symbol.
    
#     Args:
#         symbol (str): Company ticker symbol (e.g., 'AAPL')
#     """
#     ticker = yf.Ticker(symbol)
#     try:
#         info = ticker.info
#         print(f"\nAvailable fields for {symbol}:")
#         print("-" * 50)
        
#         # Print all keys and their values
#         for key, value in sorted(info.items()):
#             print(f"{key}: {value}")
            
#     except Exception as e:
#         print(f"Error fetching info for {symbol}: {e}")

# Example usage
# explore_ticker_info("AAPL")
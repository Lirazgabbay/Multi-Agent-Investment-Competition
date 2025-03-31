"""
visualization_functions.py (Fixed)
Simple visualization functions using matplotlib
"""
import matplotlib.pyplot as plt
import numpy as np
import json
import base64
from io import BytesIO
from config.app_constants import END_YEAR, START_YEAR
from finance.profit_margin import calculate_profit_margins
from finance.profit_multipliers import price_to_EBIT_ratio, ratios
from finance.LLM_get_financial import get_related_companies

def plot_company_comparison(stock_symbol, competitor=None):
    """
    Creates a visualization comparing key financial metrics between a company and its competitor.
    
    Args:
        stock_symbol (str): The main company ticker symbol
        competitor (str, optional): The competitor ticker symbol. If None, finds a related company.
    
    Returns:
        str: Base64 encoded image string
    """
    # Find competitor if not provided
    if not competitor:
        related = get_related_companies(stock_symbol, n=1)
        competitor = related[0] if related else "MSFT"  # Default to Microsoft if no competitor found
    
    # Get financial data for comparison
    years = [year for year in range(START_YEAR, END_YEAR + 1)]
    
    # Get margin data
    company_margins = {}
    competitor_margins = {}
    
    for year in years:
        try:
            # Parse the JSON string returned by calculate_profit_margins
            company_data = json.loads(calculate_profit_margins(stock_symbol, year))
            competitor_data = json.loads(calculate_profit_margins(competitor, year))
            
            company_margins[year] = company_data
            competitor_margins[year] = competitor_data
        except Exception as e:
            print(f"Error getting margins for {year}: {str(e)}")
            continue
    
    # Get price to EBIT and other ratios
    company_pebit = {}
    competitor_pebit = {}
    company_other_ratios = {}
    competitor_other_ratios = {}
    
    for year in years:
        try:
            company_pebit[year] = price_to_EBIT_ratio(stock_symbol, year)
            competitor_pebit[year] = price_to_EBIT_ratio(competitor, year)
            
            # Parse the JSON string returned by ratios
            company_other_ratios[year] = json.loads(ratios(stock_symbol, year))
            competitor_other_ratios[year] = json.loads(ratios(competitor, year))
        except Exception as e:
            print(f"Error getting ratios for {year}: {str(e)}")
            continue
    
    # Create comparison chart
    fig, axes = plt.subplots(2, 1, figsize=(10, 12))
    
    # Determine which years have data
    available_years = [year for year in years if year in company_margins and year in competitor_margins]
    
    if not available_years:
        # If no data is available, create an error message chart
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis('off')
        ax.text(0.5, 0.5, f"No financial data available for comparison between {stock_symbol} and {competitor}.",
                fontsize=12, ha='center', va='center', wrap=True)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{img_str}"
    
    # Use the most recent year with available data
    latest_year = max(available_years)
    
    # Plot margins
    margin_labels = []
    company_margin_values = []
    competitor_margin_values = []
    
    # Safely extract margin values if they exist
    for label, key in [
        ('Gross Margin', 'Gross Profit Margin (%)'), 
        ('Operating Margin', 'Operating Profit Margin (%)'), 
        ('Net Margin', 'Net Profit Margin (%)')
    ]:
        if key in company_margins[latest_year] and key in competitor_margins[latest_year]:
            if company_margins[latest_year][key] is not None and competitor_margins[latest_year][key] is not None:
                margin_labels.append(label)
                company_margin_values.append(company_margins[latest_year][key])
                competitor_margin_values.append(competitor_margins[latest_year][key])
    
    # Create bar chart for margins if we have data
    if margin_labels:
        x = np.arange(len(margin_labels))
        width = 0.35
        
        axes[0].bar(x - width/2, company_margin_values, width, label=stock_symbol)
        axes[0].bar(x + width/2, competitor_margin_values, width, label=competitor)
        
        axes[0].set_ylabel('Percentage (%)')
        axes[0].set_title(f'Profit Margins Comparison ({latest_year})')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(margin_labels)
        axes[0].legend()
    else:
        axes[0].axis('off')
        axes[0].text(0.5, 0.5, "No margin data available for comparison", 
                   fontsize=12, ha='center', va='center')
    
    # Plot valuation metrics if available
    if latest_year in company_other_ratios and latest_year in competitor_other_ratios:
        # Check if we have valid data for both companies
        valuation_labels = []
        company_valuation_values = []
        competitor_valuation_values = []
        
        # Safely extract valuation metrics if they exist
        for label, c_key, p_key in [
            ('P/E Ratio', 'price_to_earning', None),
            ('P/S Ratio', 'price_to_sales_ratio', None), 
            ('P/B Ratio', 'price_to_book', None),
            ('P/EBIT Ratio', None, 'pebit')
        ]:
            # Handle the special case for P/EBIT ratio which comes from a different source
            if p_key == 'pebit':
                if latest_year in company_pebit and latest_year in competitor_pebit:
                    c_val = company_pebit[latest_year]
                    comp_val = competitor_pebit[latest_year]
                    if c_val and comp_val:
                        valuation_labels.append(label)
                        company_valuation_values.append(float(c_val))
                        competitor_valuation_values.append(float(comp_val))
            # Handle regular valuation metrics from ratios
            elif c_key:
                c_val = company_other_ratios[latest_year].get(c_key)
                comp_val = competitor_other_ratios[latest_year].get(c_key)
                if c_val and comp_val:
                    valuation_labels.append(label)
                    company_valuation_values.append(float(c_val))
                    competitor_valuation_values.append(float(comp_val))
        
        # Create bar chart for valuation metrics if we have data
        if valuation_labels:
            x = np.arange(len(valuation_labels))
            width = 0.35
            
            axes[1].bar(x - width/2, company_valuation_values, width, label=stock_symbol)
            axes[1].bar(x + width/2, competitor_valuation_values, width, label=competitor)
            
            axes[1].set_ylabel('Ratio')
            axes[1].set_title(f'Valuation Metrics Comparison ({latest_year})')
            axes[1].set_xticks(x)
            axes[1].set_xticklabels(valuation_labels)
            axes[1].legend()
        else:
            axes[1].axis('off')
            axes[1].text(0.5, 0.5, "No valuation metrics available for comparison", 
                       fontsize=12, ha='center', va='center')
    else:
        axes[1].axis('off')
        axes[1].text(0.5, 0.5, "No valuation data available for comparison", 
                   fontsize=12, ha='center', va='center')
    
    plt.tight_layout()
    
    # Convert plot to base64-encoded image
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    
    return f"data:image/png;base64,{img_str}"


def plot_qualitative_summary(stock_symbol, business_info):
    """
    Creates a visual summary of key qualitative factors for a company.
    
    Args:
        stock_symbol (str): The company ticker symbol
        business_info (str): Business description JSON string
        
    Returns:
        str: Base64 encoded image string
    """
    try:
        # Parse business info
        info = json.loads(business_info)
        description = info.get("businessDescription", "No description available")
        
        # Extract key points (simplified approach)
        sentences = description.split('.')
        key_points = [s.strip() for s in sentences if len(s.strip()) > 20][:5]  # Get up to 5 substantial sentences
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Hide axes
        ax.axis('off')
        
        # Add company name as title
        ax.text(0.5, 0.95, f"{stock_symbol} Key Business Factors", fontsize=18, ha='center', weight='bold')
        
        # Add key points as bullet points
        y_pos = 0.85
        for i, point in enumerate(key_points):
            # Limit point length
            if len(point) > 100:
                point = point[:97] + "..."
                
            ax.text(0.1, y_pos, f"• {point}", fontsize=12, ha='left', va='top', wrap=True)
            y_pos -= 0.15
            
            # Only show 5 points maximum
            if i >= 4:
                break
        
        # Convert plot to base64-encoded image
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        # If there's an error, create a simple error chart
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis('off')
        ax.text(0.5, 0.5, f"Error creating qualitative summary: {str(e)}", 
                fontsize=12, ha='center', va='center', wrap=True)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{img_str}"
    

# import yfinance as yf
# import matplotlib.pyplot as plt
# # from autogen.visualize import Visualize


# def fetch_and_visualize_stock_data(stock_symbol: str, period: str = "1mo"):
#     """
#     Fetches stock data using yfinance and visualizes it using matplotlib.

#     Args:
#         stock_symbol (str): The stock symbol (e.g., "AAPL").
#         period (str): The time period for the data (e.g., "1mo", "1y").

#     Returns:
#         str: A message indicating success or failure.
#     """
#     try:
#         # Fetch stock data
#         stock_data = yf.Ticker(stock_symbol)
#         history = stock_data.history(period=period)

#         # Check if data is available
#         if history.empty:
#             return f"No data found for stock symbol: {stock_symbol}"

#         # Plot the stock data
#         plt.figure(figsize=(10, 5))
#         plt.plot(history['Close'], label='Close Price')
#         plt.title(f"{stock_symbol} Stock Price ({period})")
#         plt.xlabel("Date")
#         plt.ylabel("Price (USD)")
#         plt.legend()
#         plt.grid()
#         plt.show()

#         return f"Stock data for {stock_symbol} fetched and visualized successfully."
#     except Exception as e:
#         return f"Error: {str(e)}"
    


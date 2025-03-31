"""
visualization_tools.py (Image-only)
Simple wrapper functions for visualization that can be used by AutoGen agents
"""
from finance.LLM_get_qualitative import extract_business_info
from utils.visualization_functions import plot_company_comparison, plot_qualitative_summary
from typing import Optional

def generate_competitive_analysis(stock_symbol: str) -> str:
    """
    Creates a competitive analysis visualization for a company.
    
    Args:
        stock_symbol (str): The stock ticker symbol
        
    Returns:
        str: Markdown with embedded visualization
    """
    try:
        # Generate the comparison chart
        chart_url = plot_company_comparison(stock_symbol)
        
        # Return only the image in markdown format
        return f"![Competitive Analysis for {stock_symbol}]({chart_url})"
    except Exception as e:
        return f"Error generating competitive analysis: {str(e)}"
    

def generate_qualitative_summary(stock_symbol: str) -> str:
    """
    Creates a qualitative summary visualization for a company.
    
    Args:
        stock_symbol (str): The stock ticker symbol
        
    Returns:
        str: Markdown with embedded visualization
    """
    try:
        # Get business description
        business_info = extract_business_info(stock_symbol)
        
        # Generate the qualitative summary chart
        chart_url = plot_qualitative_summary(stock_symbol, business_info)
        
        # Return only the image in markdown format
        return f"![Qualitative Summary for {stock_symbol}]({chart_url})"
    except Exception as e:
        return f"Error generating qualitative summary: {str(e)}"
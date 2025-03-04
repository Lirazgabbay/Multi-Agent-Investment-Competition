"""
test_finance_functions.py
This module contains the unit tests for the finance functions.
validate financial functions. 
It ensures that functions analyzing financial and qualitative data work correctly by
mocking external dependencies to provide controlled test conditions.
"""
import json
import pytest
from finance.agents_functions import historical_func, competative_func, qualitative_func
from finance.profit_margin import calculate_profit_margins
from finance.profit_multipliers import price_to_EBIT_ratio, ratios
from finance.LLM_get_financial import get_related_companies, quick_ratio
from finance.LLM_get_qualitative import extract_business_info, get_company_data
from unittest.mock import Mock


@pytest.fixture
def mock_requests_get(mocker):
    """Fixture to mock requests.get"""
    return mocker.patch('requests.get')


@pytest.fixture
def mock_fetch_income_statement(mocker):
    """Fixture to mock fetch_income_statement"""
    return mocker.patch('finance.profit_margin.fetch_income_statement')


def test_historical_func():
    """Test the historical_func function with valid input data to ensure it returns the expected results.""" 
    symbols = ["AAPL", "GOOGL"]
    years = [2022, 2023]
    result = historical_func(symbols, years)
    assert isinstance(result, dict)
    assert "AAPL" in result and "GOOGL" in result
    assert all(year in result["AAPL"] for year in years)
    assert all("profit_margins" in result["AAPL"][year] for year in years)


def test_historical_func_empty():
    """Test the historical_func function with empty input data to ensure it returns an empty dictionary."""
    result = historical_func([], [])
    assert result == {}


def test_competative_func():
    """Test the competative_func function with valid input data to ensure it returns the expected results."""
    symbol = "AAPL"
    years = [2022, 2023]
    result = competative_func(symbol, years)
    assert isinstance(result, dict)
    assert "AAPL" in result
    assert all(year in result["AAPL"] for year in years)
    assert all("price_to_EBIT_ratio" in result["AAPL"][year] for year in years)


def test_competative_func_invalid():
    """Test the competative_func function with an invalid symbol to ensure it returns the expected results."""
    result = competative_func("INVALID", [2022])
    assert isinstance(result, dict)
    assert "INVALID" in result


def test_qualitative_func():
    """Test the qualitative_func function with valid input data to ensure it returns the expected results."""
    symbols = ["AAPL", "GOOGL"]
    result = qualitative_func(symbols)
    assert isinstance(result, dict)
    assert "AAPL" in result and "GOOGL" in result
    assert "business_info" in result["AAPL"]
    assert "company_data" in result["AAPL"]


def test_qualitative_func_empty():
    """Test the qualitative_func function with empty input data to ensure it returns an empty dictionary."""
    result = qualitative_func([])
    assert result == {}


def test_calculate_profit_margins_no_revenue(mock_fetch_income_statement):
    """Test when the income statement has no revenue field or revenue is 0"""
    mock_fetch_income_statement.return_value = {
        'revenue': None,  # Simulate missing or undefined revenue
        'grossProfit': 500000,
        'operatingIncome': 300000,
        'netIncome': 200000,
        'calendarYear': '2022'
    }

    result = calculate_profit_margins("AAPL", 2022)
    assert result == {"error": "Revenue is zero or undefined."}


def test_calculate_profit_margins_no_data(mock_fetch_income_statement):
    """Test when the API returns no data for the given symbol and year"""
    mock_fetch_income_statement.return_value = None
    result = calculate_profit_margins("AAPL", 2022)
    assert result == {"error": "No data available for the given symbol and year."}


def test_calculate_profit_margins_missing_fields(mock_fetch_income_statement):
    """Test when the income statement is missing some profit fields"""
    mock_fetch_income_statement.return_value = {
        'revenue': 1000000,
        'grossProfit': None,  # Missing gross profit
        'operatingIncome': None,  # Missing operating income
        'netIncome': None,  # Missing net income
        'calendarYear': '2022'
    }

    result = calculate_profit_margins("AAPL", 2022)
    expected_result = json.dumps({
        'Gross Profit Margin (%)': None,
        'Operating Profit Margin (%)': None,
        'Net Profit Margin (%)': None
    })
    assert result == expected_result


def test_price_to_EBIT_ratio_no_market_cap(mock_requests_get):
    """Test when market capitalization data is unavailable"""
    mock_requests_get.side_effect = [
        Mock(status_code=404, json=Mock(return_value=[])),  # Mock failure for market cap response
        Mock(status_code=200, json=Mock(return_value=[{'calendarYear': '2022', 'operatingIncome': 50000000}])),  # Mock income statement response
    ]

    result = price_to_EBIT_ratio("AAPL", 2022)
    assert result is None


def test_price_to_EBIT_ratio_no_ebit(mock_requests_get):
    """Test when EBIT (operatingIncome) data is unavailable"""
    mock_requests_get.side_effect = [
        Mock(status_code=200, json=Mock(return_value=[{'marketCap': 1000000000}])),  # Mock market cap response
        Mock(status_code=200, json=Mock(return_value=[{'calendarYear': '2022', 'operatingIncome': None}])),  # Mock income statement response with no EBIT
    ]

    result = price_to_EBIT_ratio("AAPL", 2022)
    assert result is None


def test_price_to_EBIT_ratio_zero_ebit(mock_requests_get):
    """Test when EBIT (operatingIncome) is zero"""
    mock_requests_get.side_effect = [
        Mock(status_code=200, json=Mock(return_value=[{'marketCap': 1000000000}])),  # Mock market cap response
        Mock(status_code=200, json=Mock(return_value=[{'calendarYear': '2022', 'operatingIncome': 0}])),  # Mock income statement response with zero EBIT
    ]

    result = price_to_EBIT_ratio("AAPL", 2022)
    assert result is None


def test_price_to_EBIT_ratio_no_data(mock_requests_get):
    """Test when both market capitalization and EBIT data are unavailable"""
    mock_requests_get.side_effect = [
        Mock(status_code=404, json=Mock(return_value=[])),  # Mock failure for market cap response
        Mock(status_code=404, json=Mock(return_value=[])),  # Mock failure for income statement response
    ]

    result = price_to_EBIT_ratio("AAPL", 2022)
    assert result is None


def test_ratios_no_data(mock_requests_get):
    """Test when no data is returned from the API for the given year"""
    mock_requests_get.return_value = Mock(status_code=200, json=Mock(return_value=[{
        "calendarYear": "2021",
        "priceEarningsRatio": 18.4,
        "priceToBookRatio": 2.2,
        "priceEarningsToGrowthRatio": 1.5,
        "priceToSalesRatio": 2.8
    }]))

    result = ratios("AAPL", 2022)
    assert result is None

"""
test_judge_profit.py
This module contains unit tests for the judge_profit module.
It tests the profit calculation functionality for investment performance evaluation.
"""
import pytest
import json
from unittest.mock import patch
from finance.judge_profit import judge_profit, get_historical_data, find_closest_price


@pytest.fixture
def mock_historical_data():
    """Sample historical data fixture with price information for testing."""
    return {
        "symbol": "GOOG",
        "historical": [
            {"date": "2022-12-31", "close": 150.00},
            {"date": "2022-12-30", "close": 149.50},
            {"date": "2023-01-02", "close": 152.00},
            {"date": "2023-12-31", "close": 200.00},
            {"date": "2023-12-29", "close": 198.50}
        ]
    }


@patch('finance.judge_profit.cached_api_request')
def test_get_historical_data_success(mock_cached_api_request, mock_historical_data):
    """Test successful retrieval and parsing of historical stock data."""
    # Setup the mock to return a valid JSON response
    mock_cached_api_request.return_value = json.dumps(mock_historical_data)
    
    # Call the function
    result = get_historical_data("GOOG")
    
    # Assert the function was called with the correct parameters
    mock_cached_api_request.assert_called_once()
    assert 'financialmodelingprep.com' in mock_cached_api_request.call_args[1]['url']
    assert mock_cached_api_request.call_args[1]['api_key_name'] == "FMP_API_KEY"
    
    # Assert the result matches our mock data
    assert result == mock_historical_data
    assert result['symbol'] == "GOOG"
    assert len(result['historical']) == 5


@patch('finance.judge_profit.cached_api_request')
def test_get_historical_data_invalid_json(mock_cached_api_request):
    """Test handling of invalid JSON response from the API."""
    # Setup the mock to return an invalid JSON
    mock_cached_api_request.return_value = "Not a valid JSON"
    
    # Call the function
    result = get_historical_data("GOOG")
    
    # Assert the result is None due to JSON parsing error
    assert result is None


def test_find_closest_price_exact_match(mock_historical_data):
    """Test finding price when there's an exact date match."""
    price = find_closest_price(mock_historical_data, "2022-12-31")
    assert price == 150.00


def test_find_closest_price_approximate_match(mock_historical_data):
    """Test finding the closest price when there's no exact date match."""
    price = find_closest_price(mock_historical_data, "2022-12-29")
    assert price == 149.50  # Should find 2022-12-30 as closest


def test_find_closest_price_no_data():
    """Test handling when no historical data is provided."""
    price = find_closest_price(None, "2022-12-31")
    assert price is None
    
    price = find_closest_price({}, "2022-12-31")
    assert price is None


@patch('finance.judge_profit.get_historical_data')
def test_judge_profit_calculation(mock_get_historical_data, mock_historical_data):
    """Test the profit calculation with mocked data."""
    # Setup the mock to return our test data
    mock_get_historical_data.return_value = mock_historical_data
    
    # Call the function with $10,000 investment
    profit = judge_profit("GOOG", 10000)
    
    # Calculate expected result manually:
    # $10,000 invested at $150 per share = 66 shares
    # 66 shares at $200 per share = $13,200
    # Profit = $13,200 - $10,000 = $3,200
    expected_profit = 3200 
    
    # Assert the result is close to our expected value
    assert pytest.approx(profit, abs=0.01) == expected_profit


@patch('finance.judge_profit.get_historical_data')
def test_judge_profit_uses_closest_date(mock_get_historical_data, mock_historical_data):
    """Test that judge_profit uses the closest available date when exact match isn't found."""
    modified_data = mock_historical_data.copy()
    # Remove exact start date but keep close dates
    modified_data['historical'] = [h for h in mock_historical_data['historical'] if h['date'] != '2022-12-31']
    mock_get_historical_data.return_value = modified_data
    
    # Should not raise an error, should use closest date
    result = judge_profit("GOOG", 10000)
    assert result is not None

@patch('finance.judge_profit.get_historical_data')
def test_judge_profit_no_dates(mock_get_historical_data, mock_historical_data):
    """Test error handling when no viable price data is available."""
    modified_data = mock_historical_data.copy()
    modified_data['historical'] = []  # No dates at all
    mock_get_historical_data.return_value = modified_data
    
    with pytest.raises(ValueError, match="Could not retrieve stock prices"):
        judge_profit("GOOOG", 10000)


@patch('finance.judge_profit.get_historical_data')
def test_judge_profit_no_historical_data(mock_get_historical_data):
    """Test error handling when no historical data is available."""
    # Setup the mock to return None
    mock_get_historical_data.return_value = None
    
    # Assert the function raises a ValueError
    with pytest.raises(ValueError, match="Could not retrieve historical data"):
        judge_profit("GOOG", 10000)


@patch('finance.judge_profit.get_historical_data')
def test_judge_profit_negative_return(mock_get_historical_data, mock_historical_data):
    """Test calculating a negative profit (loss)."""
    # Modify the test data to have a lower end price
    modified_data = mock_historical_data.copy()
    for item in modified_data['historical']:
        if item['date'] in ('2023-12-31', '2023-12-29'):
            item['close'] = 100.00  # Lower than start price
    
    mock_get_historical_data.return_value = modified_data
    
    # Call the function
    profit = judge_profit("GOOG", 10000)
    
    # Calculate expected result:
    # $10,000 invested at $150 per share = 66 shares
    # 66 shares at $100 per share = $6,600
    # Profit = $6,600 - $10,000 = -$3,400
    expected_profit = -3400
    
    # Assert the result is close to our expected negative value
    assert pytest.approx(profit, abs=0.01) == expected_profit
"""
test_apo_utils.py:
Test suite for cached_api_request function.

This test suite covers:
1. Caching Logic: Ensures that cached responses are returned when available.
2. API Calls: Validates that requests are made when responses are not cached.
3. API Key Handling: Checks the correct behavior when API keys are required.
4. Error Handling: Tests how the function responds to missing API keys, cache service failures, and API service failures.

Mocking is used to prevent actual HTTP requests.
"""
import pytest
import requests
from unittest.mock import patch
from database.api_utils import cached_api_request

def test_cached_response():
    """Test if the function returns cached response when available."""
    mock_cache_response = {"data": [{"response": "Cached API Response"}]}
    
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_cache_response
        
        response = cached_api_request("http://example.com/api", api_key_name=None)
        assert response == "Cached API Response"
        mock_post.assert_called_once()

def test_api_call_when_not_cached():
    """Test if function makes an API call when response is not cached."""
    mock_cache_response = {"data": []}  # Cache miss
    mock_api_response = "Live API Response"
    
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_cache_response
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_api_response
        
        response = cached_api_request("http://example.com/api", api_key_name=None)
        assert response == mock_api_response
        assert mock_post.call_count == 2  # One for checking cache, one for logging response
        mock_get.assert_called_once()

def test_missing_api_key():
    """Test if function raises ValueError when API key is missing from env."""
    with patch("os.getenv", return_value=None):
        with pytest.raises(ValueError, match="API key 'FAKE_API_KEY' not found in environment variables"):
            cached_api_request("http://example.com/api", api_key_name="FAKE_API_KEY")

def test_api_key_in_url():
    """Test if function correctly appends API key to URL when required."""
    with patch("os.getenv", return_value="FAKE_KEY"), patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": []}  # Cache miss
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "API Response"
        
        response = cached_api_request("http://example.com/api", api_key_name="FAKE_API_KEY", api_key_in_url=True)
        
        mock_get.assert_called_once_with("http://example.com/api?apiKey=FAKE_KEY", params={})
        assert response == "API Response"

def test_cache_service_down():
    """Test if function handles cache service failure gracefully."""
    with patch("requests.post", side_effect=requests.RequestException("Cache service error")), patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "API Response"
        
        response = cached_api_request("http://example.com/api", api_key_name=None)
        
        assert response == "API Response"
        mock_get.assert_called_once()

def test_api_service_down():
    """Test if function gracefully handles API service failure."""
    with patch("requests.post") as mock_post, patch("requests.get", side_effect=requests.RequestException("API request failed")):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": []}  # Cache miss
        
        with pytest.raises(requests.RequestException, match="API request failed"):
            cached_api_request("http://example.com/api", api_key_name=None)

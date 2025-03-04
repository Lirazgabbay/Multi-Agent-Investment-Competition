"""
api_utils.py
Utility functions for making API requests with caching
using FastAPI routes for chacning API responses.
"""
import requests
from typing import Dict, Optional, Any
import os
from dotenv import load_dotenv

def cached_api_request(
    url: str, 
    api_key_name: Optional[str] = None,
    api_key_param: str = "apiKey",
    params: Dict[str, Any] = {},
    api_key_in_url: bool = False,
    api_service_url: str = "http://localhost:8000"
) -> str:
    """
    Makes an API request with caching using the FastAPI routes.
    If the same request exists in the database, returns the cached response.
    Otherwise, makes the request and caches the response.
    
    Args:
        url (str): The API endpoint URL
        api_key_name (Optional[str]): The name of the API key in the .env file (e.g., 'FMP_API_KEY', 'POLYGON_API_KEY')
        api_key_param (str): The parameter name for the API key in the request (default: 'apiKey')
        params (Dict[str, Any]): Query parameters for the request (excluding the API key)
        api_key_in_url (bool): Whether the API key should be added to the URL directly (True) or in params (False)
        api_service_url (str): The base URL for the caching service
    
    Returns:
        str: The API response as a string
    """
    load_dotenv()
    request_params = params.copy()
    
    if api_key_name:
        api_key_value = os.getenv(api_key_name)
        
        if not api_key_value:
            raise ValueError(f"API key '{api_key_name}' not found in environment variables")
        
        if api_key_in_url:
            if "?" in url:
                url = f"{url}&{api_key_param}={api_key_value}"
            else:
                url = f"{url}?{api_key_param}={api_key_value}"
        else:
            request_params[api_key_param] = api_key_value
    
    cache_request_payload = {
        "params": params,
        "url": url
    }
    
    try:
        cache_response = requests.post(
            f"{api_service_url}/get_api_call", 
            json=cache_request_payload
        )
        
        if cache_response.status_code == 200:
            # Cache hit
            cache_data = cache_response.json()
            if cache_data.get("data") and len(cache_data["data"]) > 0:
                print(f"Using cached response for {url}")
                return cache_data["data"][0]["response"]
    except Exception as e:
        print(f"Error checking cache: {str(e)}")
    
    # If not cached, make the actual API request
    api_response = requests.get(url, params=request_params)
    response_text = api_response.text
    
    # Cache the response using log_api_call endpoint
    cache_payload = {
        "params": params,
        "url": url,
        "response": response_text
    }
    
    try:
        # Log the API call to cache it for future use
        requests.post(f"{api_service_url}/log_api_call", json=cache_payload)
    except Exception as e:
        print(f"Error caching response: {str(e)}")
        # Continue even if caching fails
    
    return response_text

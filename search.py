"""
search.py
This module contains a function that performs a Google search and returns the top results.
The function uses the Google Custom Search API to perform the search and the BeautifulSoup library to extract the content of the search results.
"""
import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from app_constants import START_YEAR


def google_search(query: str, num_results: int = 2, max_chars: int = 500) -> list:  # type: ignore[type-arg]
    """
    Perform a Google search and return the top results.
    the query use START_YEAR, ensures that Google only returns articles published on or before December 31, START_YEAR.

    Args:
        query (str): The search query.
        num_results (int): The number of search results to return.
        max_chars (int): The maximum number of characters to return from the page content.

    Returns:
        list: A list of dictionaries containing the title, link, snippet, and body of each search result.
    """
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        raise ValueError("API key or Search Engine ID not found in environment variables")
    before_year = START_YEAR 
    if before_year:
        query += f" before:{before_year}-12-31"

    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {"key": str(api_key), "cx": str(search_engine_id), "q": str(query), "num": str(num_results)}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.json())
        raise Exception(f"Error in API request: {response.status_code}")

    results = response.json().get("items", [])

    def get_page_content(url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            words = text.split()
            content = ""
            for word in words:
                if len(content) + len(word) + 1 > max_chars:
                    break
                content += " " + word
            return content.strip()
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""

    enriched_results = []
    for item in results:
        body = get_page_content(item["link"])
        enriched_results.append(
            {"title": item["title"], "link": item["link"], "snippet": item["snippet"], "body": body}
        )
        time.sleep(1) 

    return enriched_results

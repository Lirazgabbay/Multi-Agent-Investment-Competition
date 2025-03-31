"""This module contains functions for the judge agents in the investment house competition."""
import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from config.app_constants import END_YEAR
import streamlit as st


def get_investment_house_discussion(house_id: int = None) -> str:
    """
    This function reads the content of a text file and returns it as a string.
    if the file is not found, it returns a message indicating that no discussion was found.
    
    Args:
        house_id (int): The ID of the investment house

    Returns:
        str: The content of the text file
    """
    if house_id not in [1, 2]:
        return "Invalid house ID. Please call with 1 or 2."
    
    filename = f"house{house_id}_discussion.txt"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return f"Discussion file for House {house_id} is empty."
            return content[:1000]
    except FileNotFoundError:
        return f"Discussion file for House {house_id} not found."
    

def google_search(query: str, num_results: int = 2, max_chars: int = 500) -> list:
    """
    Perform a Google search and return the top results.
    the query use START_YEAR, ensures that Google only returns articles published on or before December 31, START_YEAR.

    Args:
        query (str): The search query
        num_results (int): The number of search results to return
        max_chars (int): The maximum number of characters to return from the page content

    Returns:
        list: A list of dictionaries containing the title, link, snippet, and body of each search result
    """
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        raise ValueError("API key or Search Engine ID not found in environment variables")
    before_year = st.session_state.get("END_YEAR", END_YEAR) 
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

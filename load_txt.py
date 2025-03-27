"""This module contains functions that read text files and return their content."""

def get_investment_house_discussion(house_id: int = None) -> str:
    """
    This function reads the content of a text file and returns it as a string.
    if the file is not found, it returns a message indicating that no discussion was found.
    
    Args:
        house_id (int): The ID of the investment house.

    Returns:
        str: The content of the text file.
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
import asyncio
import datetime
import json
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import requests
from config.config_list_LLM import CONFIG_LLM_GPT
import datetime


async def init_investment_house_discussion(agents_init, stocks_symbol: list[str], budget: float, name: str, start_year: int):
    """
    Initiates a discussion between all agents in the investment house 
    until a consensus is reached.

    Parameters:
        agents_init: Object containing all initialized agents.
        stocks_symbol [str]: The stocks symbols to analyze.
        budget (float): Budget for the investment.
        name (str): Name of the investment house.

    Returns:
        dict: A summary of the final decision and key discussion points.
    """
    # Create a model client that will be used for the selector

    load_dotenv()
    api_key_open_AI = os.getenv('OPEN_AI_API_KEY')
    model_client = OpenAIChatCompletionClient(
        model='gpt-3.5-turbo',
        api_key=api_key_open_AI,
        temperature=0.7,
        timeout=200
    )
        
    # Set up termination conditions
    text_termination = TextMentionTermination("TERMINATE")
    max_messages = MaxMessageTermination(max_messages=15)
    termination = text_termination | max_messages
    
    # Create the selector prompt
    selector_prompt = """You are coordinating a financial analysis discussion.
The following roles are available:
{roles}.

The liquidity_agent analyzes stock liquidity.
The historical_margin_multiplier_analyst examines historical margin trends.
The competative_margin_multiplier_analyst provides insights on competitive positioning.
The qualitative_analyst evaluates qualitative factors.
The manager_agent guides the discussion and ensures all perspectives are considered.

Given the current context, select the most appropriate next speaker.
Each agent should:
- Execute the function call they suggest
- Analyze the results and provide insights
- Challenge any perspectives they disagree with

Only after an agent finishes their analysis, choose the next agent to speak.

Read the following conversation. Then select the next role from {participants} to play. Only return the role.

{history}

Read the above conversation. Then select the next role from {participants} to play. ONLY RETURN THE ROLE."""
    
    team = SelectorGroupChat(
        participants=[
            agents_init.liquidity_agent,
            agents_init.historical_margin_multiplier_analyst,
            agents_init.competative_margin_multiplier_analyst, 
            agents_init.qualitative_analyst,
            agents_init.manager_agent
        ],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True
    )
    
    dict_symbol_price = StockPrice(stocks_symbol, start_year)


    initial_message = f"""Let's analyze {stocks_symbol} for a potential investment of ${budget:,.2f}.
Liquidity Analyst, please start by presenting your analysis of {stocks_symbol} liquidity.
Historical Margin Analyst, follow with an analysis of historical margin trends.
Competitive Margin Analyst, provide your insights on competitive positioning.
Qualitative Analyst, provide your insights on qualitative factors.
Manager, please guide the discussion and ensure all perspectives are considered. Facilitate a consensus on whether to invest and how much.
All agents please respond to each other for challenging any perspectives you disagree with.

The current prices of {stocks_symbol} are {dict_symbol_price}.
Please base your analyses on data up to and including {start_year}."""


    # Use Console to display conversation in real-time
    print("\nStarting conversation:")
    
    result = await Console(team.run_stream(task=initial_message))
    messages = result.messages

    try:
        summary_message = TextMessage(
            content=f"Summarize this discussion:\n{messages}", 
            source="user"
        )
        
        summary_response = await agents_init.summary_agent.on_messages(
            [summary_message], 
            None  
        )
        
        # Extract the content from the response
        if hasattr(summary_response, 'chat_message') and hasattr(summary_response.chat_message, 'content'):
            return summary_response.chat_message.content
        else:
            return "A summary could not be generated in the expected format."
            
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"The discussion about {stocks_symbol} included multiple messages from the team. A formal summary could not be generated due to a technical issue."



def StockPrice(symbols: list[str], start_year: int):
    """
    Get the closing stock prices for specific symbols within a given year.

    Parameters:
    symbols (list[str]): List of stock ticker symbols.
    start_year (int): The year for which to retrieve closing prices.

    Returns:
    dict: A dictionary with symbols as keys and lists of closing prices as values.
    """
    load_dotenv()
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'FMP_API_KEY' environment variable.")
    
    base_url = "https://financialmodelingprep.com/api/v3/historical-price-full"
    headers = {'Content-Type': 'application/json'}
    res = {}

    for stock_symbol in symbols:
        url = f"{base_url}/{stock_symbol}?apikey={api_key}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'historical' in data:
                for record in data['historical']:
                    record_date = datetime.datetime.strptime(record['date'], '%Y-%m-%d')
                    if record_date.year == start_year:
                        res[stock_symbol] = record['close']
                        break
    
    return res
"""
group_chat.py
This file contains the code for the group chat functionality of the Investment House discussion.
"""
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage
from autogen_core import AgentId
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import streamlit as st
import requests
import datetime
import os
from autogen_agentchat.messages import (
    ModelClientStreamingChunkEvent,
    ToolCallRequestEvent,
    ToolCallExecutionEvent
)


async def init_investment_house_discussion(agents_init, stocks_symbol: list[str], budget: float, name: str, start_year: int, chat_placeholder):
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
    load_dotenv()
    api_key_open_AI = os.getenv('OPEN_AI_API_KEY')
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-2024-08-06",
        api_key=api_key_open_AI,
        temperature=0.3,
        timeout=600
    )
    
    text_termination = TextMentionTermination("TERMINATE")
    max_messages = MaxMessageTermination(max_messages=30)
    termination = text_termination | max_messages
    
    selector_prompt = """You are a coordinator of a financial analysis discussion.
    The first speaker must always be the **liquidity_agent**. 
    The groupchat order should follow:
    liquidity_agent -> historical_margin_multiplier_analyst -> competative_margin_multiplier_analyst -> qualitative_analyst -> red_flags_agent -> search_agent -> red_flags_agent_liquidity -> search_agent -> liquidity_agent -> solid_agent -> search_agent -> Pro_Investment_agent -> search_agent -> manager_agent.
    Note: liquidity_agent is the first speaker
    Only after manager_agent speaks, follow the order dynamically based on the discussion.

    -   If there is a deadlock, or a consensus has reached - the manager_agent should intervene.
    -   If the manager calls all the team members to provide final decision, they should provide their decision in this order:
        liquidity_agent -> historical_margin_multiplier_analyst -> competative_margin_multiplier_analyst -> qualitative_analyst -> red_flags_agent -> red_flags_agent_liquidity -> Pro_Investment_agent -> solid_agent

    Now, given the current context and debate - select the most appropriate next speaker.
    The following roles are available: {roles}.

    {history}
    Read the above conversation. Then select the next role from {participants} to play according to the relevant info and debate. ONLY RETURN THE ROLE."""

    team = SelectorGroupChat(
        participants=[
            agents_init.liquidity_agent,
            agents_init.historical_margin_multiplier_analyst,
            agents_init.competative_margin_multiplier_analyst, 
            agents_init.qualitative_analyst,
            agents_init.red_flags_agent,
            agents_init.search_agent,
            agents_init.red_flags_agent_liquidity,
            agents_init.solid_agent,
            agents_init.pro_investment_agent,
            agents_init.manager_agent
        ],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,
        max_selector_attempts=10
    )

    
    dict_symbol_price = StockPrice(stocks_symbol, start_year)


    initial_message = f"""Let's analyze {stocks_symbol} for a potential investment of ${budget:,.2f}.
    Liquidity Analyst, start by presenting your analysis of liquidity.  
    Historical Margin Analyst, speak after the Liquidity Analyst and provide an analysis of historical margin trends.  
    Competitive Margin Analyst, speak after the Historical Analyst and add insights on competitive positioning.  
    Qualitative Analyst, present your insights on qualitative factors after the Competitive Margin Analyst.  

    Red Flags Agent, you should identify potential risks and weaknesses only after the team has completed their analyses.  
    red_flags_agent_liquidity, you should identify potential risks and problems with the analysis
    solid_agent, you should exposing all potential dangers, uncertainties, and red flags associated with any investment decision.
    Pro_Investment_agent, you should emphasizes that inaction is the biggest financial risk
    Search Agent, you only respond to requests from the Red Flags Agent, red_flags_agent_liquidity,solid_agent,Pro_Investment_agent — provide any information they ask for to help assess risks and concerns.  

    Manager, ensure all perspectives are considered and facilitate a consensus on whether to invest and how much.  

    Each agent should:  
    - Respond to each other when challenging perspectives.  
    - Execute only their designated function calls and analyze the data accordingly.  
    - Return a final decision and the recommended investment amount at the end of the discussion.  

    The Manager Agent should intervene only as a last resort in the following cases:  
    - No other agent has a relevant function to execute.  
    - The conversation reaches a deadlock and no progress is made for two rounds.  
    - Request from every agent to provide a final decision of investment (percentage from the budget). 

    The current prices of {stocks_symbol} are {dict_symbol_price}.  
    Please base your analyses on data up to and including {start_year}."""

    # chat_placeholder = st.empty()

    chat_key = "house1_messages" if name == "Investment House 1" else "chat_messages_2"
    
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    chat_messages = st.session_state[chat_key] 
    print("\nStarting conversation:")
    
    # result = await Console(team.run_stream(task=initial_message)
    # messages = result.messages
    messages = []
    async for event in team.run_stream(task=initial_message):
        # Skip system-generated messages (function calls, tool execution logs)
        if isinstance(event, (ModelClientStreamingChunkEvent, ToolCallRequestEvent, ToolCallExecutionEvent)):
            continue  # Ignore tool execution events

        agent_name = getattr(event, "source", "Unknown Agent")
        if isinstance(agent_name, AgentId):  
            agent_name = agent_name.type

        message_content = getattr(event, "content", str(event))

        messages.append(message_content)

        # Format the message
        chat_messages.append({"role": agent_name, "content": message_content}) 
        
        with chat_placeholder.container():
                for msg in chat_messages:
                    with st.chat_message("assistant"):  
                        st.write(f"**{msg.get('role', 'Unknown Agent')}**")  
                        st.markdown(msg.get("content", "")) 


        await asyncio.sleep(0.1)  # Allow UI to update smoothly


    try:
        summary_message = TextMessage(
            content=f"Summarize this discussion:\n{messages} and conclude a final investment decision.", 
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

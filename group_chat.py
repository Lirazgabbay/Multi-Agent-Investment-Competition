"""
group_chat.py
This file contains the code for the group chat functionality of the Investment House discussion.
"""
import asyncio
import contextlib
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
import io
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
    api_key_open_AI = os.getenv('OPENAI_API_KEY')
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-2024-08-06",
        api_key=api_key_open_AI,
        temperature=0.3,
        timeout=600
    )
    
    text_termination = TextMentionTermination("TERMINATE")
    max_messages = MaxMessageTermination(max_messages=40)
    termination = text_termination | max_messages
    
    # selector_prompt = """You are a coordinator of a financial analysis discussion.
    # - The following roles are available: {roles}.
    # - The groupchat order should usually follow:
    # liquidity_agent -> historical_margin_multiplier_analyst -> competative_margin_multiplier_analyst -> qualitative_analyst -> red_flags_agent -> search_agent -> red_flags_agent_liquidity -> search_agent -> liquidity_agent -> solid_agent -> search_agent -> Pro_Investment_agent -> search_agent -> manager_agent.
    # - make sure each agent get its turn to speak, and you can change the order dynamically based on the discussion.

    # {history}
    # Read the above conversation. Then select the best fit as the next speaker from {participants} to play according to the relevant info and debate. ONLY RETURN THE ROLE.

    # -   If there is a deadlock, or a consensus has reached - the manager_agent should intervene.
    # -   If the manager calls all the team members to provide final decision, they should provide their decision in this order:
    #     liquidity_agent -> historical_margin_multiplier_analyst -> competative_margin_multiplier_analyst -> qualitative_analyst -> red_flags_agent -> red_flags_agent_liquidity -> Pro_Investment_agent -> solid_agent
    # """
    
    selector_prompt = """
    You are the **coordinator** of a financial analysis discussion.
    Your role is to dynamically **select the next agent to speak** based on the conversation’s needs.

    ### **🔹 Speaker Selection Rules**
    1️⃣ **Prioritize Resolving Unanswered Questions**  
    - If an agent raises a question, **select the best-suited agent to respond** before moving forward.  
    - Example: If **Red Flags Analyst** questions the **Liquidity Analyst**, Liquidity Analyst should be selected next.  

    2️⃣ **Do NOT Select the Manager Repeatedly**  
    - The **Manager should only speak when**:
        - Agents are in disagreement and require mediation.
        - All agents have provided their final investment decisions and a final consensus check is required.  
    - **If debate is still ongoing, keep selecting debating agents, NOT the Manager.**  

    3️⃣ **Red Flags Agents Must Always Provide Risks Before Finalization**  
    - If the **Red Flags Analyst** and **Red Flags Liquidity Analyst** have NOT spoken yet, **they MUST be selected next**.  
    - If risks are identified, **ensure these risks are debated before finalizing investment recommendations.**  

    4️⃣ **Agents Must Debate Until They Reach the SAME Investment Percentage**  
    - If agents propose **different investment allocations**, **force them to debate until they agree**.  
    - **DO NOT select the Manager to finalize the decision if disagreements still exist.**  
    - Keep selecting debating agents until they reach a shared decision.  

    5️⃣ **Search Agent Should Only Speak If Requested**  
    - The **Search Agent should NOT be called automatically** unless another agent explicitly asks for external data.  

    6️⃣ **Final Investment Decision Order**  
    - Once the Manager calls for final investment decisions, agents should respond **in this order**:  
        `liquidity_agent → historical_margin_multiplier_analyst → competative_margin_multiplier_analyst → qualitative_analyst → red_flags_agent → red_flags_agent_liquidity → pro_investment_agent → solid_agent`  
    - If agents provide **different investment percentages**, force them to debate until they align.  

    ---

    ### **🔹 Decision Logic**
    {history}  
    Read the conversation above. **Now select the next agent to speak from {participants}** based on the rules.  

    🚫 **DO NOT select the Manager unless**:
    - There is a **clear deadlock** and mediation is needed.  
    - All agents have spoken, and a final consensus check is required.  

    ✔ **Prioritize agents who need to respond to unresolved questions or debates.**  
    💬 **If agents disagree, keep selecting debating agents until they agree.**  
    ✅ **Select the Manager ONLY when consensus is near or final checks are needed.**  

    ONLY RETURN THE ROLE.
    """

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
    - Return a final decision and the recommended investment amount (percentage of the budget).

    The Manager Agent should:
    - Ensure that ALL 8 KEY AGENTS (liquidity_agent, historical_margin_multiplier_analyst, competative_margin_multiplier_analyst, qualitative_analyst, red_flags_agent, red_flags_agent_liquidity, solid_agent, Pro_Investment_agent) explicitly provide their final percentage recommendation.
    - Track which agents have provided their final investment percentage and which haven't.
    - Only conclude the discussion when all 8 key agents have provided their final decision AND they all agree on the same percentage.


    The current prices of {stocks_symbol} are {dict_symbol_price}.  
    Please base your analyses on data up to and including {start_year}."""


    chat_key = "house1_messages" if name == "Investment House 1" else "chat_messages_2"
    
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    chat_messages = st.session_state[chat_key] 
    print("\nStarting conversation:")

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
      
        if "TaskResult" in message_content:
            continue 
        
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
            summary_text = summary_response.chat_message.content
            chat_messages.append({"role": "Summary Agent", "content": summary_text})
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

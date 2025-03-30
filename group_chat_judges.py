"""
group_chat_judges.py
This module contains functions to compare and judge the final decisions of investment houses.
"""
import os
import asyncio
from autogen_core import AgentId
import streamlit as st
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from init_judge_agents import InitJudgeAgent
from autogen_agentchat.messages import (
    ModelClientStreamingChunkEvent,
    ToolCallRequestEvent,
    ToolCallExecutionEvent
)


async def init_judges_discussion(init_judges: InitJudgeAgent, stocks_symbol: list[str], budget: float, names: list[str], start_year: int, end_year: int, summary: str, chat_placeholder):
    """
    Initiates a discussion between all judges in the investment house 
    until a consensus is reached.

    Parameters:
        init_judges: Object containing all initialized judges.
        stocks_symbol [str]: The stocks symbols to analyze.
        budget (float): Budget for the investment.
        names [str]: Names of the investment houses.
        start_year (int): The given start year for the investment.
        end_year (int): The end year to use for the judgement.
        summary (str): A summary of the final decision and key discussion points made by the investment houses.

    Returns:
        dict: A summary of the final decision verdict for each investment house.
    """
    load_dotenv()
    # api_key_openrouter = os.getenv('OPENROUTER_API_KEY')
    # model_client = OpenAIChatCompletionClient(
    #     model="openai/gpt-4o-mini",
    #     base_url="https://openrouter.ai/api/v1",
    #     api_key=api_key_openrouter,
    #     extra_headers={
    #         "HTTP-Referer": "http://localhost:8000",
    #         "X-Title": "Investment Analysis App"
    #     },
    #     model_info={
    #         "completion_parser": "openai",
    #         "chat_parser": "openai",
    #         "use_system_prompt": True,
    #         "function_calling": False,
    #         "supports_function_calling": False,
    #         "supports_vision": False,
    #         "vision": False,
    #         "json_output": False,
    #         "family": "gpt-4o-mini"
    #     }
    # )
    
    api_key_open_AI = os.getenv('OPENAI_API_KEY')
    selector_model_client = OpenAIChatCompletionClient(
        model="gpt-3.5-turbo",
        api_key=api_key_open_AI,
        temperature=0.1,
        timeout=600
    )


    text_termination = TextMentionTermination("TERMINATE")
    max_messages = MaxMessageTermination(max_messages=30)
    termination = text_termination | max_messages
    
    selector_prompt = """You are a coordinator of a the final judgement discussion.
    The first speaker MUST ALWAYS be the **Manager**. 
    The groupchat order should be as follows:
    manager -> decision_quality_judge -> profit_judge -> web_surfer -> manager.
    
    {history}
    Read the above conversation. Then select the next role from {participants} to play according to the relevant info and debate. ONLY RETURN THE ROLE.
    """
    
    team = SelectorGroupChat(
        participants=[
            init_judges.decision_quality_judge,
            init_judges.profit_judge,
            init_judges.web_surfer,
            init_judges.manager_agent
        ],
        model_client=selector_model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,
        max_selector_attempts=10
    )

    initial_message = f"""Welcome to the final judgement discussion for the investment houses: {names}.
    The goal of this discussion is to compare and judge the final decisions of the investment houses, and determine which one did better.
    The stocks to analyze was: {stocks_symbol}.
    The budget for the investment was for both houses: {budget}.
    The money was invested is: {budget} multiplied by the percentage that was allocated to the stock by the investment house.
    The given start year was: {start_year}.
    
    Extract the final decisions of both houses from the summary massage: {summary}.
    
    The end year you can use for your judgement is: {end_year}.
    
    Your judging team includes:
    - Profit Judge: Evaluates the actual profit made by each house using performance metrics.
    - Web Surfer: Provides external information about company events and macroeconomic factors that occurred after {start_year}.
    - Decision Quality Judge: Evaluates how complete, logical, and well-structured each house's internal decision-making process was. They may use the tool `get_investment_house_discussion(house_id)` to retrieve full internal discussions.

    Manager, guide this judging discussion by:
    1. Asking each judge for their analysis.
    2. Comparing both houses using all three perspectives: profit, decision quality, and external events.
    3. Delivering a final verdict on which house made the better decision, and why.
    
    Determine which investment house made the best decision and why.
    Let's begin the discussion!
    """
    
    # Use session state to track messages
    if "judges_chat" not in st.session_state:
        st.session_state["judges_chat"] = []

    chat_messages = st.session_state["judges_chat"]


    print("\nStarting conversation:")
    
    messages = []
    async for event in team.run_stream(task=initial_message):
        if isinstance(event, (ModelClientStreamingChunkEvent, ToolCallRequestEvent, ToolCallExecutionEvent)):
            continue  # Ignore system-generated messages

        # Extract agent name
        agent_name = getattr(event, "source", "Unknown Agent")
        if isinstance(agent_name, str):
            agent_name = agent_name
        elif isinstance(agent_name, AgentId):
            agent_name = agent_name.type  # Extract agent type if it's an object

        # Extract message content
        message_content = getattr(event, "content", str(event))

        messages.append(message_content)

        # Store message in session state
        chat_messages.append({"role": agent_name, "content": message_content})

        if "TaskResult" in message_content:
            continue 
        
        # Display messages dynamically
        with chat_placeholder.container():
            for msg in chat_messages:
                with st.chat_message("assistant"):  # Display all agents as "assistant"
                    st.write(f"**{msg.get('role', 'Unknown Agent')}**")  # Show agent name
                    st.markdown(msg.get("content", ""))  # Display message content

        await asyncio.sleep(0.1)  # Allow UI to update

    try:
        summary_message = TextMessage(
            content=f"Summarize this discussion:\n{messages} and conclude a final investment decision.", 
            source="user"
        )
        
        summary_response = await init_judges.summary_agent.on_messages(
            [summary_message], 
            None  
        )
        
        # Extract the content from the response
        if hasattr(summary_response, 'chat_message') and hasattr(summary_response.chat_message, 'content'):
            # return summary_response.chat_message.content
            return {
                "summary": summary_response.chat_message.content,
                "full_discussion": chat_messages  # This is the list of messages
            }
        else:
            # return "A summary could not be generated in the expected format."
            return {
                "summary": "Summary not available.",
                "full_discussion": chat_messages
            }

            
    except Exception as e:
        print(f"Error generating summary: {e}")
        error_message = f"The discussion about {stocks_symbol} included multiple messages from the team. A formal summary could not be generated due to a technical issue."
        return {
            "summary": error_message,
            "full_discussion": chat_messages
        }
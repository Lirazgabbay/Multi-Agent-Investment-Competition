# import autogen
# from config.config_list_LLM import CONFIG_LLM_GPT4
# import init_agents as InitAgents
# import os
# import time
# from autogen_agentchat.teams import SelectorGroupChat
# from autogen_ext.models.openai import OpenAIChatCompletionClient
# from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination


# async def init_investment_house_discussion(agents_init:InitAgents, stock_symbol: str, budget: float, name:str):
#     """
#     Initiates a discussion between all agents in the investment house 
#     until a consensus is reached.

#     Parameters:
#         agents (InitAgents): Object containing all initialized agents.
#         stock_symbol (str): The stock symbol to analyze.
#         budget (float): Budget for the investment.
#         name (str): Name of the investment house.

#     Returns:
#         dict: A summary of the final decision and key discussion points.
#     """
#     # Create a model client that will be used for the selector
#     model_client = OpenAIChatCompletionClient(
#         model="gpt-4",
#         config_list=CONFIG_LLM_GPT4,
#         timeout=200
#     )
    
#     # Create the SelectorGroupChat with all the agents
#     # Each agent will directly use their tools instead of routing through a user proxy
#     team = SelectorGroupChat(
#         participants=[
#             agents_init.liquidity_agent,
#             agents_init.historical_margin_multiplier_analyst,
#             agents_init.competative_margin_multiplier_analyst,
#             agents_init.qualitative_analyst,
#             agents_init.manager_agent  # Represents the Manager agent that speaks during the discussion and provides the final decision
#         ],
#         model_client=model_client,
#         termination_condition=termination,
#         allow_repeated_speaker=True,
#         selector_prompt=selector_prompt)

# termination = MaxMessageTermination(
#         max_messages=10) | TextMentionTermination("TERMINATE")
    
# selector_prompt="""You are coordinating a financial analysis discussion.
# The following roles are available:
# {roles}.

# Read the following conversation. Then select the next role from {participants} to speak.
# Choose the role that should logically continue the discussion based on their expertise and the current discussion flow.
# each agent should:
# - execute the function call they suggest
# - Analyze the results and provide insights
# - Challenge any perspectives they disagree with
# only after some agent finishes their analysis, choose the next agent to speak
# Only return the role name.

# {history}

# Based on the conversation above, select the next role from {participants} to speak. Only return the role name.
# """

# # Constructing the initial message
# initial_message = f"""Let's analyze {stock_symbol} for a potential investment of ${budget:,.2f}.
# Liquidity Analyst, please start by presenting your analysis of {stock_symbol} liquidity.
# Historical Margin Analyst, follow with an analysis of historical margin trends.
# Competitive Margin Analyst, provide your insights on competitive positioning.
# Qualitative Analyst, provide your insights on qualitative factors.
# Manager, please guide the discussion and ensure all perspectives are considered. Facilitate a consensus on whether to invest and how much.
# All agents please respond to each other for challenging any perspectives you disagree with."""

#     # Run the discussion
#     result = await groupchat.run(task=initial_message)
    
#     # Extract all messages from the result
#     messages = result.messages
    
#     # Create a chat history string from all messages
#     chat_history = "\n".join([f"{msg.source}: {msg.content}" for msg in messages])
    
#     # Use the summary agent to create a summary
#     summary = agents_init.summary_agent.generate_reply(
#         messages=[{"role": "user", "content": f"Summarize this discussion:\n{chat_history}"}],
#         sender=agents_init.user_proxy
#     )

#     return summary["content"] if isinstance(summary, dict) else summary


import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from config.config_list_LLM import CONFIG_LLM_GPT4


async def init_investment_house_discussion(agents_init, stock_symbol: str, budget: float, name: str):
    """
    Initiates a discussion between all agents in the investment house 
    until a consensus is reached.

    Parameters:
        agents_init: Object containing all initialized agents.
        stock_symbol (str): The stock symbol to analyze.
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
    
    # Create the SelectorGroupChat with all the agents
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
    
    # Constructing the initial message
    initial_message = f"""Let's analyze {stock_symbol} for a potential investment of ${budget:,.2f}.
Liquidity Analyst, please start by presenting your analysis of {stock_symbol} liquidity.
Historical Margin Analyst, follow with an analysis of historical margin trends.
Competitive Margin Analyst, provide your insights on competitive positioning.
Qualitative Analyst, provide your insights on qualitative factors.
Manager, please guide the discussion and ensure all perspectives are considered. Facilitate a consensus on whether to invest and how much.
All agents please respond to each other for challenging any perspectives you disagree with."""


 # Use Console to display conversation in real-time
    print("\nStarting conversation:")
    
    result = await Console(team.run_stream(task=initial_message))
    messages = result.messages

    # Use the summary agent to create a summary
    try:
        # Create a message for the summary agent
        summary_message = TextMessage(
            content=f"Summarize this discussion:\n{messages}", 
            source="user"
        )
        
        # Use on_messages instead of generate_reply
        summary_response = await agents_init.summary_agent.on_messages(
            [summary_message], 
            None  # No cancellation token needed
        )
        
        # Extract the content from the response
        if hasattr(summary_response, 'chat_message') and hasattr(summary_response.chat_message, 'content'):
            return summary_response.chat_message.content
        else:
            return "A summary could not be generated in the expected format."
            
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"The discussion about {stock_symbol} included multiple messages from the team. A formal summary could not be generated due to a technical issue."
        # Run the discussion
    # result = await team.run(task=initial_message)
    
    # Extract all messages from the result
    # messages = result.messages
    
    # Create a chat history string from all messages
    # chat_history = "\n".join([f"{msg.source}: {msg.content}" for msg in messages])
    
    # # Use the summary agent to create a summary
    # summary = agents_init.summary_agent.generate_reply(
    #     messages=[{"role": "user", "content": f"Summarize this discussion:\n{chat_history}"}],
    #     sender=agents_init.user_proxy
    # )

    # return summary["content"] if isinstance(summary, dict) else summary
import autogen
import init_agents as InitAgents
import os
from autogen import AssistantAgent

def init_investment_house_discussion(agents_init:InitAgents, stock_symbol: str, budget: float, name:str):
    """
    Initiates a discussion between all agents in the investment house 
    until a consensus is reached.

    Parameters:
        agents (InitAgents): Object containing all initialized agents.
        stock_symbol (str): The stock symbol to analyze.
        budget (float): Budget for the investment.
        name (str): Name of the investment house.

    Returns:
        dict: A summary of the final decision and key discussion points.
    """
    groupchat = autogen.GroupChat(
        agents=[
            agents_init.liquidity_agent,
            agents_init.historical_margin_multiplier_analyst,
            agents_init.competative_margin_multiplier_analyst,
            agents_init.qualitative_analyst
        ],
        messages=[],
        max_round=10,
        speaker_selection_method="round_robin",
        allow_repeat_speaker=False
    )

    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config={
            "config_list": [{"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}],
            "timeout": 90
        }
    )

    initial_message = {"content":
        str(f"""Let's analyze {stock_symbol} for a potential investment of ${budget:,.2f}.
        Liquidity Analyst, please start by presenting your analysis of {stock_symbol} liquidity.
        Historical Margin Analyst, follow with an analysis of historical margin trends.
        Competitive Margin Analyst, provide your insights on competitive positioning.
        Qualitative Analyst, provide your insights on qualitative factors.
        Manager, please guide the discussion and ensure all perspectives are considered. Facilitate a consensus on whether to invest and how much.""")
    ,"role":"user", "name": "user"}
    

    # Begin discussion
    agents_init.user_proxy.initiate_chat(manager,message=initial_message)


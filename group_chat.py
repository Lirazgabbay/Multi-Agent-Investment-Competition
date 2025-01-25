import autogen
import init_agents as InitAgents
# TODO: check all

def initiate_stock_discussion(stock_symbol: str, budget: float):
    # Create the group chat
    agents = InitAgents()
    groupchat = autogen.GroupChat(
        agents=[agents.user_proxy, agents.technical_analyst, agents.social_analyst, agents.moderator],
        messages=[],
        max_round=15
    )
    
    manager = autogen.GroupChatManager(groupchat=groupchat)
    
    # Start the discussion
    agents.user_proxy.initiate_chat(
        manager,
        message=f"""
        Let's analyze {stock_symbol} for a potential investment of ${budget:,.2f}.
        
        Technical Analyst, please start by presenting your analysis of {stock_symbol}'s technical indicators.
        After that, Social Analyst will present their perspective on market sentiment.
        
        Both analysts should then discuss and try to reach a consensus on whether to invest and how much.
        
        Moderator, please guide the discussion and ensure both perspectives are thoroughly considered.
        """
    )


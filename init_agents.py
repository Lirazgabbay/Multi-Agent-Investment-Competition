import asyncio
import os
from config.config_list_LLM import CONFIG_LLM_GPT4
from dotenv import load_dotenv
from config.system_messages import SYS_MSG_MANAGER_CONFIG, SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_LIQUIDITY_CONFIG, SYSTEM_MSG_QUALITATIVE_CONFIG
from finance.LLM_get_financial import get_related_companies, quick_ratio
from finance.LLM_get_qualitative import extract_business_info, get_company_data
from finance.profit_margin import calculate_profit_margins
from finance.profit_multipliers import price_to_EBIT_ratio, ratios
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken


class InitAgents():
    def __init__(self):
        # Create a model client for all agents to use
        load_dotenv()
        api_key_open_AI = os.getenv('OPEN_AI_API_KEY')
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-3.5-turbo',
            api_key=api_key_open_AI,
        )
        
        # Liquidity Analyst
        self.liquidity_agent = AssistantAgent(
            name="Liquidity_Analyst",
            model_client=self.model_client,
            tools=[quick_ratio],
            description="Analyzes liquidity ratios for companies.",
            system_message=SYSTEM_MSG_LIQUIDITY_CONFIG,
            reflect_on_tool_use=True 
        )
        
        # Historical Margin Multiplier Analyst
        self.historical_margin_multiplier_analyst = AssistantAgent(
            name="Historical_Margin_Multiplier_Analyst",
            model_client=self.model_client,
            tools=[price_to_EBIT_ratio, ratios, calculate_profit_margins],
            description="Analyzes historical profit margins and valuation multiples.",
            system_message=SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG,
            reflect_on_tool_use=True 
        )

        # Competitive Margin Multiplier Analyst
        self.competative_margin_multiplier_analyst = AssistantAgent(
            name="Competative_Margin_Multiplier_Analyst",
            model_client=self.model_client,
            tools=[get_related_companies, price_to_EBIT_ratio, ratios, calculate_profit_margins],
            description="Analyzes competitive positioning and relative valuation.",
            system_message=SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG,
            reflect_on_tool_use=True 
        )

        # Qualitative Analyst
        self.qualitative_analyst = AssistantAgent(
            name="Qualitative_Analyst",
            model_client=self.model_client,
            tools=[extract_business_info, get_company_data],
            description="Analyzes qualitative factors about the company.",
            system_message=SYSTEM_MSG_QUALITATIVE_CONFIG,
            reflect_on_tool_use=True 
        )

        # Manager Agent
        self.manager_agent = AssistantAgent(
            name="Manager",
            model_client=self.model_client,
            description="Guides the discussion and ensures all perspectives are considered.",
            system_message=SYS_MSG_MANAGER_CONFIG,
            reflect_on_tool_use=True 
        )

        # Summary Agent
        self.summary_agent = AssistantAgent(
            name="Summary_Analyst",
            model_client=self.model_client,
            description="Provides a final summary of the discussion and consensus reached.",
            system_message="Provide the consensus that the agents have reached and a short summary on the final decision."
        )

        # User Proxy Agent (still needed for some interactions)
        self.user_proxy = UserProxyAgent(
            name="User_Proxy"
        )



# async def test_agent_with_tool():
#     agents_init = InitAgents()
#     liquidity_agent = agents_init.liquidity_agent
    
#     try:
#         # Test the agent with a direct message
#         response = await liquidity_agent.on_messages(
#             [TextMessage(content="analyze AAPL symbole", source="user")], 
#             CancellationToken()
#         )
#         print("Liquidity agent response:", response)
#     except Exception as e:
#         print(f"Error testing liquidity agent: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     # Run both tests
#     asyncio.run(test_agent_with_tool())
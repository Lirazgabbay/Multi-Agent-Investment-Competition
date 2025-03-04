import os
from dotenv import load_dotenv
from config.system_messages import SYS_MSG_MANAGER_CONFIG, SYS_MSG_PRO_INVEST, SYS_MSG_SOLID_AGENT, SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_LIQUIDITY_CONFIG, SYSTEM_MSG_QUALITATIVE_CONFIG, SYS_MSG_PRO_INVEST,SYS_MSG_RED_FLAGS
from finance.LLM_get_financial import quick_ratio
from finance.agents_functions import competative_func, historical_func, qualitative_func
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
# from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_ext.models.openai import OpenAIChatCompletionClient
from search import google_search
from autogen_core.tools import FunctionTool


class InitAgents():
    def __init__(self):
        load_dotenv()
        api_key_open_AI = os.getenv('OPEN_AI_API_KEY')
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-3.5-turbo',
            api_key=api_key_open_AI,
        )

        # Internet search: The company's financial reports on SEC Edgar or the Investor Relations section of the company's website.
        google_search_tool = FunctionTool(
            google_search, description="Search Google for information, returns results with a snippet and body content"
        )
        
        self.liquidity_agent = AssistantAgent(
            name="Liquidity_Analyst",
            model_client=self.model_client,
            tools=[quick_ratio],
            description="Analyzes liquidity ratios for companies.",
            system_message=SYSTEM_MSG_LIQUIDITY_CONFIG,
            reflect_on_tool_use=True 
        )
        
        self.historical_margin_multiplier_analyst = AssistantAgent(
            name="Historical_Margin_Multiplier_Analyst",
            model_client=self.model_client,
            tools=[historical_func],
            description="Analyzes historical profit margins and valuation multiples.",
            system_message=SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG,
            reflect_on_tool_use=True 
        )

        self.competative_margin_multiplier_analyst = AssistantAgent(
            name="Competative_Margin_Multiplier_Analyst",
            model_client=self.model_client,
            tools=[competative_func],
            description="Analyzes competitive positioning and relative valuation.",
            system_message=SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG,
            reflect_on_tool_use=True 
        )

        self.qualitative_analyst = AssistantAgent(
            name="Qualitative_Analyst",
            model_client=self.model_client,
            tools=[qualitative_func],
            description="Analyzes qualitative factors about the company.",
            system_message=SYSTEM_MSG_QUALITATIVE_CONFIG,
            reflect_on_tool_use=True 
        )

        self.manager_agent = AssistantAgent(
            name="Manager",
            model_client=self.model_client,
            description="Guides the discussion and ensures all perspectives are considered.",
            system_message=SYS_MSG_MANAGER_CONFIG,
            reflect_on_tool_use=True 
        )

        self.summary_agent = AssistantAgent(
            name="Summary_Analyst",
            model_client=self.model_client,
            description="Provides a final summary of the discussion and consensus reached.",
            system_message="Provide the consensus that the agents have reached and a short summary on the final decision."
        )

        self.user_proxy = UserProxyAgent(
            name="User_Proxy"
        )


        self.red_flags_agent = AssistantAgent(
            name="Red_Flags_Analyst",
            model_client=self.model_client,
            description="Identifies potential risks and problems with the analysis.",
            system_message=SYS_MSG_RED_FLAGS
        )
                    
        self.solid_agent = AssistantAgent(
            name="Solid_Analyst",
            model_client=self.model_client,
            description="An ultra-cautious risk analyst dedicated to exposing all potential dangers, uncertainties, and red flags associated with any investment decision.",
            system_message=SYS_MSG_SOLID_AGENT
        )

        self.red_flags_agent_liquidity = AssistantAgent(
            name="Red_Flags_Analyst_Liquidity",
            model_client=self.model_client,
            description="Identifies potential risks and problems with the analysis.",
            system_message="Ask the liquidity_agent how inventory growth rate to revenue growth rate can influace the liquidity analysis? and ask the search_agent to search for information that supports your doubts."
        )

        self.pro_investment_agent = AssistantAgent(
            name="Pro_Investment_Agent",
            model_client=self.model_client,
            description="A bold and aggressive investment strategist who strongly advocates for taking calculated risks. This agent actively debates against overly cautious approaches, pushes for seizing investment opportunities, and emphasizes that inaction is the biggest financial risk.",
            system_message=SYS_MSG_PRO_INVEST
        )

        self.search_agent = AssistantAgent(
            name="Google_Search_Agent",
            model_client=OpenAIChatCompletionClient(model="gpt-4o"),
            tools=[google_search_tool],
            description="Search Google for information, returns top 2 results with a snippet and body content.",
            system_message="You are a helpful AI assistant. You are getting tasks only from the red_flags_agent and solve tasks using your tools.",
            reflect_on_tool_use=True 
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
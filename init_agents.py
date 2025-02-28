import asyncio
import os
from config.config_list_LLM import CONFIG_LLM_GPT
from dotenv import load_dotenv
from config.system_messages import SYS_MSG_MANAGER_CONFIG, SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_LIQUIDITY_CONFIG, SYSTEM_MSG_QUALITATIVE_CONFIG
from finance.LLM_get_financial import quick_ratio
from finance.agents_functions import competative_func, historical_func, qualitative_func
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken


class InitAgents():
    def __init__(self):
        load_dotenv()
        api_key_open_AI = os.getenv('OPEN_AI_API_KEY')
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-3.5-turbo',
            api_key=api_key_open_AI,
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
"""
init_agents.py
This module contains the InitAgents class that initializes all the agents required for the group chat.
"""

import os
from dotenv import load_dotenv
from config.system_messages import SYS_MSG_MANAGER_CONFIG, SYS_MSG_PRO_INVEST, SYS_MSG_SOLID_AGENT, SYS_RED_FLAGS_AGENT_LIQUIDITY, SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG, SYSTEM_MSG_LIQUIDITY_CONFIG, SYSTEM_MSG_QUALITATIVE_CONFIG, SYS_MSG_PRO_INVEST,SYS_MSG_RED_FLAGS
from finance.LLM_get_financial import quick_ratio
from finance.agents_functions import competative_func, historical_func, qualitative_func
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from utils.search import google_search
from autogen_core.tools import FunctionTool


class InitAgents():
    def __init__(self):
        load_dotenv()

        api_key_open_AI = os.getenv('OPENAI_API_KEY')
        self.gpt4o_mini_model_client = OpenAIChatCompletionClient(
            model='gpt-4o-mini',
            api_key=api_key_open_AI,
            temperature=0.3,
        )

        api_key_open_AI = os.getenv('OPENAI_API_KEY')
        self.gpt4o_model_client = OpenAIChatCompletionClient(
            model='gpt-4o',
            api_key=api_key_open_AI,
            temperature=0.3,
        )

        self.gpt_turbo_model_client = OpenAIChatCompletionClient(
            model='gpt-3.5-turbo', 
            api_key=api_key_open_AI,
            temperature=0.3,
        )

        api_key_openrouter = os.getenv('OPENROUTER_API_KEY')
        self.gemini_model_client  = OpenAIChatCompletionClient(
            model="google/gemini-2.0-flash-lite-001",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key_openrouter,
            temperature=0.3,
            timeout=600,
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Investment Analysis App"
            },
            model_info={
                "completion_parser": "openai",
                "chat_parser": "openai",
                "use_system_prompt": True,
                "function_calling": False,
                "supports_function_calling": False,
                "supports_vision": False,
                "vision": False,
                "json_output": False,
                "family": "gemini-2.0-flash-lite-001"
            }
        )
  

        # Internet search: The company's financial reports on SEC Edgar or the Investor Relations section of the company's website.
        google_search_tool = FunctionTool(
            google_search, description="Search Google for information, returns results with a snippet and body content"
        )

        self.manager_agent = AssistantAgent(
            name="Manager",
            model_client=self.gpt_turbo_model_client,
            description="Guides the discussion and ensures all perspectives are considered.",
            system_message=SYS_MSG_MANAGER_CONFIG,
            reflect_on_tool_use=True 
        )
        
        self.liquidity_agent = AssistantAgent(
            name="Liquidity_Analyst",
            model_client=self.gpt4o_mini_model_client,
            tools=[quick_ratio],
            description="Analyzes liquidity ratios for companies.",
            system_message=SYSTEM_MSG_LIQUIDITY_CONFIG,
            reflect_on_tool_use=True 
        )
        
        self.historical_margin_multiplier_agent = AssistantAgent(
            name="Historical_Margin_Multiplier_Analyst",
            model_client=self.gpt4o_mini_model_client,
            tools=[historical_func],
            description="Analyzes historical profit margins and valuation multiples.",
            system_message=SYSTEM_MSG_HISTORICAL_MARGIN_MULTIPLIER_CONFIG,
            reflect_on_tool_use=True 
        )

        self.competative_margin_multiplier_agent = AssistantAgent(
            name="Competative_Margin_Multiplier_Analyst",
            model_client=self.gpt4o_mini_model_client,
            tools=[competative_func],
            description="Analyzes competitive positioning and relative valuation.",
            system_message=SYSTEM_MSG_COMPETATIVE_MARGIN_MULTIPLIER_CONFIG,
            reflect_on_tool_use=True 
        )

        self.qualitative_agent = AssistantAgent(
            name="Qualitative_Analyst",
            model_client=self.gpt4o_model_client,
            tools=[qualitative_func],
            description="Analyzes qualitative factors about the company.",
            system_message=SYSTEM_MSG_QUALITATIVE_CONFIG,
            reflect_on_tool_use=True 
        )

        self.red_flags_agent = AssistantAgent(
            name="Red_Flags_Analyst",
            model_client=self.gpt4o_mini_model_client,
            description="Identifies potential risks and problems with the analysis.",
            system_message=SYS_MSG_RED_FLAGS
        )

        self.red_flags_agent_liquidity = AssistantAgent(
            name="Red_Flags_Liquidity_Analyst",
            model_client=self.gemini_model_client,
            description="Identifies potential risks and problems with the analysis.",
            system_message=SYS_RED_FLAGS_AGENT_LIQUIDITY,
            reflect_on_tool_use=False
        )
                    
        self.solid_agent = AssistantAgent(
            name="Solid_Analyst",
            model_client=self.gpt4o_mini_model_client,
            description="An ultra-cautious risk analyst dedicated to exposing all potential dangers, uncertainties, and red flags associated with any investment decision.",
            system_message=SYS_MSG_SOLID_AGENT
        )

        self.pro_investment_agent = AssistantAgent(
            name="Pro_Investment_Analyst",
            model_client=self.gpt4o_mini_model_client,
            description="A bold and aggressive investment strategist who strongly advocates for taking calculated risks. This agent actively debates against overly cautious approaches, pushes for seizing investment opportunities, and emphasizes that inaction is the biggest financial risk.",
            system_message=SYS_MSG_PRO_INVEST
        )

        self.search_agent = AssistantAgent(
            name="Google_Search_Analyst",
            model_client=self.gpt4o_mini_model_client,
            tools=[google_search_tool],
            description="Search Google for information, returns top 2 results with a snippet and body content.",
            system_message="You are a helpful AI assistant. You are getting tasks only from the red_flags_agent and solve tasks using your tools.",
            reflect_on_tool_use=True 
        )

        self.summary_agent = AssistantAgent(
            name="Summary_Analyst",
            model_client=self.gemini_model_client,
            description="Provides a final summary of the discussion and consensus reached.",
            system_message="Provide the consensus that the agents have reached and a short summary on the final decision.",
            reflect_on_tool_use=False
        )
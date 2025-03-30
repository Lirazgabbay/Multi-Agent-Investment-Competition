"""
init_judge_agents.py
This module contains the judge agents for the investment house competition.
"""
import os
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
from finance.judge_profit import judge_profit
from search import google_search
from autogen_ext.models.openai import OpenAIChatCompletionClient
from system_messages_judges import SYS_MSG_DECISION_QUALITY_JUDGE, SYS_MSG_MANAGER_JUDGE, SYS_MSG_PROFIT_JUDGE, SYS_MSG_WEBSURFER_JUDGE
from autogen_core.tools import FunctionTool
from load_txt import get_investment_house_discussion
from google.generativeai import GenerationConfig

class InitJudgeAgent():
    def __init__(self):
        load_dotenv()
        api_key_open_AI = os.getenv('OPENAI_API_KEY')
        self.gpt4o_mini_model_client = OpenAIChatCompletionClient(
            model='gpt-4o-mini', 
            api_key=api_key_open_AI,
            temperature=0.3,
        )

        self.gpt4o_model_client = OpenAIChatCompletionClient(
            model='gpt-4o', 
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


        google_search_tool = FunctionTool(
            google_search, description="Search Google for information, returns results with a snippet and body content"
        )

        judge_profit_tool = FunctionTool(
            judge_profit, description="Calculate the profit of a stock in a defined period."
        )

        # self.user_proxy = UserProxyAgent(
        #     name="User_Proxy"
        # )

        self.summary_agent = AssistantAgent(
            name="Summary_Analyst",
            model_client=self.gemini_model_client,
            description="Provides a final summary of the discussion and consensus reached.",
            system_message="Provide the consensus that the agents have reached and a short summary on the final decision.",
            reflect_on_tool_use=False
        )
        
        self.manager_agent = AssistantAgent(
            name="Manager",
            model_client=self.gpt4o_model_client,
            description="Guides the discussion and ensures all perspectives are considered.",
            system_message=SYS_MSG_MANAGER_JUDGE,
            reflect_on_tool_use=True 
        )

        self.profit_judge = AssistantAgent(
            name="Profit_Judge",
            tools=[judge_profit_tool],
            model_client=self.gpt4o_mini_model_client,
            description="Judges the profit of the stock in a defined period.",
            system_message=SYS_MSG_PROFIT_JUDGE,
            reflect_on_tool_use=True 
        )

        self.web_surfer = AssistantAgent(
            name="Web_Surfer",
            model_client=self.gpt4o_mini_model_client,
            tools=[google_search_tool],
            description="Surfs the web for information.",
            system_message=SYS_MSG_WEBSURFER_JUDGE,
            reflect_on_tool_use=True 
        )

        get_discussion_tool = FunctionTool(
        get_investment_house_discussion,
        name="get_investment_house_discussion", 
        description="Returns the full internal discussion of an investment house (1 or 2)."
        )

        self.decision_quality_judge = AssistantAgent(
            name="Decision_Quality_Judge",
            model_client=self.gpt4o_mini_model_client,
            tools=[get_discussion_tool],
            description="Judges the completeness and quality of the decision-making process in each investment house.",
            system_message=SYS_MSG_DECISION_QUALITY_JUDGE,
            reflect_on_tool_use=True
        )

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
from system_messages_judges import SYS_MSG_MANAGER_JUDGE, SYS_MSG_PROFIT_JUDGE, SYS_MSG_WEBSURFER_JUDGE
from autogen_core.tools import FunctionTool

class InitJudgeAgent():
    def __init__(self):
        load_dotenv()
        api_key_open_AI = os.getenv('OPENAI_API_KEY')
        self.model_client = OpenAIChatCompletionClient(
            model='gpt-3.5-turbo',
            api_key=api_key_open_AI,
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
            model_client=self.model_client,
            description="Provides a final summary of the discussion and consensus reached.",
            system_message="Provide the consensus that the agents have reached and a short summary on the final decision."
        )
        
        self.manager_agent = AssistantAgent(
            name="Manager",
            model_client=self.model_client,
            description="Guides the discussion and ensures all perspectives are considered.",
            system_message=SYS_MSG_MANAGER_JUDGE,
            reflect_on_tool_use=True 
        )

        self.profit_judge = AssistantAgent(
            name="Profit_Judge",
            tools=[judge_profit_tool],
            model_client=self.model_client,
            description="Judges the profit of the stock in a defined period.",
            system_message=SYS_MSG_PROFIT_JUDGE,
            reflect_on_tool_use=True 
        )

        self.web_surfer = AssistantAgent(
            name="Web_Surfer",
            model_client=self.model_client,
            tools=[google_search_tool],
            description="Surfs the web for information.",
            system_message=SYS_MSG_WEBSURFER_JUDGE,
            reflect_on_tool_use=True 
        )
"""
init_judge_agents.py
This module contains the judge agents for the investment house competition.
"""
import os
from autogen_agentchat.agents import AssistantAgent
from dotenv import load_dotenv
from finance.judge_profit import judge_profit
from utils.judges_functions import google_search, get_investment_house_discussion
from autogen_ext.models.openai import OpenAIChatCompletionClient
from config.system_messages_judges import SYS_MSG_DECISION_QUALITY_JUDGE, SYS_MSG_MANAGER_JUDGE, SYS_MSG_PROFIT_JUDGE, SYS_MSG_SUMMARY_JUDGE, SYS_MSG_WEBSURFER_JUDGE
from autogen_core.tools import FunctionTool

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

        self.gpt_turbo_model_client = OpenAIChatCompletionClient(
            model='gpt-3.5-turbo', 
            api_key=api_key_open_AI,
            temperature=0.3,
        )

        google_search_tool = FunctionTool(
            google_search, description="Search Google for information, returns results with a snippet and body content"
        )

        judge_profit_tool = FunctionTool(
            judge_profit, description="Calculate the profit of a stock in a defined period."
        )

        get_discussion_tool = FunctionTool(
            get_investment_house_discussion,
            name="get_investment_house_discussion", 
            description="Returns the full internal discussion of an investment house (1 or 2)."
        )
        
        self.manager_judge = AssistantAgent(
            name="Manager",
            model_client=self.gpt_turbo_model_client,
            description="Guides the discussion and ensures all perspectives are considered.",
            system_message=SYS_MSG_MANAGER_JUDGE,
            reflect_on_tool_use=True 
        )

        self.profit_judge = AssistantAgent(
            name="Profit_Judge",
            tools=[judge_profit_tool],
            model_client=self.gpt4o_model_client,
            description="Judges the profit of the stock in a defined period.",
            system_message=SYS_MSG_PROFIT_JUDGE,
            reflect_on_tool_use=True 
        )

        self.web_surfer_judge = AssistantAgent(
            name="Web_Surfer_Judge",
            model_client=self.gpt4o_mini_model_client,
            tools=[google_search_tool],
            description="Surfs the web for information.",
            system_message=SYS_MSG_WEBSURFER_JUDGE,
            reflect_on_tool_use=True 
        )

        self.decision_quality_judge = AssistantAgent(
            name="Decision_Quality_Judge",
            model_client=self.gpt4o_model_client,
            tools=[get_discussion_tool],
            description="Judges the completeness and quality of the decision-making process in each investment house.",
            system_message=SYS_MSG_DECISION_QUALITY_JUDGE,
            reflect_on_tool_use=True
        )

        self.summary_judge = AssistantAgent(
            name="Summary_Judge",
            model_client=self.gpt4o_model_client,
            tools=[get_discussion_tool],
            description="Summarizes the discussion and final verdict of the judges.",
            system_message=SYS_MSG_SUMMARY_JUDGE,
            reflect_on_tool_use=True 
        )
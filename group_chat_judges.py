"""
group_chat_judges.py
This module contains functions to compare and judge the final decisions of investment houses.
"""
import os
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from init_judge_agents import InitJudgeAgent

async def init_judges_discussion(init_judges: InitJudgeAgent, stocks_symbol: list[str], budget: float, names: list[str], start_year: int, end_year: int, summary: str):
    """
    Initiates a discussion between all judges in the investment house 
    until a consensus is reached.

    Parameters:
        init_judges: Object containing all initialized judges.
        stocks_symbol [str]: The stocks symbols to analyze.
        budget (float): Budget for the investment.
        names [str]: Names of the investment houses.
        start_year (int): The given start year for the investment.
        end_year (int): The end year to use for the judgement.
        summary (str): A summary of the final decision and key discussion points made by the investment houses.

    Returns:
        dict: A summary of the final decision verdict for each investment house.
    """
    load_dotenv()
    api_key_open_AI = os.getenv('OPEN_AI_API_KEY')
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-2024-08-06",
        api_key=api_key_open_AI,
        temperature=0.3,
        timeout=600
    )
    
    text_termination = TextMentionTermination("TERMINATE")
    max_messages = MaxMessageTermination(max_messages=30)
    termination = text_termination | max_messages
    
    selector_prompt = """You are a coordinator of a the final judgement discussion.
    The first speaker must always be the **Manager**. 
    The groupchat order should be as follows:
    manager -> profit_judge -> web_surfer -> manager.
    
    {history}
    Read the above conversation. Then select the next role from {participants} to play according to the relevant info and debate. ONLY RETURN THE ROLE.
    """
    
    team = SelectorGroupChat(
        participants=[
            init_judges.profit_judge,
            init_judges.web_surfer,
            init_judges.manager_agent
        ],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True,
        max_selector_attempts=3
    )

    initial_message = f"""Welcome to the final judgement discussion for the investment houses: {names}.
    The goal of this discussion is to compare and judge the final decisions of the investment houses, and determine which one did better.
    The stocks to analyze was: {stocks_symbol}.
    The budget for the investment was for both houses: {budget}.
    The money was invested is: {budget} multiplied by the percentage that was allocated to the stock by the investment house.
    The given start year was: {start_year}.
    Extract the final decisions of both houses from the summary massage: {summary}.
    The end year you can use for your judgement is: {end_year}.
    Manager judge, use the profit judge and web surfer to help you make the final decision.
    Determine which investment house made the best decision and why.
    Let's begin the discussion!
    """
    
    print("\nStarting conversation:")
    
    result = await Console(team.run_stream(task=initial_message))

    messages = result.messages

    try:
        summary_message = TextMessage(
            content=f"Summarize this discussion:\n{messages} and conclude a final investment decision.", 
            source="user"
        )
        
        summary_response = await init_judges.summary_agent.on_messages(
            [summary_message], 
            None  
        )
        
        # Extract the content from the response
        if hasattr(summary_response, 'chat_message') and hasattr(summary_response.chat_message, 'content'):
            return summary_response.chat_message.content
        else:
            return "A summary could not be generated in the expected format."
            
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"The discussion about {stocks_symbol} included multiple messages from the team. A formal summary could not be generated due to a technical issue."

import init_agents as InitAgents
from group_chat import init_investment_house_discussion
from app_constants import BUDGET, TICKER_STOCKS
from judge_agent import JudgeAgent
import time

def Main():
    Investment_house1 = InitAgents.InitAgents()
    Investment_house2 = InitAgents.InitAgents()
    
    print("\n\033[4minvestment house 1 Discussion:\033[0m\n")
    manager_final_conclusion1 = init_investment_house_discussion(Investment_house1, TICKER_STOCKS, BUDGET, "Investment House 1")
    print("\n\033[94mSummery:\033[0m\n", manager_final_conclusion1)

    time.sleep(10)

    print("\n\033[94mInvestment House 2 Discussion:\033[0m\n")
    manager_final_conclusion2 = init_investment_house_discussion(Investment_house2, TICKER_STOCKS, BUDGET, "Investment House 2")
    print("\n\033[94mSummary:\033[0m\n", manager_final_conclusion2)

    print("\n\033[94mIt's now time for the judge to reveal the winner of the Investment House competition!\033[0m\n")
    judge = JudgeAgent()
    judge.judge_investment_house_outputs(manager_final_conclusion1, manager_final_conclusion2)

if __name__ == "__main__":
    Main()

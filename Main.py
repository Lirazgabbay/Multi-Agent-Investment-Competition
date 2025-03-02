import uvicorn
from database.init_db import init_db
import init_agents as InitAgents
from group_chat import init_investment_house_discussion
from app_constants import BUDGET, TICKER_STOCKS
from judge_agent import JudgeAgent
import time
from database.routes import app
import asyncio

async def start_fastapi():
    """Runs FastAPI as a background task."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve() # starts the FastAPI server
    
async def Main():
    init_db("stock_trading.db")
    Investment_house1 = InitAgents.InitAgents()
    Investment_house2 = InitAgents.InitAgents()

    # Start FastAPI in the background
    loop = asyncio.get_running_loop()
    loop.create_task(start_fastapi())
    
    print("\n\033[4minvestment house 1 Discussion:\033[0m\n")
    manager_final_conclusion1 = await init_investment_house_discussion(Investment_house1, TICKER_STOCKS, BUDGET, "Investment House 1", start_year=2022)
    print("\n\033[94mSummery:\033[0m\n", manager_final_conclusion1)

    time.sleep(10)

    # print("\n\033[94mInvestment House 2 Discussion:\033[0m\n")
    # manager_final_conclusion2 = init_investment_house_discussion(Investment_house2, TICKER_STOCKS, BUDGET, "Investment House 2")
    # log_chat_message("investment_house_2.db", "Summary_Agent", manager_final_conclusion2)
    # print("\n\033[94mSummary:\033[0m\n", manager_final_conclusion2)

    # print("\n\033[94mIt's now time for the judge to reveal the winner of the Investment House competition!\033[0m\n")
    # judge = JudgeAgent()
    # judge.judge_investment_house_outputs(manager_final_conclusion1, manager_final_conclusion2)

if __name__ == "__main__":
    asyncio.run(Main())

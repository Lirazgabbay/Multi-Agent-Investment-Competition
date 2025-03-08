import os
import threading
import requests
import uvicorn
from finance.LLM_get_qualitative import get_company_data
from database.init_db import init_db
import init_agents
import init_judge_agents
from group_chat import init_investment_house_discussion
from group_chat_judges import init_judges_discussion
from app_constants import BUDGET, TICKER_STOCKS, START_YEAR, END_YEAR
import time
from database.routes import app
import asyncio


def run_fastapi():
    """Runs FastAPI in a separate thread."""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


def wait_for_fastapi():
    """Waits until FastAPI is fully running by sending health check requests."""
    url = "http://localhost:8000/docs"  # or use a custom `/health` endpoint if you have one
    for _ in range(10):  # Try for 10 seconds
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("✅ FastAPI is ready!")
                return
        except requests.exceptions.ConnectionError:
            pass
        print("⏳ Waiting for FastAPI to start...")
        time.sleep(1)  # Wait 1 second before retrying
    print("❌ FastAPI did not start in time. Exiting...")
    exit(1)  # Exit with error if FastAPI never starts

    
async def Main():

    # Initialize the database
    init_db("stock_trading.db")
    
    # Initialize investment houses
    Investment_house1 = init_agents.InitAgents()
    Investment_house2 = init_agents.InitAgents()
    
    # Initialize judges
    judges = init_judge_agents.InitJudgeAgent()

    # Start FastAPI in a separate thread to avoid blocking
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Wait for FastAPI to be ready
    wait_for_fastapi()

    # Run investment house 1 discussion
    print("\n\033[4mInvestment House 1 Discussion:\033[0m\n")
    manager_final_conclusion1 = await init_investment_house_discussion(
        Investment_house1, 
        TICKER_STOCKS, 
        BUDGET, 
        "Investment House 1", 
        START_YEAR
    )
    print("\n\033[94mSummary for Investment House 1:\033[0m\n", manager_final_conclusion1)

    # Run investment house 2 discussion
    print("\n\033[4mInvestment House 2 Discussion:\033[0m\n")
    manager_final_conclusion2 = await init_investment_house_discussion(
        Investment_house2, 
        TICKER_STOCKS, 
        BUDGET, 
        "Investment House 2", 
        START_YEAR
    )
    print("\n\033[94mSummary for Investment House 2:\033[0m\n", manager_final_conclusion2)

    # manager_final_conclusion1 = """
    # After a thorough analysis and discussion by the team on investing in Apple Inc. (AAPL), 
    # the final decision is to proceed with an investment in AAPL and allocate 30% of the total budget to this opportunity. 
    # The decision is based on various factors, including historical margin trends, competitive positioning, 
    # qualitative insights, liquidity concerns, and differing perspectives on risks and opportunities.

    # The team reached a consensus to invest in Apple Inc. due to its innovation, market position, 
    # and valuation potential, while also acknowledging the identified risks. 
    # The decision aims to capture growth opportunities and maintain a balanced approach to investment.

    # Thank you to all agents for their detailed analyses, challenges, and valuable contributions that led to this final decision.
    # """

    # manager_final_conclusion2 = """
    # After a thorough analysis and discussion by the team on investing in Apple Inc. (AAPL), 
    # the final decision is to proceed with an investment in AAPL and allocate 30% of the total budget to this opportunity. 
    # The decision is based on various factors, including historical margin trends, competitive positioning, 
    # qualitative insights, liquidity concerns, and differing perspectives on risks and opportunities.

    # The team reached a consensus to invest in Apple Inc. due to its innovation, market position, 
    # and valuation potential, while also acknowledging the identified risks. 
    # The decision aims to capture growth opportunities and maintain a balanced approach to investment.

    # Thank you to all agents for their detailed analyses, challenges, and valuable contributions that led to this final decision.
    # """


    # Run the judges discussion
    print("\n\033[4mJudges Panel Discussion:\033[0m\n")
    judges_conclusion = await init_judges_discussion(
        judges,
        TICKER_STOCKS,
        BUDGET,
        ["Investment House 1", "Investment House 2"],
        START_YEAR,
        END_YEAR,
        f"Investment House 1: {manager_final_conclusion1}\n\nInvestment House 2: {manager_final_conclusion2}"
    )
    print("\n\033[94mJudges Final Verdict:\033[0m\n", judges_conclusion)

    # Give some time for any final database operations to complete before exiting
    time.sleep(3)
    print("\n\033[92mProcess completed successfully!\033[0m")


if __name__ == "__main__":
    asyncio.run(Main())

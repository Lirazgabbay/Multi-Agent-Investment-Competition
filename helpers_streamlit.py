"""
helper functions for streamlit app and fastapi app 
"""
import threading
import asyncio
import time
import requests
import uvicorn
import socket
import psutil
import streamlit as st
from database.routes import app
from group_chat import init_investment_house_discussion
from group_chat_judges import init_judges_discussion

# init fastapi server
def is_fastapi_running():
    """Checks if FastAPI is already running."""
    for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        if process.info['cmdline'] and 'uvicorn' in process.info['cmdline'][0]:
            return True
    return False


def is_port_in_use(port: int) -> bool:
    """Checks if a port is already occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def run_fastapi():
    """Starts FastAPI only if it's not already running."""
    if not is_port_in_use(8000):
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    else:
        print("🚀 FastAPI is already running. Skipping startup.")


def wait_for_fastapi():
    """Waits until FastAPI is fully running by sending health check requests."""
    url = "http://localhost:8000/docs" 
    for _ in range(10): 
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("✅ FastAPI is ready!")
                return
        except requests.exceptions.ConnectionError:
            pass
        print("⏳ Waiting for FastAPI to start...")
        time.sleep(1)  
    print("❌ FastAPI did not start in time. Exiting...")
    exit(1) 


def start_fastapi_server():
    """Starts FastAPI in a separate thread if not running."""
    if not is_fastapi_running():
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
    wait_for_fastapi()


# init streamlit session state
def initialize_session_state():
    """Ensures all session state variables are initialized."""
    st.session_state.setdefault("house1_messages", [])
    st.session_state.setdefault("house2_messages", [])
    st.session_state.setdefault("judges_messages", [])

                    
async def run_analysis(stocks, investment_budget, start_year, end_year, house1_chat, house2_chat, judges_chat, investment_house1, investment_house2, judges):
    """Runs AI analysis asynchronously with better UI updates."""
    st.session_state.house1_messages = []
    st.session_state.house2_messages = []
    st.session_state.judges_messages = []
    
    with house1_chat:
        st.write("Investment House 1 analysis in progress...")
    
    with house2_chat:
        st.write("Investment House 2 analysis in progress...")
    
    with judges_chat:
        st.write("Judges panel will evaluate after houses complete their analysis...")
    
    house1_result = await init_investment_house_discussion(
        investment_house1, 
        stocks.split(","), 
        investment_budget, 
        "Investment House 1", 
        start_year,
        house1_chat  
    )
    save_discussion_to_file(1, house1_result['full_discussion'])

    house2_result = await init_investment_house_discussion(
        investment_house2, 
        stocks.split(","), 
        investment_budget, 
        "Investment House 2", 
        start_year,
        house2_chat
    )
    save_discussion_to_file(2, house2_result['full_discussion']) 

    judge_summary = f"House 1: {house1_result['summary']}\n\nHouse 2: {house2_result['summary']}"


    judges_result = await init_judges_discussion(
        judges, 
        stocks.split(","), 
        investment_budget, 
        ["Investment House 1", "Investment House 2"], 
        start_year, 
        end_year, 
        judge_summary,
        judges_chat 
    )
    
def save_discussion_to_file(house_id: int, messages: list[dict]):
    filename = f"house{house_id}_discussion.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for msg in messages:
            role = msg.get("role", "Unknown")
            content = msg.get("content", "")
            f.write(f"[{role}]: {content}\n\n")


def start_analysis_thread(stocks, investment_budget, start_year, end_year, house1_chat, house2_chat, judges_chat, Investment_house1, Investment_house2, judges):
    """Starts AI analysis in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_analysis(stocks, investment_budget, start_year, end_year, house1_chat, house2_chat, judges_chat, Investment_house1, Investment_house2, judges))
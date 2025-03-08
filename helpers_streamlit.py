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
    st.session_state.setdefault("chat_messages_2", [])
    st.session_state.setdefault("chat_messages_judges", [])


async def stream_messages(agent_function, chat_key, chat_container, *args):
    """Streams messages to the UI dynamically with real-time updates."""
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Call the coroutine function
    result = await agent_function(*args)
    
    if isinstance(result, str):
        st.session_state[chat_key].append(result)
        st.experimental_rerun()
    elif hasattr(result, '__iter__') and not isinstance(result, str):
        for message in result:
            st.session_state[chat_key].append(message)
            with chat_container:
                # Display all messages collected so far
                for i, msg in enumerate(st.session_state[chat_key]):
                    message_key = f"{chat_key}_{i}"
                    st.markdown(msg, unsafe_allow_html=True, key=message_key)
            # Small delay to allow UI to update
            await asyncio.sleep(0.2)
            # Force a rerun to update the UI
            st.experimental_rerun()
    else:
        message = str(result)
        st.session_state[chat_key].append(message)
        st.experimental_rerun()
                    
async def run_analysis(stocks, investment_budget, start_year, end_year, house1_chat, house2_chat, judges_chat, investment_house1, investment_house2, judges):
    """Runs AI analysis asynchronously with better UI updates."""
    st.session_state.house1_messages = []
    st.session_state.chat_messages_2 = []
    st.session_state.chat_messages_judges = []
    
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
    
    house2_result = await init_investment_house_discussion(
        investment_house2, 
        stocks.split(","), 
        investment_budget, 
        "Investment House 2", 
        start_year,
        house2_chat
    )
    
    judge_summary = f"House 1: {house1_result}\n\nHouse 2: {house2_result}"
    
    judges_result = await init_judges_discussion(
        judges, 
        stocks.split(","), 
        investment_budget, 
        ["Investment House 1", "Investment House 2"], 
        start_year, 
        end_year, 
        judge_summary,
        house2_chat 
    )
    
    st.session_state.chat_messages_judges.append(judges_result)
    with judges_chat:
        st.empty()
        st.markdown(judges_result, unsafe_allow_html=True)


def start_analysis_thread(stocks, investment_budget, start_year, end_year, house1_chat, house2_chat, judges_chat, Investment_house1, Investment_house2, judges):
    """Starts AI analysis in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_analysis(stocks, investment_budget, start_year, end_year, house1_chat, house2_chat, judges_chat, Investment_house1, Investment_house2, judges))
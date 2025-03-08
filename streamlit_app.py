import streamlit as st
from database.init_db import init_db
from helpers_streamlit import (
    start_fastapi_server,
    start_analysis_thread,
    initialize_session_state
)
import init_agents
import init_judge_agents
from styles import load_custom_styles
from app_constants import BUDGET, TICKER_STOCKS, START_YEAR, END_YEAR

init_db("stock_trading.db")
start_fastapi_server()

Investment_house1 = init_agents.InitAgents()
Investment_house2 = init_agents.InitAgents()
judges = init_judge_agents.InitJudgeAgent()

# Setup Streamlit Page
st.set_page_config(page_title="Investment Analysis", page_icon="📈", layout="wide")
st.title("📊 Investment Houses Competition")
st.subheader("Multi-Agent Investment Analysis & Judging System")

load_custom_styles()
initialize_session_state()

# Sidebar Inputs
st.sidebar.header("Configuration")
stocks_symbol = st.sidebar.text_input("Stock Ticker(s)", "AAPL")
budget = st.sidebar.number_input("Investment Budget ($)", min_value=BUDGET, value=BUDGET, step=0)
st.sidebar.header("Time Period")
start_year = st.sidebar.number_input("Analysis Start Year", min_value=2000, max_value=START_YEAR, value=START_YEAR)
end_year = st.sidebar.number_input("Evaluation End Year", min_value=START_YEAR, max_value=END_YEAR, value=END_YEAR)

start_analysis = st.button("🚀 Start Analysis")


tab1, tab2, tab3 = st.tabs(["🏠 Investment House 1", "🏠 Investment House 2", "⚖️ Judges Panel"])

# Display placeholders for chat discussions
with tab1:
    st.header("Investment House 1 Analysis")
    house1_chat = st.empty()

with tab2:
    st.header("Investment House 2 Analysis")
    house2_chat = st.empty()

with tab3:
    st.header("Judges Panel Verdict")
    judges_chat = st.empty()

# Start Analysis
if start_analysis:
    start_analysis_thread(stocks_symbol, budget, start_year, end_year, house1_chat, house2_chat, judges_chat, Investment_house1, Investment_house2, judges)
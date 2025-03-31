import streamlit as st
from database.init_db import init_db
from helpers_streamlit import (
    start_fastapi_server,
    start_analysis_thread,
    initialize_session_state
)
import group_chats.init_agents as init_agents
import group_chats.init_judge_agents as init_judge_agents
from config.app_constants import BUDGET, TICKER_STOCKS, START_YEAR, END_YEAR

init_db("stock_trading.db")
start_fastapi_server()

Investment_house1 = init_agents.InitAgents()
Investment_house2 = init_agents.InitAgents()
judges = init_judge_agents.InitJudgeAgent()

# Setup Streamlit Page
st.set_page_config(page_title="Investment Analysis", page_icon="📈", layout="wide")
st.title("📊 Investment Houses Competition")
st.subheader("Multi-Agent Investment Analysis & Judging System")

# Load external CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="intro-container">
        <div class="intro-title">📈 Step into the Future of Investment Strategy!</div>
        <div class="intro-text">
            Welcome to the <span class="intro-highlight">Investment Houses Competition</span> – where
            <span class="intro-highlight">AI-driven multi-agent analysis</span> meets real-world financial decision-making.
            Our system simulates real-world investment scenarios, empowering analysts to assess financial opportunities with precision.
        </div>
        <div class="divider"></div>
        <div class="intro-title">Are you ready?</div>
    </div>
    """,
    unsafe_allow_html=True
)


initialize_session_state()

if "BUDGET" not in st.session_state:
    st.session_state["BUDGET"] = BUDGET

if "TICKER_STOCKS" not in st.session_state:
    st.session_state["TICKER_STOCKS"] = ", ".join(TICKER_STOCKS)

st.sidebar.header("Configuration")
st.session_state["TICKER_STOCKS"] = st.sidebar.text_input("Stock Ticker(s)", st.session_state["TICKER_STOCKS"])
st.session_state["BUDGET"] = st.sidebar.number_input("Investment Budget ($)", min_value=1000, value=st.session_state["BUDGET"], step=1000)

if "START_YEAR" not in st.session_state:
    st.session_state["START_YEAR"] = START_YEAR

if "END_YEAR" not in st.session_state:
    st.session_state["END_YEAR"] = END_YEAR
    
st.sidebar.header("Time Period")
st.session_state["START_YEAR"] = st.sidebar.number_input(
    "Analysis Start Year", min_value=2000, max_value=2024, value=st.session_state["START_YEAR"]
)
st.session_state["END_YEAR"] = st.sidebar.number_input(
    "Evaluation End Year", min_value=st.session_state["START_YEAR"], max_value=2025, value=st.session_state["END_YEAR"]
)
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
    start_analysis_thread(st.session_state["TICKER_STOCKS"], st.session_state["BUDGET"], st.session_state["START_YEAR"], st.session_state["END_YEAR"], house1_chat, house2_chat, judges_chat, Investment_house1, Investment_house2, judges)
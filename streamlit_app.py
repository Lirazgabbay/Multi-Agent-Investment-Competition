import streamlit as st
import asyncio
from group_chat import init_investment_house_discussion
from group_chat_judges import init_judges_discussion
import init_agents
import init_judge_agents

# ✅ Initialize session state variables if they don't exist
if "chat_messages_1" not in st.session_state:
    st.session_state["chat_messages_1"] = []
if "chat_messages_2" not in st.session_state:
    st.session_state["chat_messages_2"] = []
if "chat_messages_judges" not in st.session_state:
    st.session_state["chat_messages_judges"] = []
if "running" not in st.session_state:
    st.session_state["running"] = False
if "started_messages" not in st.session_state:
    st.session_state["started_messages"] = {"chat_messages_1": False, "chat_messages_2": False, "chat_messages_judges": False}

# 🔹 Setup Streamlit UI
st.set_page_config(page_title="Investment Houses Competition", layout="wide")
st.title("🏦 Investment Houses Competition")
st.subheader("Multi-Agent Investment Analysis & Judging System")

# Sidebar Inputs
st.sidebar.header("Configuration")
stocks_symbol = st.sidebar.text_input("Stock Ticker(s)", "AAPL")
budget = st.sidebar.number_input("Investment Budget ($)", min_value=1000, value=100000, step=500)

st.sidebar.header("Time Period")
start_year = st.sidebar.number_input("Analysis Start Year", min_value=2000, max_value=2025, value=2022)
end_year = st.sidebar.number_input("Evaluation End Year", min_value=start_year, max_value=2030, value=2024)

# Start Analysis Button
if st.sidebar.button("🚀 Run Full Analysis"):
    st.session_state["running"] = True
    st.session_state["chat_messages_1"].clear()
    st.session_state["chat_messages_2"].clear()
    st.session_state["chat_messages_judges"].clear()
    st.session_state["started_messages"] = {"chat_messages_1": False, "chat_messages_2": False, "chat_messages_judges": False}

# Initialize Agents
Investment_house1 = init_agents.InitAgents()
Investment_house2 = init_agents.InitAgents()
judges = init_judge_agents.InitJudgeAgent()

# 🔹 Create Tabs for Different Sections
tabs = st.tabs(["📊 Overview", "🏠 Investment House 1", "🏠 Investment House 2", "⚖️ Judges Panel"])

# ✅ CSS for Chat Bubbles
st.markdown(
    """
    <style>
        .chat-container {
            display: flex;
            flex-direction: column;
        }
        .chat-bubble {
            max-width: 75%;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 15px;
            font-size: 16px;
            word-wrap: break-word;
            white-space: pre-wrap;
            display: inline-block;
        }
        .user-message {
            background-color: #0084ff;
            color: white;
            align-self: flex-end;
        }
        .agent-message {
            background-color: #f1f0f0;
            color: black;
            align-self: flex-start;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Define Async Discussion Functions
async def run_discussion():
    """Runs the investment discussions and updates UI in real-time."""
    try:
        await stream_messages("chat_messages_1", init_investment_house_discussion, Investment_house1, stocks_symbol.split(", "), budget, "Investment House 1", start_year)
        await stream_messages("chat_messages_2", init_investment_house_discussion, Investment_house2, stocks_symbol.split(", "), budget, "Investment House 2", start_year)
        await stream_messages("chat_messages_judges", init_judges_discussion, judges, stocks_symbol.split(", "), budget, ["Investment House 1", "Investment House 2"], start_year, end_year)
    
    except asyncio.CancelledError:
        st.warning("⚠️ The discussion process was interrupted.")
    
    finally:
        st.session_state["running"] = False  # Ensure UI updates correctly

async def stream_messages(chat_key, agent_function, *args):
    """Calls the agent function and streams its messages live."""
    
    # ✅ Show "Starting discussion" message only once
    if not st.session_state["started_messages"][chat_key]:
        st.session_state[chat_key].append(f"**🔹 Starting discussion for {args[3]}**...")
        st.session_state["started_messages"][chat_key] = True  # Mark as shown
    
    async for message in agent_function(*args):
        if message not in st.session_state[chat_key]:  # ✅ Prevent duplicates
            st.session_state[chat_key].append(message)

        with tabs[1 if chat_key == "chat_messages_1" else 2 if chat_key == "chat_messages_2" else 3]:
            chat_box = st.empty()
            chat_box.markdown("\n".join([f'<div class="chat-bubble agent-message">{msg}</div>' for msg in st.session_state[chat_key]]), unsafe_allow_html=True)

# ✅ Start the discussion if triggered
if "running" in st.session_state and st.session_state["running"]:
    asyncio.run(run_discussion())

# 🔹 Overview Tab
with tabs[0]:
    st.write("### 📈 Overview")
    st.write("This system evaluates investment decisions made by two AI-driven Investment Houses. Each house performs a full analysis, and a Judges Panel reviews their recommendations.")

# 🔹 Investment House 1 Tab
with tabs[1]:
    st.write("### 🏠 Investment House 1 Analysis")
    st.write("#### Agent Conversation")
    chat_box_1 = st.empty()
    if not st.session_state["chat_messages_1"]:
        chat_box_1.info("No messages to display yet.")

# 🔹 Investment House 2 Tab
with tabs[2]:
    st.write("### 🏠 Investment House 2 Analysis")
    st.write("#### Agent Conversation")
    chat_box_2 = st.empty()
    if not st.session_state["chat_messages_2"]:
        chat_box_2.info("No messages to display yet.")

# 🔹 Judges Panel Tab
with tabs[3]:
    st.write("### ⚖️ Judges Panel Decision")
    st.write("#### Discussion")
    chat_box_judges = st.empty()
    if not st.session_state["chat_messages_judges"]:
        chat_box_judges.info("No messages to display yet.")

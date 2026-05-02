import streamlit as st
import os
import json
import sys

# Ensure Python can find the orchestrator module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import AgentOrchestrator, get_indian_datetime, get_stock_price

st.set_page_config(page_title="Agent Orchestrator", layout="centered")

st.title("🤖 Agent Orchestrator")
st.write("Welcome back! Use the modular orchestrator interface below to run your tools.")

@st.cache_resource
def get_or_create_orchestrator():
    agent = AgentOrchestrator()
    agent.register_tool("get_indian_datetime", get_indian_datetime, "Fetches current date and time in IST.")
    agent.register_tool("get_stock_price", get_stock_price, "Fetches current stock values.")
    return agent

agent = get_or_create_orchestrator()

# --- Main Interaction Field ---
user_input = st.text_input("Enter your request:", placeholder="e.g., What is the stock price of TCS?")

if st.button("Execute Task", type="primary"):
    if user_input.strip() == "":
        st.warning("Please enter a command to process.")
    else:
        with st.spinner("Analyzing request and running orchestrator..."):
            result = agent.process_request(user_input)
            
            if result["status"] == "success":
                st.success(f"Action completed using tool: {result['tool']}")
                st.json(result["result"])
            elif result["status"] == "idle":
                st.info(result["message"])
            else:
                st.error(result["message"])

# --- History Section ---
st.markdown("### 📜 Execution History")
history_file = "agent_history.json"

if os.path.exists(history_file):
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
            
        if history:
            for timestamp, data in reversed(list(history.items())):
                with st.expander(f"Task: {data['tool']} at {timestamp.split('T')[1][:8]}"):
                    st.json(data["result"])
        else:
            st.info("No interactions recorded yet.")
    except Exception:
        st.info("No interactions recorded yet.")
        

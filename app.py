import streamlit as st
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

with st.sidebar:
    st.subheader("🛠️ Available Tools")
    for name, tool in agent.tools.items():
        with st.expander(name):
            st.caption(tool["description"])

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

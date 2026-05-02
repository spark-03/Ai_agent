import streamlit as st
import json
from orchestrator import AgentOrchestrator, get_indian_datetime, get_stock_price

# Page Configuration
st.set_page_config(
    page_title="Agent Orchestrator",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🤖 Agent Orchestrator")
st.write("Welcome back! Use the modular orchestrator interface below to run your tools.")

# Initialize the Orchestrator
@st.cache_resource
def get_or_create_orchestrator():
    orchestrator = AgentOrchestrator()
    
    # Register tools
    orchestrator.register_tool(
        name="get_indian_datetime", 
        function_ref=get_indian_datetime, 
        description="Fetches current date and time in Indian Standard Time (IST)."
    )
    orchestrator.register_tool(
        name="get_stock_price", 
        function_ref=get_stock_price, 
        description="Fetches the current market price for a given stock symbol or ticker."
    )
    return orchestrator

agent = get_or_create_orchestrator()

# --- Sidebar for Tool Info ---
with st.sidebar:
    st.subheader("🛠️ Available Tools")
    for name, tool in agent.tools.items():
        with st.expander(name):
            st.caption(tool["description"])

# --- Main Interaction Field ---
user_input = st.text_input(
    "Enter your request:", 
    placeholder="e.g., What is the stock price of TCS?"
)

if st.button("Execute Task", type="primary"):
    if user_input.strip() == "":
        st.warning("Please enter a command to process.")
    else:
        with st.spinner("Analyzing request and running orchestrator..."):
            result = agent.process_request(user_input)
            
            # Display result nicely based on status
            if result["status"] == "success":
                st.success(f"Action completed successfully using tool: {result['tool']}")
                st.json(result["result"])
            elif result["status"] == "idle":
                st.info(result["message"])
            else:
                st.error(result["message"])
  

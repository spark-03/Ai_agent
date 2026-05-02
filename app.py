import streamlit as st
import os
import sys
import json

# Ensure the module path includes the directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import AgentOrchestrator, get_indian_datetime, get_stock_price

st.set_page_config(page_title="Agent Orchestrator", layout="centered")

st.title("🤖 Agent Orchestrator")
st.write("Welcome back! Interact with your orchestrator agent below.")

@st.cache_resource
def get_or_create_orchestrator():
    agent = AgentOrchestrator()
    agent.register_tool("get_indian_datetime", get_indian_datetime, "Fetches current date and time in IST.")
    agent.register_tool("get_stock_price", get_stock_price, "Fetches current stock values.")
    return agent

agent = get_or_create_orchestrator()

# Initialize the chat session state if it does not exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User chat input
if prompt := st.chat_input("What would you like to do? (e.g., What is the stock price of Reliance?)"):
    # Render user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process using the stateful orchestrator
    with st.spinner("Processing request..."):
        result = agent.process_request(prompt)
        
        if result["status"] == "success":
            response = f"**Tool used:** `{result['tool']}`\n\n"
            response += f"```json\n{json.dumps(result['result'], indent=4)}\n```"
        elif result["status"] == "idle":
            response = result["message"]
        else:
            response = f"**Error:** {result['message']}"
            
    # Render and store assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    

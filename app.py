import streamlit as st
import os
import sys
import json

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

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to do? (e.g., What is the stock price of Reliance?)"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Processing request..."):
        result = agent.process_request(prompt)
        
        if result["status"] == "success":
            response = result["response_text"]
            # Keep raw data accessible for debugging
            with st.expander("Show raw data"):
                st.json(result["result"])
        elif result["status"] == "idle":
            response = result["message"]
        else:
            response = f"**Error:** {result['message']}"
            
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    

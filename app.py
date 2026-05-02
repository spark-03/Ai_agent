import streamlit as st
import os
import sys
import pandas as pd
import importlib

# Enforce the current working directory path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import orchestrator
importlib.reload(orchestrator)

st.set_page_config(page_title="Agent Orchestrator", layout="centered")

st.title("🤖 Agent Orchestrator")
st.write("Welcome back! Interact with your orchestrator agent below.")

@st.cache_resource
def get_or_create_orchestrator():
    agent = orchestrator.AgentOrchestrator()
    agent.register_tool("get_indian_datetime", orchestrator.get_indian_datetime, "Fetches current date and time in IST.")
    agent.register_tool("get_stock_price", orchestrator.get_stock_price, "Fetches current stock values.")
    agent.register_tool("get_live_weather", orchestrator.get_live_weather, "Fetches live weather data for a city.")
    agent.register_tool("web_search", orchestrator.web_search, "Searches the web for real-world information.")
    return agent

agent = get_or_create_orchestrator()

# Display or retrieve chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Tool Inspection & Analytics
with st.sidebar:
    st.subheader("🛠️ Available Tools")
    for name, tool in agent.tools.items():
        with st.expander(name):
            st.caption(tool["description"])
            
    st.markdown("---")
    st.subheader("🗄️ Database Logs & Analytics")
    
    import sqlite3
    try:
        conn = sqlite3.connect("agent_memory.db")
        df = pd.read_sql_query("SELECT timestamp, user_message, tool_used FROM memory ORDER BY id DESC", conn)
        conn.close()
        
        if not df.empty:
            st.metric(label="Total Interactions", value=len(df))
            
            # Tool usage breakdown
            tool_counts = df['tool_used'].value_counts()
            st.bar_chart(tool_counts)
            
            with st.expander("Recent Logs"):
                for index, row in df.head(5).iterrows():
                    st.text(f"⏱️ {row['timestamp'][:19]}\n   Msg: {row['user_message']}\n   Tool: {row['tool_used']}")
        else:
            st.info("No logs in memory yet.")
    except Exception:
        st.warning("No database found.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to do?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Processing request..."):
        result = agent.process_request(prompt)
        
        if result["status"] == "success":
            response = result["response_text"]
            with st.expander("Show raw data"):
                st.json(result["result"])
        elif result["status"] == "idle":
            response = result["message"]
        else:
            response = f"**Error:** {result['message']}"
            
    with st.chat_message("assistant"):
        st.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})
            

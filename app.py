import streamlit as st
from orchestrator import AgentOrchestrator

# 1. Page Configuration
st.set_page_config(page_title="Personal AI Agent", page_icon="🤖", layout="wide")
st.title("🤖 Personal AI Agent - Free Local Orchestrator")

# 2. Get API Key directly inside the UI
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = ""

api_key_input = st.text_input(
    "🔑 Enter your Gemini API Key:", 
    type="password", 
    value=st.session_state["gemini_api_key"]
)

if api_key_input:
    st.session_state["gemini_api_key"] = api_key_input

if not st.session_state["gemini_api_key"]:
    st.info("⚠️ Please enter your Gemini API Key to proceed.")
else:
    # Initialize the agent with the provided API key
    @st.cache_resource
    def init_agent(key):
        return AgentOrchestrator(key)

    agent = init_agent(st.session_state["gemini_api_key"])

    # Initialize Message History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Process User Input
    if user_input := st.chat_input("Enter your command, question, or fact to remember:"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        response = agent.route_query(user_input)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

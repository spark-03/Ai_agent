import streamlit as st
from orchestrator import AgentOrchestrator

# 1. Page Configuration
st.set_page_config(page_title="Personal AI Agent", page_icon="🤖", layout="wide")
st.title("🤖 Personal AI Agent - Free Local Orchestrator")

# 2. Retrieve Gemini API Key from Streamlit Secrets
@st.cache_resource
def init_agent():
    try:
        # Reads from both possible secret key formats
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        else:
            api_key = st.secrets["gemini_api_key"]
            
        return AgentOrchestrator(api_key)
    except Exception as e:
        st.error("⚠️ GEMINI_API_KEY not found in Streamlit secrets. Please check your .streamlit/secrets.toml file.")
        return None

agent = init_agent()

if agent:
    # 3. Initialize Message History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 4. Process User Input
    if user_input := st.chat_input("Enter your command, question, or fact to remember:"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        response = agent.route_query(user_input)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

import streamlit as st
from orchestrator import AgentOrchestrator

# 1. Page Configuration
st.set_page_config(page_title="Personal AI Agent", page_icon="🤖", layout="wide")
st.title("🤖 Personal AI Agent - Free Local Orchestrator")

# 2. Retrieve all keys automatically from Streamlit Secrets
@st.cache_resource
def init_agent():
    try:
        # Get Gemini API key
        api_key = st.secrets.get("GEMINI_API_KEY", st.secrets.get("gemini_api_key", ""))
        
        # Get Twilio credentials
        twilio_sid = st.secrets.get("TWILIO_ACCOUNT_SID", "")
        twilio_token = st.secrets.get("TWILIO_AUTH_TOKEN", "")
        twilio_from = st.secrets.get("TWILIO_WHATSAPP_FROM", "")
        twilio_to = st.secrets.get("TWILIO_WHATSAPP_TO", "")
        
        return AgentOrchestrator(
            gemini_api_key=api_key,
            twilio_sid=twilio_sid,
            twilio_token=twilio_token,
            twilio_from=twilio_from,
            twilio_to=twilio_to
        )
    except Exception as e:
        st.error("⚠️ Error initializing agent. Please check your .streamlit/secrets.toml file.")
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

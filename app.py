import streamlit as st
from orchestrator import Orchestrator

# Page Configuration
st.set_page_config(page_title="Ultimate AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 Ultimate Personal AI Assistant")

# Initialize persistent session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

orchestrator = Orchestrator()

def main():
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose Module", [
        "Chat Assistant",
        "Document & Data Analyzer",
        "Math Problem-Solving",
        "Math Quiz Generator",
        "Financial Analyzer",
        "Task Execution Engine",
        "Context-Aware WhatsApp Agent",
        "Location & Weather Hub"
    ])
    
    if not orchestrator.client:
        st.error("Client initialization failed. Please check your GEMINI_API_KEY secret.")
    else:
        if app_mode == "Chat Assistant":
            orchestrator.render_chat_assistant()
        elif app_mode == "Document & Data Analyzer":
            orchestrator.render_doc_analyzer()
        elif app_mode == "Math Problem-Solving":
            orchestrator.render_math_solver()
        elif app_mode == "Math Quiz Generator":
            orchestrator.render_math_quiz()
        elif app_mode == "Financial Analyzer":
            orchestrator.render_financial_analyzer()
        elif app_mode == "Task Execution Engine":
            orchestrator.render_task_engine()
        elif app_mode == "Context-Aware WhatsApp Agent":
            orchestrator.render_whatsapp_agent()
        elif app_mode == "Location & Weather Hub":
            orchestrator.render_location_weather()

if __name__ == '__main__':
    main()

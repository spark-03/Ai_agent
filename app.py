import streamlit as st
from orchestrator import Orchestrator

st.set_page_config(page_title="AI Orchestrator", page_icon="🤖")

st.title("🤖 Personal AI Orchestrator Agent")
st.write("Built on Streamlit & Gemini - 100% Free Tier")

# Initialize orchestrator
orchestrator = Orchestrator()

# User input field
user_input = st.text_input("What is your task or question today?")

if st.button("Execute"):
    if user_input:
        with st.spinner("Orchestrating..."):
            # 1. Determine Intent
            intent = orchestrator.determine_intent(user_input)
            
            # 2. Generate Result
            result = orchestrator.route_task(intent, user_input)
            
            # Display results
            st.success("Task completed successfully!")
            st.info(f"**Detected Intent:** {intent}")
            
            st.markdown("### Response:")
            st.write(result)
    else:
        st.warning("Please enter a task or question first.")

import streamlit as st
from orchestrator import orchestrator

st.set_page_config(page_title="AI Agent", layout="centered")

st.title("🤖 AI Agent (Orchestrator v1)")

st.write("Enter your request below:")

user_input = st.text_area("Your Input", height=120)

if st.button("Run"):

    if not user_input.strip():
        st.warning("Please enter something.")
    else:
        with st.spinner("Thinking..."):
            output = orchestrator(user_input)

        st.subheader("Output:")
        st.write(output)
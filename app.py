import streamlit as st
from orchestrator import orchestrator

st.title("AI Agent")

user_input = st.text_input("Enter your task:")

if st.button("Run"):
    if user_input:
        output = orchestrator(user_input)
        st.write(output)
    else:
        st.warning("Please enter something.")
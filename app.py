import streamlit as st
from orchestrator import Orchestrator

st.set_page_config(page_title="Simple Q&A Agent", page_icon="🤖")

st.title("🤖 Simple Q&A Agent")
st.write("Built on Streamlit Community Cloud and powered by Gemini.")

orchestrator = Orchestrator()

user_input = st.text_input("Ask a question or give a simple task:")

if st.button("Generate Answer"):
    if user_input:
        with st.spinner("Thinking..."):
            result = orchestrator.answer_question(user_input)
            st.markdown("### Answer:")
            st.write(result)
    else:
        st.warning("Please enter a question first.")

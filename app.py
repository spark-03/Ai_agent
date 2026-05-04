import streamlit as st
import os
from google import genai

st.set_page_config(page_title="AI Orchestrator", page_icon="🤖")

st.title("🤖 Chat Agent")
st.write("Powered by Gemini and Streamlit Community Cloud.")

# Retrieve the API key from Streamlit secrets or environment variables
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not detected. Please add your key to Streamlit secrets.")
else:
    try:
        # Initialize the modern Gemini Client
        client = genai.Client(api_key=api_key)

        # Initialize chat history in session state
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display all past messages above the input field
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Accept user input at the bottom of the page
        if prompt := st.chat_input("Ask a question or give a simple task:"):
            # Display user's question
            with st.chat_message("user"):
                st.write(prompt)
            
            # Save the question to history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate and display the answer
            with st.spinner("Thinking..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                    )
                    bot_response = response.text
                except Exception as e:
                    bot_response = f"An error occurred: {str(e)}"

            with st.chat_message("assistant"):
                st.write(bot_response)
            
            # Save the answer to history
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            # Rerun the app to update the UI instantly
            st.rerun()
            
    except Exception as e:
        st.error(f"Error initializing or running the client: {e}")

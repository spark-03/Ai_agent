import streamlit as st
from orchestrator import Orchestrator

st.set_page_config(page_title="AI Orchestrator", page_icon="🤖")

st.title("🤖 Chat Agent with WhatsApp")
st.write("Powered by Gemini, Twilio, and Streamlit Community Cloud.")

# Initialize the orchestrator
orchestrator = Orchestrator()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all past messages above the input field
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Accept user input at the bottom
if prompt := st.chat_input("Ask a question, or say 'send hi to my whatsapp number'"):
    # Display user's question
    with st.chat_message("user"):
        st.write(prompt)
    
    # Save the question to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Processing..."):
        # Call the orchestrator to do the processing logic
        bot_response = orchestrator.process_request(prompt)

    # Display and store output
    with st.chat_message("assistant"):
        st.write(bot_response)
    
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Rerun the app to update the UI instantly
    st.rerun()

import streamlit as st
import os
from google import genai
from twilio.rest import Client

st.set_page_config(page_title="AI Orchestrator", page_icon="🤖")

st.title("🤖 Chat Agent with WhatsApp")
st.write("Powered by Gemini, Twilio, and Streamlit Community Cloud.")

# Retrieve secrets
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
account_sid = os.getenv("TWILIO_ACCOUNT_SID") or st.secrets.get("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN") or st.secrets.get("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM_NUMBER") or st.secrets.get("TWILIO_FROM_NUMBER")
to_number = os.getenv("TWILIO_TO_NUMBER") or st.secrets.get("TWILIO_TO_NUMBER")

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

        # Accept user input at the bottom
        if prompt := st.chat_input("Ask a question, or say 'send hi to my whatsapp number'"):
            # Display user's question
            with st.chat_message("user"):
                st.write(prompt)
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Intent Determination for WhatsApp
            prompt_lower = prompt.lower()
            if "send" in prompt_lower and "whatsapp" in prompt_lower:
                with st.spinner("Sending message to your WhatsApp..."):
                    if not all([account_sid, auth_token, from_number, to_number]):
                        bot_response = "❌ Error: Twilio credentials are not configured properly in secrets.toml."
                    else:
                        try:
                            # Initialize Twilio Client
                            twilio_client = Client(account_sid, auth_token)
                            
                            # Standard format for Twilio WhatsApp sandbox: whatsapp:+1... to whatsapp:+91...
                            from_whatsapp = f"whatsapp:{from_number}"
                            to_whatsapp = f"whatsapp:{to_number}"
                            
                            # Determine message content
                            message_body = "Hi" if "hi" in prompt_lower else "Hello from your AI Agent!"
                            
                            # Send message
                            twilio_client.messages.create(
                                body=message_body,
                                from_=from_whatsapp,
                                to=to_whatsapp
                            )
                            bot_response = f"✅ Success! I sent '{message_body}' to your WhatsApp number ({to_number})."
                        except Exception as e:
                            bot_response = f"❌ Failed to send WhatsApp message: {str(e)}"
                            
            else:
                # General Gemini Q&A
                with st.spinner("Thinking..."):
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt,
                        )
                        bot_response = response.text
                    except Exception as e:
                        bot_response = f"An error occurred: {str(e)}"

            # Display and store output
            with st.chat_message("assistant"):
                st.write(bot_response)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.rerun()
            
    except Exception as e:
        st.error(f"Error initializing or running the client: {e}")

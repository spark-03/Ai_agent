import os
import streamlit as st
from google import genai
from twilio.rest import Client

class Orchestrator:
    def __init__(self):
        # Retrieve and validate keys
        self.api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID") or st.secrets.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN") or st.secrets.get("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER") or st.secrets.get("TWILIO_FROM_NUMBER")
        self.to_number = os.getenv("TWILIO_TO_NUMBER") or st.secrets.get("TWILIO_TO_NUMBER")

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def determine_intent(self, prompt: str) -> str:
        """
        Determines the user intent deterministically without errors.
        """
        text = prompt.lower()
        if "send" in text and "whatsapp" in text:
            return "WHATSAPP"
        else:
            return "GENERATE"

    def process_request(self, prompt: str) -> str:
        """
        Routes the request to the appropriate method based on the intent.
        """
        intent = self.determine_intent(prompt)
        
        if intent == "WHATSAPP":
            return self._send_whatsapp(prompt)
        else:
            return self._generate_gemini(prompt)

    def _generate_gemini(self, prompt: str) -> str:
        """Handles standard questions and tasks via Gemini."""
        if not self.client:
            return "❌ Error: Gemini API key not detected. Please add your key to Streamlit secrets."
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def _send_whatsapp(self, prompt: str) -> str:
        """Handles sending messages through Twilio."""
        if not all([self.account_sid, self.auth_token, self.from_number, self.to_number]):
            return "❌ Error: Twilio credentials are not configured properly in Streamlit secrets."

        try:
            twilio_client = Client(self.account_sid, self.auth_token)
            
            # Formats numbers correctly
            from_whatsapp = f"whatsapp:{self.from_number}"
            to_whatsapp = f"whatsapp:{self.to_number}"
            
            # Determine message body
            text = prompt.lower()
            message_body = "Hi" if "hi" in text else "Hello from your AI Agent!"
            
            twilio_client.messages.create(
                body=message_body,
                from_=from_whatsapp,
                to=to_whatsapp
            )
            
            return f"✅ Success! I sent '{message_body}' to your WhatsApp number ({self.to_number})."
        except Exception as e:
            return f"Twilio Error: {str(e)}"

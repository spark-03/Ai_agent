import os
import streamlit as st
from google import genai

class Orchestrator:
    def __init__(self):
        # Get the API key from Streamlit secrets or environment variables
        api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        
        if not api_key:
            st.error("Gemini API key not detected. Please add your key to Streamlit secrets.")
            self.client = None
        else:
            # Initialize the modern Gemini Client
            self.client = genai.Client(api_key=api_key)
            self.model = "gemini-2.5-flash"

    def answer_question(self, user_prompt: str) -> str:
        if not self.client:
            return "Initialization failed. Check your API key."
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
            )
            return response.text
        except Exception as e:
            return f"An error occurred: {str(e)}"

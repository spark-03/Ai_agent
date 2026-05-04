import os
import google.generativeai as genai
import streamlit as st

class Orchestrator:
    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            st.error("API Key not found. Please check your secrets.toml.")
        else:
            genai.configure(api_key=api_key)
            # Use the fast, free-tier model
            self.model = genai.GenerativeModel("gemini-2.5-flash")

    def determine_intent(self, user_prompt: str) -> str:
        """
        Analyzes the user's prompt and classifies the intent, returning just the category.
        """
        intent_prompt = f"""
        You are an intelligent, lightweight AI orchestrator. 
        Analyze the user's input and determine their intent. Classify it into one of the following exact categories:
        - CODING: If the user asks for code, debugging, or programming concepts.
        - MATH: If the user asks for math equations, calculations, or problem-solving.
        - GENERAL: For general knowledge, chit-chat, or simple questions.
        - SEARCH: If the user explicitly asks to retrieve information, facts, or news.

        Respond ONLY with the category name. Do not add any punctuation or extra text.

        User Input: {user_prompt}
        """
        
        response = self.model.generate_content(intent_prompt)
        return response.text.strip().upper()

    def route_task(self, intent: str, user_prompt: str) -> str:
        """
        Routes the task to the appropriate context instructions based on intent.
        """
        if intent == "MATH":
            system_instruction = "You are an expert math tutor. Solve the problem step-by-step with clear explanations."
        elif intent == "CODING":
            system_instruction = "You are a senior software developer. Provide clean, well-commented code in Python or the appropriate language."
        elif intent == "SEARCH":
            system_instruction = "Provide clear, factual, and direct answers to the user's request."
        else:
            system_instruction = "You are a helpful assistant."

        # Pass the prompt along with the system instruction
        chat = self.model.start_chat(history=[])
        response = self.model.generate_content(
            f"{system_instruction}\n\nTask: {user_prompt}"
        )
        return response.text

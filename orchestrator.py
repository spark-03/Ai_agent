import google.generativeai as genai
import streamlit as st

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

def call_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"
ALLOWED_INTENTS = [
    "general_qa",
    "code_generation",
    "task_execution",
    "information_lookup"
]
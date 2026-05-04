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
def classify_intent(user_input):
    prompt = f"""
You are an AI intent classifier.

Classify the user's input into EXACTLY ONE of these categories:
- general_qa
- code_generation
- task_execution
- information_lookup

Rules:
- Return ONLY the category name
- No explanation
- No extra words

User input: {user_input}
"""

    result = call_gemini(prompt).lower().strip()

    # Safety check (VERY IMPORTANT)
    if result not in ALLOWED_INTENTS:
        return "general_qa"

    return result
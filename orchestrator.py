import google.generativeai as genai
import streamlit as st

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")

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

def handle_general_qa(user_input):
    return call_gemini(user_input)


def handle_code(user_input):
    prompt = f"Write clean and correct code for:\n{user_input}"
    return call_gemini(prompt)


def handle_task(user_input):
    prompt = f"""
Break this task into steps and solve it clearly:

Task: {user_input}
"""
    return call_gemini(prompt)


def handle_info(user_input):
    prompt = f"Provide accurate information:\n{user_input}"
    return call_gemini(prompt)

def orchestrator(user_input):
    intent = classify_intent(user_input)

    if intent == "general_qa":
        return handle_general_qa(user_input)

    elif intent == "code_generation":
        return handle_code(user_input)

    elif intent == "task_execution":
        return handle_task(user_input)

    elif intent == "information_lookup":
        return handle_info(user_input)

    else:
        return "Something went wrong."

from google import genai
import streamlit as st
import json

# ==============================
# CONFIGURATION
# ==============================

# Initialize client safely
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    raise Exception(f"API KEY ERROR: {str(e)}")

# Use a stable model (no guessing)
MODEL_NAME = "gemini-2.0-flash"

# Allowed intents (strict control)
ALLOWED_INTENTS = [
    "general_qa",
    "code_generation",
    "task_execution",
    "information_lookup"
]


# ==============================
# SAFE GEMINI CALL
# ==============================

def call_gemini(prompt):
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not response.text:
            return "ERROR: Empty response from model"

        return response.text.strip()

    except Exception as e:
        return f"ERROR: {str(e)}"


# ==============================
# INTENT CLASSIFIER (STRUCTURED)
# ==============================

def classify_intent(user_input):
    prompt = f"""
You are an AI intent classifier.

Return ONLY valid JSON:
{{"intent": "<one_of_allowed_intents>"}}

Allowed intents:
- general_qa
- code_generation
- task_execution
- information_lookup

Rules:
- No explanation
- No extra text
- Only JSON

User input: {user_input}
"""

    result = call_gemini(prompt)

    # Safe parsing
    try:
        data = json.loads(result)
        intent = data.get("intent", "").strip()

        if intent in ALLOWED_INTENTS:
            return intent
        else:
            return "general_qa"

    except Exception:
        return "general_qa"


# ==============================
# HANDLERS
# ==============================

def handle_general_qa(user_input):
    return call_gemini(user_input)


def handle_code(user_input):
    prompt = f"""
Write clean, correct, and efficient code.

Task:
{user_input}

Rules:
- Provide only code
- No explanation unless necessary
"""
    return call_gemini(prompt)


def handle_task(user_input):
    prompt = f"""
Break this task into clear steps and solve it.

Task:
{user_input}
"""
    return call_gemini(prompt)


def handle_info(user_input):
    prompt = f"""
Provide accurate and factual information.

Query:
{user_input}
"""
    return call_gemini(prompt)


# ==============================
# MAIN ORCHESTRATOR
# ==============================

def orchestrator(user_input):
    if not user_input or not user_input.strip():
        return "Please enter a valid input."

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
        return "ERROR: Unknown intent"
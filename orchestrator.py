import os
import json
from datetime import datetime
from google import genai
from twilio.rest import Client

class AgentOrchestrator:
    def __init__(self, gemini_api_key, **kwargs):
        """Initializes the local memory engine, Gemini AI, and Twilio client.
        Accepts **kwargs to prevent unexpected argument errors."""
        self.data_folder = "agent_data"
        self.memory_file = os.path.join(self.data_folder, "memory.json")
        
        # Initialize Gemini API Client
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        
        # Safely extract Twilio credentials from kwargs
        self.twilio_sid = kwargs.get("twilio_sid")
        self.twilio_token = kwargs.get("twilio_token")
        self.twilio_from = kwargs.get("twilio_from")
        self.twilio_to = kwargs.get("twilio_to")
        
        if self.twilio_sid and self.twilio_token:
            try:
                self.twilio_client = Client(self.twilio_sid, self.twilio_token)
            except Exception:
                self.twilio_client = None
        else:
            self.twilio_client = None
        
        # Ensure the target folder exists
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            
        # Create an empty memory file if it does not exist
        if not os.path.exists(self.memory_file):
            self._save_data({})

    def _load_data(self):
        """Helper to read data from the local JSON file."""
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_data(self, data):
        """Helper to write data to the JSON file."""
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=4)

    def remember_fact(self, key: str, value: str):
        """Saves a fact to the local storage."""
        try:
            data = self._load_data()
            data[key.lower()] = {
                "original_key": key,
                "value": value,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_data(data)
            return True
        except Exception:
            return False

    def recall_fact(self, key_query: str):
        """Recalls a fact from the local storage."""
        try:
            data = self._load_data()
            key_query_lower = key_query.lower()
            for k, v in data.items():
                if key_query_lower in k or k in key_query_lower:
                    return v["value"]
            return None
        except Exception:
            return None

    def send_whatsapp_message(self, message_text: str):
        """Sends a message using the Twilio API."""
        if not self.twilio_client or not self.twilio_from or not self.twilio_to:
            return "⚠️ Twilio credentials are not set or incomplete in your secrets."
        
        try:
            message = self.twilio_client.messages.create(
                body=message_text,
                from_=f"whatsapp:{self.twilio_from}",
                to=f"whatsapp:{self.twilio_to}"
            )
            return f"✅ **Message sent to your WhatsApp number!** (ID: {message.sid})"
        except Exception as e:
            return f"⚠️ **Twilio Error:** {str(e)}"

    def route_query(self, user_input: str):
        """Intent classifier and orchestrator router."""
        user_input_lower = user_input.lower()
        response = ""

        # Intent 1: Send WhatsApp Message Intent (Strict Keyword Matching)
        whatsapp_prefixes = ["send to my whatsapp number", "send me a message", "send a message"]
        matched_prefix = None
        
        for p in whatsapp_prefixes:
            if user_input_lower.startswith(p) or p in user_input_lower:
                matched_prefix = p
                break

        if matched_prefix:
            idx = user_input_lower.find(matched_prefix) + len(matched_prefix)
            message_content = user_input[idx:].strip()
            
            if message_content.startswith("that "):
                message_content = message_content[5:].strip()
            if message_content.startswith(": "):
                message_content = message_content[2:].strip()
            
            if message_content:
                response = self.send_whatsapp_message(message_content)
            else:
                response = "⚠️ **Invalid format:** Please include the message text. Example: `send me a message [message]`"

        # Intent 2: Write/Save Intent
        elif user_input_lower.startswith("remember "):
            parts = user_input.split(" is ")
            if len(parts) == 2:
                key = parts[0].replace("remember ", "").strip()
                val = parts[1].strip()
                if self.remember_fact(key, val):
                    response = f"✅ **Saved to {self.data_folder}:** I will remember that `{key}` is `{val}`."
                else:
                    response = "⚠️ Failed to save fact to file."
            else:
                response = "⚠️ **Invalid Format:** Please use `Remember [key] is [value]`"

        # Intent 3: Read/Recall Intent
        elif user_input_lower.startswith("do you remember ") or user_input_lower.startswith("tell me about "):
            key = user_input.replace("do you remember", "").replace("tell me about", "").strip()
            result = self.recall_fact(key)
            if result:
                response = f"🧠 **Fact Recalled:** {key} is **{result}**."
            else:
                response = f"❌ I could not find anything about `{key}` in your local memory."

        # Intent 4: General Query Intent (Gemini Fallback)
        else:
            try:
                chat_response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"You are a personal AI Agent. Keep responses concise. User input: {user_input}"
                )
                response = chat_response.text
            except Exception:
                response = f"🤖 **Orchestrator (Fallback):** You said: {user_input}"

        return response

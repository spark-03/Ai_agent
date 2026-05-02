import os
import json
from datetime import datetime
from google import genai

class AgentOrchestrator:
    def __init__(self, gemini_api_key):
        """Initializes the local memory engine in a specific folder and sets up Gemini AI."""
        self.data_folder = "agent_data"
        self.memory_file = os.path.join(self.data_folder, "memory.json")
        
        # Initialize Gemini API Client
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        
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
        """Helper to write data to the local JSON file."""
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=4)

    def remember_fact(self, key: str, value: str):
        """Saves a fact to the specific folder's memory file."""
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
        """Recalls a fact from the specific folder's memory file."""
        try:
            data = self._load_data()
            key_query_lower = key_query.lower()
            
            # Search for a match in the keys
            for k, v in data.items():
                if key_query_lower in k or k in key_query_lower:
                    return v["value"]
            return None
        except Exception:
            return None

    def route_query(self, user_input: str):
        """Processes user input, updating memory or forwarding to Gemini."""
        user_input_lower = user_input.lower()
        response = ""

        if user_input_lower.startswith("remember "):
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

        elif user_input_lower.startswith("do you remember ") or user_input_lower.startswith("tell me about "):
            key = user_input.replace("do you remember", "").replace("tell me about", "").strip()
            result = self.recall_fact(key)
            if result:
                response = f"🧠 **Fact Recalled:** {key} is **{result}**."
            else:
                response = f"❌ I could not find anything about `{key}` in your local memory."

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

import os
from google import genai

# Replace with your actual key if not using an environment variable
API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_YOUR_API_KEY_HERE")

if not API_KEY or API_KEY == "PASTE_YOUR_API_KEY_HERE":
    print("⚠️ Please set your API key in the verify_connection.py script.")
else:
    try:
        print("Initializing Gemini Client...")
        client = genai.Client(api_key=API_KEY)
        
        print("Sending test prompt...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Calculate 5+2 and tell me the result."
        )
        print("\n✅ Connection Successful!")
        print(f"Gemini Response: {response.text}")
    except Exception as e:
        print(f"\n❌ Connection Failed. Error Details: {e}")

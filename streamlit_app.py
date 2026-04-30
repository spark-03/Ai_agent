import streamlit as st
from google import genai

st.set_page_config(page_title="My AI Agent", page_icon="🤖")
st.title("🤖 My Personal AI Assistant")

try:
    # Automatically retrieve the API key from Streamlit cloud secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
    user_prompt = st.text_area("How can I help you today?")
    
    if st.button("Generate"):
        if user_prompt:
            # Generate response
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt
            )
            st.write("### Response:")
            st.write(response.text)
            
except Exception as e:
    st.error("Configuration issue detected. Please make sure your GEMINI_API_KEY is saved in Streamlit secrets.")

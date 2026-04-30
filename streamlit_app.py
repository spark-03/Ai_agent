
import streamlit as st
from google import genai

st.set_page_config(page_title="My AI Agent", page_icon="🤖")
st.title("🤖 My Personal AI Assistant")

# Secure input for your Gemini API key
api_key = st.text_input("Enter your Gemini API Key", type="password")

if api_key:
    try:
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
        st.error(f"Please check your API key or connection.")
else:
    st.info("Please enter your API key to proceed.")
              

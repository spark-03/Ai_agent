import streamlit as st
import os
from google import genai

st.set_page_config(page_title="Simple Q&A Agent", page_icon="🤖")

st.title("🤖 Simple Q&A Agent")
st.write("Built on Streamlit Community Cloud and powered by Gemini.")

# Retrieve the API key from Streamlit secrets or environment variables
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not detected. Please add your key to Streamlit secrets.")
else:
    try:
        # Initialize the modern Gemini Client
        client = genai.Client(api_key=api_key)
        
        user_input = st.text_input("Ask a question or give a simple task:")

        if st.button("Generate Answer"):
            if user_input:
                with st.spinner("Thinking..."):
                    # Generate response using the modern GenAI SDK
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=user_input,
                    )
                    st.markdown("### Answer:")
                    st.write(response.text)
            else:
                st.warning("Please enter a question first.")
                
    except Exception as e:
        st.error(f"Error initializing or running the client: {e}")

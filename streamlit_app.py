import streamlit as st
import pandas as pd
from google import genai

st.set_page_config(page_title="My AI Agent", page_icon="🤖", layout="wide")
st.title("🤖 My Personal AI Assistant")

# Initialize persistent chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    # Retrieve securely stored API key
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
    # Sidebar navigation for features
    st.sidebar.title("🛠️ Tools & Modules")
    module = st.sidebar.selectbox(
        "Choose an action hub:",
        ["Chat Assistant", "Document & Data Analyzer", "Math Problem-Solving Module"]
    )

    # 1. Chat Assistant Module
    if module == "Chat Assistant":
        st.subheader("Chat Assistant (with Memory)")
        
        # Display history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        if user_input := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
                
            try:
                # Format memory for the model
                contents = []
                for m in st.session_state.messages:
                    role_prefix = "You" if m["role"] == "user" else "Agent"
                    contents.append(f"{role_prefix}: {m['content']}")
                    
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="\n".join(contents)
                )
                
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                with st.chat_message("assistant"):
                    st.write(response.text)
            except Exception as e:
                st.error("Failed to generate response. Check your API limit or connection.")
                
    # 2. Document and Data Analyzer Module
    elif module == "Document & Data Analyzer":
        st.subheader("Document & Data Analyzer")
        uploaded_file = st.file_uploader("Upload a file (.txt or .csv)", type=["txt", "csv"])
        
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".txt"):
                file_content = uploaded_file.read().decode("utf-8")
                st.text_area("File Content:", file_content, height=120)
                
                prompt = st.text_input("Ask a question about the text:")
                if st.button("Analyze Text"):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"Given this content:\n{file_content}\n\nAnswer the question: {prompt}"
                    )
                    st.write("### Analysis Result:")
                    st.write(response.text)
                    
            elif uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head(10))
                
                prompt = st.text_input("Ask about this dataset (e.g., summarize columns or calculate totals):")
                if st.button("Analyze Data"):
                    data_slice = df.head(50).to_string()
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"Dataset sample:\n{data_slice}\n\nTask: {prompt}"
                    )
                    st.write("### Data Analysis Result:")
                    st.write(response.text)

    # 3. Math & Problem-Solving Module
    elif module == "Math Problem-Solving Module":
        st.subheader("Math Problem-Solving Module")
        problem_input = st.text_area("Type your equation or problem statement:", height=100)
        
        step_by_step = st.checkbox("Include step-by-step working out", value=True)
        
        if st.button("Solve Problem"):
            if problem_input:
                instruction = "Provide a structured solution."
                if step_by_step:
                    instruction = "Provide the steps sequentially and output the final answer."
                    
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{instruction}\n\nProblem:\n{problem_input}"
                )
                st.write("### Solution:")
                st.write(response.text)
                
except Exception as e:
    st.error("Please configure your API credentials in the Streamlit app settings.")

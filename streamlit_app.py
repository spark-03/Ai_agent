import streamlit as st
import pandas as pd
from google import genai
import io

st.set_page_config(page_title="Ultimate AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 Ultimate Personal AI Assistant")

# Initialize persistent session state for memory and file uploads
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

try:
    # Retrieve securely stored API key
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
    # Sidebar navigation for features
    st.sidebar.title("🛠️ Tools & Modules")
    module = st.sidebar.selectbox(
        "Choose an action hub:",
        [
            "Chat Assistant",
            "Document & Data Analyzer",
            "Math Problem-Solving Module",
            "Math Worksheet & Quiz Generator",
            "Financial Data Analyzer"
        ]
    )

    # 1. Chat Assistant Module
    if module == "Chat Assistant":
        st.subheader("Chat Assistant")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        if user_input := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
                
            try:
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
                st.error("Failed to generate response. Please check your API limits or connection.")

    # 2. Document and Data Analyzer Module (Persistent)
    elif module == "Document & Data Analyzer":
        st.subheader("Document & Data Analyzer")
        
        uploaded_file = st.file_uploader("Upload a file (.txt or .csv)", type=["txt", "csv"])
        
        if uploaded_file is not None:
            st.session_state.uploaded_file_data = uploaded_file.read()
            st.session_state.uploaded_file_name = uploaded_file.name
        elif st.session_state.uploaded_file_data is not None:
            st.info(f"Using previously uploaded file: {st.session_state.uploaded_file_name}")
            
        if st.session_state.uploaded_file_data is not None:
            if st.session_state.uploaded_file_name.endswith(".txt"):
                file_content = st.session_state.uploaded_file_data.decode("utf-8")
                st.text_area("File Content:", file_content, height=100)
                
                prompt = st.text_input("Ask a question about the text:")
                if st.button("Analyze Text"):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"Given this content:\n{file_content}\n\nTask: {prompt}"
                    )
                    st.write("### Analysis Result:")
                    st.write(response.text)
                    
            elif st.session_state.uploaded_file_name.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(st.session_state.uploaded_file_data))
                st.dataframe(df.head(10))
                
                prompt = st.text_input("Ask about this dataset:")
                if st.button("Analyze Data"):
                    data_slice = df.head(50).to_string()
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"Dataset sample:\n{data_slice}\n\nTask: {prompt}"
                    )
                    st.write("### Data Analysis Result:")
                    st.write(response.text)

    # 3. Math Problem-Solving Module
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

    # 4. Math Worksheet & Quiz Generator
    elif module == "Math Worksheet & Quiz Generator":
        st.subheader("Math Worksheet & Quiz Generator")
        topic = st.text_input("Topic/Concept (e.g., Quadratic Equations, Arithmetic Progressions):")
        difficulty = st.selectbox("Select Difficulty:", ["Easy", "Medium", "Hard"])
        num_questions = st.slider("Number of questions to generate:", min_value=3, max_value=10, value=5)
        
        if st.button("Generate Worksheet"):
            if topic:
                prompt = f"Generate {num_questions} math problems on the topic '{topic}' with a '{difficulty}' difficulty level. Provide the complete answer key separately at the bottom."
                with st.spinner("Generating worksheet..."):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    st.write("### Generated Worksheet:")
                    st.write(response.text)

    # 5. Financial Data Analyzer
    elif module == "Financial Data Analyzer":
        st.subheader("Financial Data Analyzer")
        symbol = st.text_input("Enter Ticker Symbol:", "RELIANCE.NS")
        analysis_type = st.selectbox("Select Analysis Type:", ["Intrinsic Value Calculator", "Basic Trend Analysis", "Custom Metric Calculation"])
        
        if st.button("Analyze Financial Data"):
            if symbol:
                prompt = f"Perform a {analysis_type} analysis for the ticker {symbol}. Provide data insights and calculations in a clear, structured format."
                with st.spinner("Analyzing financial data..."):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    st.write("### Financial Analysis Result:")
                    st.write(response.text)
                    
except Exception as e:
    st.error("Please configure your GEMINI_API_KEY in the Streamlit cloud settings.")
        

import streamlit as st
import pandas as pd
from google import genai
import io
import requests
from bs4 import BeautifulSoup

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
            "Financial Data Analyzer",
            "Task Execution Engine",
            "Web Scraper Module"
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

    # 6. Task Execution Engine
    elif module == "Task Execution Engine":
        st.subheader("Task Execution Engine")
        task_type = st.selectbox(
            "Select Task Type:", 
            ["EMI Calculator", "Dataset Statistical Engine", "Currency Converter", "Unit Converter"]
        )
        
        if task_type == "EMI Calculator":
            st.write("#### Calculate Loan EMIs")
            p = st.number_input("Principal Amount (Rs/$):", value=50000.0)
            r = st.number_input("Annual Interest Rate (%):", value=8.5)
            t = st.number_input("Tenure (Years):", value=5)
            
            if st.button("Run Calculation"):
                r_month = r / (12 * 100)
                months = t * 12
                if r_month > 0:
                    emi = (p * r_month * (1 + r_month)**months) / ((1 + r_month)**months - 1)
                    total_amount = emi * months
                    total_interest = total_amount - p
                    st.success("Calculation Successful!")
                    st.metric(label="Calculated Monthly EMI", value=f"{emi:,.2f}")
                    st.write(f"**Total Interest Payable:** {total_interest:,.2f}")
                    st.write(f"**Total Amount Payable:** {total_amount:,.2f}")
                else:
                    st.error("Interest rate must be greater than zero.")
                    
        elif task_type == "Dataset Statistical Engine":
            st.write("#### CSV File Statistics & Processing")
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                st.write("Dataset Sample:", df.head())
                
                col_to_analyze = st.selectbox("Select column to analyze:", df.columns)
                if st.button("Compute Statistics"):
                    if pd.api.types.is_numeric_dtype(df[col_to_analyze]):
                        st.write("#### Statistics for:", col_to_analyze)
                        stats = df[col_to_analyze].describe()
                        st.dataframe(stats)
                        
                        csv_data = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Processed CSV",
                            data=csv_data,
                            file_name='processed_dataset.csv',
                            mime='text/csv'
                        )
                    else:
                        st.error("Selected column is not numeric. Please select a numerical column.")

        elif task_type == "Currency Converter":
            st.write("#### Currency Converter")
            amount = st.number_input("Amount:", value=100.0)
            from_curr = st.selectbox("From Currency:", ["USD", "EUR", "INR", "GBP"])
            to_curr = st.selectbox("To Currency:", ["INR", "USD", "EUR", "GBP"])
            
            rates = {
                "USD_INR": 83.50, "INR_USD": 1/83.50,
                "EUR_INR": 89.50, "INR_EUR": 1/89.50,
                "USD_EUR": 0.93, "EUR_USD": 1/0.93,
                "GBP_INR": 104.50, "INR_GBP": 1/104.50,
                "USD_GBP": 0.80, "GBP_USD": 1/0.80,
                "EUR_GBP": 0.86, "GBP_EUR": 1/0.86,
                "USD_USD": 1.0, "INR_INR": 1.0, 
                "EUR_EUR": 1.0, "GBP_GBP": 1.0
            }
            
            if st.button("Convert Currency"):
                key = f"{from_curr}_{to_curr}"
                if key in rates:
                    converted = amount * rates[key]
                    st.success(f"Converted Amount: {converted:,.2f} {to_curr}")
                else:
                    st.error("Conversion rate not available.")

        elif task_type == "Unit Converter":
            st.write("#### Unit Converter")
            unit_type = st.selectbox("Select Unit Type:", ["Length", "Weight"])
            
            if unit_type == "Length":
                val = st.number_input("Value:", value=1.0)
                from_unit = st.selectbox("From Unit:", ["Meters", "Kilometers", "Centimeters", "Inches"])
                to_unit = st.selectbox("To Unit:", ["Kilometers", "Meters", "Centimeters", "Inches"])
                
                to_meters = {
                    "Meters": 1.0,
                    "Kilometers": 1000.0,
                    "Centimeters": 0.01,
                    "Inches": 0.0254
                }
                
                if st.button("Convert Length"):
                    val_in_meters = val * to_meters[from_unit]
                    res = val_in_meters / to_meters[to_unit]
                    st.success(f"Result: {res:.4f} {to_unit}")
                    
            elif unit_type == "Weight":
                val = st.number_input("Value:", value=1.0)
                from_unit = st.selectbox("From Unit:", ["Kilograms", "Grams", "Pounds", "Ounces"])
                to_unit = st.selectbox("To Unit:", ["Grams", "Kilograms", "Pounds", "Ounces"])
                
                to_kg = {
                    "Kilograms": 1.0,
                    "Grams": 0.001,
                    "Pounds": 0.453592,
                    "Ounces": 0.0283495
                }
                
                if st.button("Convert Weight"):
                    val_in_kg = val * to_kg[from_unit]
                    res = val_in_kg / to_kg[to_unit]
                    st.success(f"Result: {res:.4f} {to_unit}")

    # 7. Web Scraper Module
    elif module == "Web Scraper Module":
        st.subheader("Web Scraper Module")
        url_input = st.text_input("Enter Website URL (include https://):", "https://example.com")
        tag_type = st.selectbox("Select HTML Tag to scrape:", ["h1", "h2", "h3", "p", "title"])
        
        if st.button("Scrape Website"):
            if url_input:
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(url_input, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, "html.parser")
                        elements = soup.find_all(tag_type)
                        
                        st.success(f"Scraped successfully from {url_input}!")
                        st.write(f"**Found {len(elements)} {tag_type} elements:**")
                        for idx, element in enumerate(elements[:10]):
                            st.text(f"{idx+1}: {element.get_text(strip=True)}")
                    else:
                        st.error(f"Failed to load website. Status code: {response.status_code}")
                except Exception as e:
                    st.error(f"Error scraping the website: {e}")

except Exception as e:
    st.error("Please configure your GEMINI_API_KEY in the Streamlit cloud settings.")
                        

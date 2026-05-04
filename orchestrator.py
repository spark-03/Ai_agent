import streamlit as st
import pandas as pd
import io
import requests
import re
from streamlit_geolocation import streamlit_geolocation
from orchestrator import Orchestrator

# Page Configuration
st.set_page_config(page_title="Ultimate AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 Ultimate Personal AI Assistant")

# Initialize persistent session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

orchestrator = Orchestrator()

# --- Modular Agent Functions ---

def render_chat_assistant():
    st.subheader("Chat Assistant")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("Ask a question, check a stock, or query market movements..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        keywords = ["stock", "best", "worst", "reliance", "sbin", "tcs"]
        is_stock_query = any(word in user_input.lower() for word in keywords)

        if is_stock_query:
            with st.chat_message("assistant"):
                with st.spinner("Accessing Angel One SmartAPI..."):
                    data = orchestrator.fetch_angel_one_data(user_input)
                    if "message" in data:
                        response_text = f"**Error:** {data['message']}"
                    else:
                        response_text = (
                            f"**Market Data Retrieved via SmartAPI**\n\n"
                            f"**Symbol/Filter:** {data['symbol']}\n"
                            f"**Last Traded Price:** ₹{data['price']:,.2f}\n"
                            f"**20-Day SMA:** ₹{data['sma']:,.2f}\n"
                            f"**Technical Signal:** {data['signal']}"
                        )
                    st.write(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            try:
                contents = [f"{'You' if m['role'] == 'user' else 'Agent'}: {m['content']}" for m in st.session_state.messages]
                response = orchestrator.generate_content("\n".join(contents))
                
                ans_text = response.text
                st.session_state.messages.append({"role": "assistant", "content": ans_text})
                with st.chat_message("assistant"):
                    st.write(ans_text)
                
                task_lower = user_input.lower()
                if any(word in task_lower for word in ["whatsapp", "send", "ans", "reminder"]):
                    with st.spinner("Sending answer to WhatsApp..."):
                        try:
                            if "send" in task_lower and "whatsapp" in task_lower:
                                clean_msg = task_lower.replace("nothing", "").replace("can you", "").replace("send", "").replace("to my whatsapp", "").replace("number", "").strip()
                                message_body = clean_msg if clean_msg else ans_text
                            else:
                                message_body = f"🤖 AI Agent Task Result\n\nTask: {user_input}\nAnswer: {ans_text}"
                            
                            orchestrator.send_whatsapp_message(message_body)
                            st.success("Sent to your WhatsApp automatically!")
                        except KeyError:
                            st.error("Configuration Error: Please check Twilio Secrets in Streamlit.")
                        except Exception as e:
                            st.error(f"Failed to send message: {e}")
            except Exception as e:
                st.error(f"Failed to generate response: {e}")

def render_doc_analyzer():
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
                response = orchestrator.generate_content(f"Given this content:\n{file_content}\n\nTask: {prompt}")
                st.write("### Analysis Result:", response.text)
                
        elif st.session_state.uploaded_file_name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(st.session_state.uploaded_file_data))
            st.dataframe(df.head(10))
            prompt = st.text_input("Ask about this dataset:")
            if st.button("Analyze Data"):
                data_slice = df.head(50).to_string()
                response = orchestrator.generate_content(f"Dataset sample:\n{data_slice}\n\nTask: {prompt}")
                st.write("### Data Analysis Result:", response.text)

def render_math_solver():
    st.subheader("Math Problem-Solving Module")
    problem_input = st.text_area("Type your equation or problem statement:", height=100)
    step_by_step = st.checkbox("Include step-by-step working out", value=True)
    
    if st.button("Solve Problem"):
        if problem_input:
            instruction = "Provide the steps sequentially and output the final answer." if step_by_step else "Provide a structured solution."
            response = orchestrator.generate_content(f"{instruction}\n\nProblem:\n{problem_input}")
            st.write("### Solution:", response.text)

def render_math_quiz():
    st.subheader("Math Worksheet & Quiz Generator")
    topic = st.text_input("Topic/Concept (e.g., Quadratic Equations, Arithmetic Progressions):")
    difficulty = st.selectbox("Select Difficulty:", ["Easy", "Medium", "Hard"])
    num_questions = st.slider("Number of questions to generate:", min_value=3, max_value=10, value=5)
    
    if st.button("Generate Worksheet"):
        if topic:
            prompt = f"Generate {num_questions} math problems on the topic '{topic}' with a '{difficulty}' difficulty level. Provide the complete answer key separately at the bottom."
            with st.spinner("Generating worksheet..."):
                response = orchestrator.generate_content(prompt)
                st.write("### Generated Worksheet:", response.text)

def render_financial_analyzer():
    st.subheader("Live Financial Data Analyzer")
    symbol = st.text_input("Enter Ticker Symbol (e.g., IBM or RELIANCE.NS):", "IBM")
    
    if st.button("Fetch Real-Time Data (Free API)"):
        if symbol:
            with st.spinner("Fetching live market metrics..."):
                try:
                    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=demo"
                    response = requests.get(url, timeout=5)
                    data = response.json()
                    
                    if "Global Quote" in data and data["Global Quote"]:
                        quote = data["Global Quote"]
                        st.success(f"Market Data for {symbol}")
                        st.metric(label="Latest Price", value=f"${float(quote['05. price']):,.2f}")
                        st.write(f"**High:** {quote['03. high']} | **Low:** {quote['04. low']} | **Volume:** {quote['06. volume']}")
                    else:
                        res = orchestrator.generate_content(f"Provide a trend analysis summary for the financial asset {symbol}")
                        st.write(res.text)
                except Exception as e:
                    st.error(f"Error fetching data: {e}")

def render_task_engine():
    st.subheader("Task Execution Engine")
    task_type = st.selectbox(
        "Select Task Type:", 
        ["EMI Calculator", "Dataset Statistical Engine", "Currency Converter", "Weather & Metadata"]
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
        st.write("#### Live Currency Converter")
        amount = st.number_input("Amount to Convert:", value=100.0)
        from_curr = st.selectbox("From Currency:", ["USD", "EUR", "INR", "GBP", "JPY"], key="f_curr")
        to_curr = st.selectbox("To Currency:", ["INR", "USD", "EUR", "GBP", "JPY"], key="t_curr")
        
        if st.button("Convert Live Currency"):
            try:
                converted_val = orchestrator.convert_currency(amount, from_curr, to_curr)
                st.success(f"Converted Amount: {converted_val:,.2f} {to_curr}")
            except Exception as e:
                st.error("Error retrieving exchange rate. Check your internet connection.")

    elif task_type == "Weather & Metadata":
        st.write("#### Weather API & Metadata Hub")
        city = st.text_input("Enter city name:", "Nellore")
        
        if st.button("Check Weather"):
            try:
                w_res = orchestrator.get_weather(city)
                if w_res['cod'] == 200:
                    st.success(f"Weather in {city}:")
                    st.metric(label="Temperature (°C)", value=w_res['main']['temp'])
                    st.write(f"**Conditions:** {w_res['weather'][0]['description'].capitalize()}")
                else:
                    st.error("City not found or invalid API key.")
            except Exception:
                st.error("Failed to fetch weather data.")

def render_whatsapp_agent():
    st.subheader("🤖 Context-Aware AI WhatsApp Agent")
    task_input = st.text_input("Enter your task or command (e.g., 'Add 5 and 89 and send ans to my whatsapp'):")
    
    if st.button("Execute"):
        if task_input:
            with st.spinner("Processing task..."):
                task_lower = task_input.lower()
                
                if "add" in task_lower or "+" in task_lower:
                    numbers = [float(s) for s in re.findall(r'-?\d+\.?\d*', task_input)]
                    if numbers:
                        answer = f"The sum of {', '.join(map(str, numbers))} is {sum(numbers)}"
                    else:
                        try:
                            response = orchestrator.generate_content(task_input)
                            answer = response.text
                        except Exception as e:
                            answer = f"Error: {e}"
                else:
                    try:
                        response = orchestrator.generate_content(task_input)
                        answer = response.text
                    except Exception as e:
                        answer = f"Error: {e}"
                        
                st.info(f"**Answer:** {answer}")
                
                if any(word in task_lower for word in ["whatsapp", "send", "ans", "reminder"]):
                    try:
                        if "send" in task_lower and "to my whatsapp" in task_lower:
                            clean_msg = task_lower.replace("nothing", "").replace("can you", "").replace("send", "").replace("to my whatsapp", "").replace("number", "").strip()
                            message_body = clean_msg if clean_msg else answer
                        else:
                            message_body = f"🤖 AI Agent Task Result\n\nTask: {task_input}\nAnswer: {answer}"
                        
                        orchestrator.send_whatsapp_message(message_body)
                        st.success(f"Sent the message '{message_body}' to your WhatsApp!")
                    except KeyError:
                        st.error("Configuration Error: Please make sure MY_PHONE_NUMBER, TWILIO_ACCOUNT_SID, and TWILIO_AUTH_TOKEN are set in secrets.")
                    except Exception as e:
                        st.error(f"Failed to send message: {e}")

def render_location_weather():
    st.subheader("Weather & Location Hub")
    
    loc = streamlit_geolocation()
    if st.button("Fetch Current Location"):
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        
        if lat is not None and lon is not None:
            st.success(f"Location found! Coordinates: {lat:.4f}, {lon:.4f}")
            
            try:
                w_res = orchestrator.get_weather_by_coords(lat, lon)
                if w_res.get('cod') == 200:
                    st.metric(label="Temperature (°C)", value=w_res['main']['temp'])
                    st.write(f"**Conditions:** {w_res['weather'][0]['description'].capitalize()}")
                else:
                    st.error("Unable to fetch weather data for your location.")
            except Exception:
                st.error("Failed to fetch weather data.")

def main():
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose Module", [
        "Chat Assistant",
        "Document & Data Analyzer",
        "Math Problem-Solving",
        "Math Quiz Generator",
        "Financial Analyzer",
        "Task Execution Engine",
        "Context-Aware WhatsApp Agent",
        "Location & Weather Hub"
    ])
    
    if not orchestrator.client:
        st.error("Client initialization failed. Please check your GEMINI_API_KEY secret.")
    else:
        if app_mode == "Chat Assistant":
            render_chat_assistant()
        elif app_mode == "Document & Data Analyzer":
            render_doc_analyzer()
        elif app_mode == "Math Problem-Solving":
            render_math_solver()
        elif app_mode == "Math Quiz Generator":
            render_math_quiz()
        elif app_mode == "Financial Analyzer":
            render_financial_analyzer()
        elif app_mode == "Task Execution Engine":
            render_task_engine()
        elif app_mode == "Context-Aware WhatsApp Agent":
            render_whatsapp_agent()
        elif app_mode == "Location & Weather Hub":
            render_location_weather()

if __name__ == '__main__':
    main()

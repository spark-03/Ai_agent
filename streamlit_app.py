import streamlit as st
import pandas as pd
import io
import requests
import re
from twilio.rest import Client
from google import genai

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

try:
    # Initialize the Gemini Client using the new google-genai SDK
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
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
            "WhatsApp AI Task Agent"
        ]
    )

    # 1. Chat Assistant Module
                    # Context-Aware WhatsApp Trigger in Chat Assistant
                task_lower = user_input.lower()
                if any(word in task_lower for word in ["whatsapp", "send", "ans", "reminder"]):
                    with st.spinner("Sending answer to WhatsApp..."):
                        try:
                            phone_number = st.secrets["MY_PHONE_NUMBER"]
                            account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
                            auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
                            
                            tw_client = Client(account_sid, auth_token)
                            
                            # Extract clean message if it's a simple send command
                            if "send" in task_lower and "whatsapp" in task_lower:
                                clean_msg = task_lower.replace("nothing", "").replace("can you", "").replace("send", "").replace("to my whatsapp", "").replace("number", "").strip()
                                message_body = clean_msg if clean_msg else ans_text
                            else:
                                message_body = f"🤖 AI Agent Task Result\n\nTask: {user_input}\nAnswer: {ans_text}"
                            
                            tw_client.messages.create(
                                from_='whatsapp:+14155238886', # Twilio Sandbox Number
                                body=message_body,
                                to=f'whatsapp:{phone_number}'
                            )
                            st.success("Sent to your WhatsApp automatically based on your instruction!")
                        except KeyError:
                            st.error("Configuration Error: Please make sure MY_PHONE_NUMBER, TWILIO_ACCOUNT_SID, and TWILIO_AUTH_TOKEN are set in your secrets.")
                        except Exception as e:
                            st.error(f"Failed to send message: {e}")

    # 2. Document and Data Analyzer Module
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
                            st.write(f"**High:** {quote['03. high']} | **Low:** {quote['04. low']}")
                            st.write(f"**Volume:** {quote['06. volume']}")
                        else:
                            st.warning("API limit reached or symbol not found. Trying generation-based analysis instead...")
                            res = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=f"Provide a trend analysis summary for the financial asset {symbol}"
                            )
                            st.write(res.text)
                    except Exception as e:
                        st.error(f"Error fetching data: {e}")

    # 6. Task Execution Engine
    elif module == "Task Execution Engine":
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
            from_curr = st.selectbox("From Currency:", ["USD", "EUR", "INR", "GBP", "JPY"])
            to_curr = st.selectbox("To Currency:", ["INR", "USD", "EUR", "GBP", "JPY"])
            
            if st.button("Convert Live Currency"):
                try:
                    url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_curr}&to={to_curr}"
                    res = requests.get(url, timeout=5).json()
                    converted_val = res['rates'][to_curr]
                    st.success(f"Converted Amount: {converted_val:,.2f} {to_curr}")
                except Exception as e:
                    st.error("Error retrieving exchange rate. Check your internet connection.")

        elif task_type == "Weather & Metadata":
            st.write("#### Weather API & Metadata Hub")
            city = st.text_input("Enter city name:", "Nellore")
            
            if st.button("Check Weather"):
                try:
                    w_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=439d4b804bc8187953eb36d2a8c26f02&units=metric"
                    w_res = requests.get(w_url, timeout=5).json()
                    if w_res['cod'] == 200:
                        st.success(f"Weather in {city}:")
                        st.metric(label="Temperature (°C)", value=w_res['main']['temp'])
                        st.write(f"**Conditions:** {w_res['weather'][0]['description'].capitalize()}")
                    else:
                        st.error("City not found or invalid API key.")
                except Exception as e:
                    st.error("Failed to fetch weather data.")


        # 7. WhatsApp AI Task Agent Module
    elif module == "WhatsApp AI Task Agent":
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
                                response = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=task_input
                                )
                                answer = response.text
                            except Exception as e:
                                answer = f"Error: {e}"
                    else:
                        try:
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=task_input
                            )
                            answer = response.text
                        except Exception as e:
                            answer = f"Error: {e}"
                            
                    st.info(f"**Answer:** {answer}")
                    
                    if any(word in task_lower for word in ["whatsapp", "send", "ans", "reminder"]):
                        try:
                            phone_number = st.secrets["MY_PHONE_NUMBER"]
                            account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
                            auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
                            
                            tw_client = Client(account_sid, auth_token)
                            
                            # Extract clean message if it is a simple "send ... to whatsapp"
                            if "send" in task_lower and "to my whatsapp" in task_lower:
                                clean_msg = task_lower.replace("nothing", "").replace("can you", "").replace("send", "").replace("to my whatsapp", "").replace("number", "").strip()
                                message_body = clean_msg if clean_msg else answer
                            else:
                                message_body = f"🤖 AI Agent Task Result\n\nTask: {task_input}\nAnswer: {answer}"
                            
                            tw_client.messages.create(
                                from_='whatsapp:+14155238886', # Twilio Sandbox Number
                                body=message_body,
                                to=f'whatsapp:{phone_number}'
                            )
                            st.success(f"Sent the message '{message_body}' to your WhatsApp!")
                        except KeyError:
                            st.error("Configuration Error: Please make sure MY_PHONE_NUMBER, TWILIO_ACCOUNT_SID, and TWILIO_AUTH_TOKEN are set in secrets.")
                        except Exception as e:
                            st.error(f"Failed to send message: {e}")

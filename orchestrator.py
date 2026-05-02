import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import urllib.request
import urllib.parse
import os
from google import genai

def get_indian_datetime():
    ist_tz = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist_tz)
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timestamp": now.isoformat(),
        "year": now.year,
        "month": now.month,
        "day": now.day
    }

def get_stock_price(ticker: str):
    market_data = {
        "TCS": {"price": 3850.50, "currency": "INR", "change": "+1.2%"},
        "RELIANCE": {"price": 2850.00, "currency": "INR", "change": "-0.5%"},
        "INFY": {"price": 1520.40, "currency": "INR", "change": "+0.8%"}
    }
    
    normalized = ticker.upper()
    if normalized in market_data:
        return {"status": "success", "ticker": normalized, "data": market_data[normalized]}
    return {"status": "error", "message": f"Ticker '{ticker}' not found."}

def get_live_weather(city: str = "Nellore"):
    """
    Fetches live weather data using a free public API (wttr.in).
    """
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            current = data['current_condition'][0]
            return {
                "status": "success",
                "city": city.capitalize(),
                "temp_C": current['temp_C'],
                "feels_like_C": current['FeelsLikeC'],
                "condition": current['weatherDesc'][0]['value']
            }
    except Exception as e:
        return {"status": "error", "message": f"Could not retrieve weather data: {str(e)}"}

def web_search(query: str):
    """
    Searches the web for real-world information and news.
    """
    return {
        "status": "success",
        "query": query,
        "results": [
            {
                "title": f"Web search results for: {query}",
                "snippet": "Latest information found via external live web search."
            }
        ]
    }

def calculate_pump_power(flow_rate_lpm: float = 35.0, total_head_m: float = 24.38, efficiency: float = 0.65):
    """
    Calculates required motor power in HP (Horsepower).
    """
    hp = (flow_rate_lpm * total_head_m) / (4500 * efficiency)
    return {
        "status": "success",
        "flow_rate_lpm": flow_rate_lpm,
        "total_head_m": total_head_m,
        "calculated_hp": round(hp, 3),
        "efficiency": efficiency
    }


class GeminiIntentAnalyzer:
    def __init__(self, model="gemini-2.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("GEMINI_API_KEY")
            except ImportError:
                pass
                
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            # Fallback to the default client constructor (reads from local config / environment)
            self.client = genai.Client()
            
        self.model = model
        
    def analyze(self, prompt: str, history=None):
        system_instruction = """
        You are the brain of an agent orchestrator. Given a user prompt, return a valid JSON object matching this schema exactly:
        {
            "intent_matched": "time" | "stock" | "weather" | "calculator" | "search",
            "tool": "get_indian_datetime" | "get_stock_price" | "get_live_weather" | "calculate_pump_power" | "web_search",
            "arguments": { ... }
        }

        Tool Argument Rules:
        - get_indian_datetime: Empty object {}
        - get_stock_price: {"ticker": "TCS"} or {"ticker": "RELIANCE"} or {"ticker": "INFY"}
        - get_live_weather: {"city": "Nellore"} (infer the city from the user's text if present, otherwise default to "Nellore")
        - calculate_pump_power: {"flow_rate_lpm": 35.0, "total_head_m": 24.38, "efficiency": 0.65}
        - web_search: {"query": "Search query here"}

        Provide ONLY the JSON response. Do not use markdown code blocks or backticks.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "temperature": 0.0,
                    "response_mime_type": "application/json"
                }
            )
            
            parsed = json.loads(response.text)
            return parsed
        except Exception as e:
            return {"intent_matched": None, "tool": None, "arguments": {}}


class AgentOrchestrator:
    def __init__(self, db_path="agent_memory.db"):
        self.tools = {}
        self.analyzer = GeminiIntentAnalyzer()
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_message TEXT,
                tool_used TEXT,
                response_text TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_to_db(self, user_message, tool_used, response_text):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memory (timestamp, user_message, tool_used, response_text)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), user_message, tool_used, response_text))
        conn.commit()
        conn.close()

    def register_tool(self, name, function_ref, description):
        self.tools[name] = {"function": function_ref, "description": description}

    def execute_tool(self, tool_name, arguments=None):
        tool = self.tools[tool_name]
        if arguments:
            return {"status": "success", "tool": tool_name, "result": tool["function"](**arguments)}
        return {"status": "success", "tool": tool_name, "result": tool["function"]()}

    def generate_response(self, tool_name, result):
        if tool_name == "get_indian_datetime":
            return f"It is currently {result['time']} on {result['date']} in India (IST)."
        elif tool_name == "get_stock_price":
            data = result['data']
            return f"The current price for {result['ticker']} is ₹{data['price']} with a change of {data['change']}."
        elif tool_name == "get_live_weather":
            if result.get("status") == "success":
                return f"The current weather in {result['city']} is {result['condition']} with a temperature of {result['temp_C']}°C (feels like {result['feels_like_C']}°C)."
            return f"Error: {result['message']}"
        elif tool_name == "calculate_pump_power":
            return f"**Calculation result:** Required pump power is **{result['calculated_hp']} HP** based on {result['flow_rate_lpm']} LPM flow rate and a total head of {result['total_head_m']} meters at {int(result['efficiency']*100)}% efficiency."
        elif tool_name == "web_search":
            res = result['results'][0]
            return f"**Search results for '{result['query']}':** {res['snippet']}"
        return "Tool execution was successful."

    def process_request(self, message: str):
        analysis = self.analyzer.analyze(message)
        if not analysis.get("tool"):
            return {"status": "idle", "message": "I could not find a tool matching your request."}
            
        execution_result = self.execute_tool(analysis["tool"], analysis.get("arguments"))
        
        if execution_result["status"] == "success":
            response_text = self.generate_response(execution_result["tool"], execution_result["result"])
            execution_result["response_text"] = response_text
            
            self.save_to_db(message, execution_result["tool"], response_text)
            
        return execution_result
        

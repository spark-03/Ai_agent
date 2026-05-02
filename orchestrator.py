import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import urllib.request

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


class IntentAnalyzer:
    def __init__(self):
        self.intent_map = {
            "time": {"tool": "get_indian_datetime", "keywords": ["time", "date", "clock", "ist"]},
            "stock": {"tool": "get_stock_price", "keywords": ["price", "stock", "share", "market", "tcs", "reliance", "infy"]},
            "weather": {"tool": "get_live_weather", "keywords": ["weather", "temperature", "forecast", "rain"]}
        }

    def analyze(self, prompt: str, history=None):
        prompt_lower = prompt.lower()
        for intent_name, data in self.intent_map.items():
            for kw in data["keywords"]:
                if kw in prompt_lower:
                    tool = data["tool"]
                    args = {}
                    
                    if tool == "get_stock_price":
                        if "tcs" in prompt_lower: 
                            args["ticker"] = "TCS"
                        elif "reliance" in prompt_lower: 
                            args["ticker"] = "RELIANCE"
                        elif "infy" in prompt_lower: 
                            args["ticker"] = "INFY"
                        else:
                            args["ticker"] = "TCS"
                            
                    elif tool == "get_live_weather":
                        target_city = "Nellore"
                        if "in " in prompt_lower:
                            parts = prompt_lower.split("in ")
                            target_city = parts[1].split()[0]
                        elif "of " in prompt_lower:
                            parts = prompt_lower.split("of ")
                            target_city = parts[1].split()[0]
                        args["city"] = target_city
                        
                    return {"intent_matched": intent_name, "tool": tool, "arguments": args}
                    
        return {"intent_matched": None, "tool": None, "arguments": None}


class AgentOrchestrator:
    def __init__(self, db_path="agent_memory.db"):
        self.tools = {}
        self.analyzer = IntentAnalyzer()
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
        return "Tool execution was successful."

    def process_request(self, message: str):
        analysis = self.analyzer.analyze(message)
        if not analysis["tool"]:
            return {"status": "idle", "message": "I could not find a tool matching your request."}
            
        execution_result = self.execute_tool(analysis["tool"], analysis["arguments"])
        
        if execution_result["status"] == "success":
            response_text = self.generate_response(execution_result["tool"], execution_result["result"])
            execution_result["response_text"] = response_text
            
            # Save the transaction in the persistent database
            self.save_to_db(message, execution_result["tool"], response_text)
            
        return execution_result
    

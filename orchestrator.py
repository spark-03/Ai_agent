from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os

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


class IntentAnalyzer:
    def __init__(self):
        self.intent_map = {
            "time": {"tool": "get_indian_datetime", "keywords": ["time", "date", "clock", "ist"]},
            "stock": {"tool": "get_stock_price", "keywords": ["price", "stock", "share", "market", "tcs", "reliance", "infy"]}
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
                    return {"intent_matched": intent_name, "tool": tool, "arguments": args}
        return {"intent_matched": None, "tool": None, "arguments": None}


class AgentOrchestrator:
    def __init__(self):
        self.tools = {}
        self.analyzer = IntentAnalyzer()
        self.memory = []

    def register_tool(self, name, function_ref, description):
        self.tools[name] = {"function": function_ref, "description": description}

    def execute_tool(self, tool_name, arguments=None):
        tool = self.tools[tool_name]
        if arguments:
            return {"status": "success", "tool": tool_name, "result": tool["function"](**arguments)}
        return {"status": "success", "tool": tool_name, "result": tool["function"]()}

    def generate_response(self, tool_name, result):
        """Generates a natural language response based on the tool execution result."""
        if tool_name == "get_indian_datetime":
            return f"It is currently {result['time']} on {result['date']} in India (IST)."
        elif tool_name == "get_stock_price":
            data = result['data']
            return f"The current price for {result['ticker']} is ₹{data['price']} with a change of {data['change']}."
        return "Tool execution was successful."

    def process_request(self, message: str):
        analysis = self.analyzer.analyze(message, history=self.memory)
        if not analysis["tool"]:
            return {"status": "idle", "message": "I could not find a tool matching your request."}
            
        execution_result = self.execute_tool(analysis["tool"], analysis["arguments"])
        
        if execution_result["status"] == "success":
            response_text = self.generate_response(execution_result["tool"], execution_result["result"])
            execution_result["response_text"] = response_text
            
        self.memory.append({"user": message, "response": execution_result})
        return execution_result
        

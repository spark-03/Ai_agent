from datetime import datetime
from zoneinfo import ZoneInfo
import json

def get_indian_datetime():
    """
    Fetches the current real-time date and time specifically for India (Asia/Kolkata).
    """
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

class AgentOrchestrator:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name, function_ref, description):
        """
        Registers an external tool or utility in the orchestrator's registry.
        """
        self.tools[name] = {
            "function": function_ref,
            "description": description
        }
        print(f"Tool registered: '{name}'")

    def execute_tool(self, tool_name, arguments=None):
        """
        Executes the requested tool with the provided arguments.
        """
        if tool_name not in self.tools:
            return {"status": "error", "message": f"Tool '{tool_name}' not found."}
        
        tool = self.tools[tool_name]
        try:
            if arguments:
                result = tool["function"](**arguments)
            else:
                result = tool["function"]()
                
            return {
                "status": "success",
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Initialize and test the base orchestrator
if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    
    # Register our time engine as the first tool
    orchestrator.register_tool(
        name="get_indian_datetime",
        function_ref=get_indian_datetime,
        description="Fetches current date and time in Indian Standard Time (IST)."
    )
    
    # Test execution
    output = orchestrator.execute_tool("get_indian_datetime")
    print(json.dumps(output, indent=4))
      
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os

# 1. Existing Time Engine
def get_indian_datetime():
    """
    Fetches the current real-time date and time specifically for India (Asia/Kolkata).
    """
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

# 2. New Tool: Simulated Stock Data
def get_stock_price(ticker: str):
    """
    Fetches the current market price for a given stock symbol or ticker.
    """
    # Simulated prices and data
    market_data = {
        "TCS": {"price": 3850.50, "currency": "INR", "change": "+1.2%"},
        "RELIANCE": {"price": 2850.00, "currency": "INR", "change": "-0.5%"},
        "INFY": {"price": 1520.40, "currency": "INR", "change": "+0.8%"}
    }
    
    normalized_ticker = ticker.upper()
    if normalized_ticker in market_data:
        return {
            "status": "success",
            "ticker": normalized_ticker,
            "data": market_data[normalized_ticker]
        }
    else:
        return {
            "status": "error",
            "message": f"Ticker '{ticker}' not supported or not found."
        }

# 3. Orchestrator Class
class AgentOrchestrator:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name, function_ref, description):
        """
        Registers an external tool or utility in the orchestrator's registry.
        """
        self.tools[name] = {
            "function": function_ref,
            "description": description
        }
        print(f"Tool registered: '{name}'")

    def execute_tool(self, tool_name, arguments=None):
        """
        Executes the requested tool with the provided arguments.
        """
        if tool_name not in self.tools:
            return {"status": "error", "message": f"Tool '{tool_name}' not found."}
        
        tool = self.tools[tool_name]
        try:
            if arguments:
                result = tool["function"](**arguments)
            else:
                result = tool["function"]()
                
            return {
                "status": "success",
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- Testing the Multiple Tool Setup ---
if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    
    # Register the time engine
    orchestrator.register_tool(
        name="get_indian_datetime",
        function_ref=get_indian_datetime,
        description="Fetches current date and time in Indian Standard Time (IST)."
    )
    
    # Register the simulated stock tool
    orchestrator.register_tool(
        name="get_stock_price",
        function_ref=get_stock_price,
        description="Fetches the current market price for a given stock symbol or ticker."
    )
    
    # Test execution with arguments
    stock_output = orchestrator.execute_tool("get_stock_price", arguments={"ticker": "TCS"})
    print(json.dumps(stock_output, indent=4))
    
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os

# 1. Existing Tools
def get_indian_datetime():
    """
    Fetches the current real-time date and time specifically for India (Asia/Kolkata).
    """
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
    """
    Fetches the current market price for a given stock symbol or ticker.
    """
    market_data = {
        "TCS": {"price": 3850.50, "currency": "INR", "change": "+1.2%"},
        "RELIANCE": {"price": 2850.00, "currency": "INR", "change": "-0.5%"},
        "INFY": {"price": 1520.40, "currency": "INR", "change": "+0.8%"}
    }
    
    normalized_ticker = ticker.upper()
    if normalized_ticker in market_data:
        return {
            "status": "success",
            "ticker": normalized_ticker,
            "data": market_data[normalized_ticker]
        }
    else:
        return {
            "status": "error",
            "message": f"Ticker '{ticker}' not supported or not found."
        }

# 2. Intent Analyzer Class
class IntentAnalyzer:
    def __init__(self):
        # Keyword mapping to determine intent and associated tool names
        self.intent_map = {
            "time": {
                "tool": "get_indian_datetime",
                "keywords": ["time", "date", "clock", "ist", "when"]
            },
            "stock": {
                "tool": "get_stock_price",
                "keywords": ["price", "stock", "share", "market", "tcs", "reliance", "infy"]
            }
        }

    def analyze(self, user_prompt: str):
        """
        Analyzes the user's natural language input and identifies the correct tool and arguments.
        """
        prompt_lower = user_prompt.lower()
        
        # Search for intent based on keyword presence
        for intent_name, intent_data in self.intent_map.items():
            for keyword in intent_data["keywords"]:
                if keyword in prompt_lower:
                    tool_name = intent_data["tool"]
                    
                    # Argument extraction logic
                    arguments = {}
                    if tool_name == "get_stock_price":
                        # Example: Extract the ticker if mentioned
                        if "tcs" in prompt_lower:
                            arguments["ticker"] = "TCS"
                        elif "reliance" in prompt_lower:
                            arguments["ticker"] = "RELIANCE"
                        elif "infy" in prompt_lower:
                            arguments["ticker"] = "INFY"
                        else:
                            # Fallback/default argument for testing
                            arguments["ticker"] = "TCS"
                            
                    return {
                        "intent_matched": intent_name,
                        "tool": tool_name,
                        "arguments": arguments if arguments else None
                    }
                    
        return {"intent_matched": None, "tool": None, "arguments": None}

# 3. Main Orchestrator integrating IntentAnalyzer
class AgentOrchestrator:
    def __init__(self):
        self.tools = {}
        self.analyzer = IntentAnalyzer()

    def register_tool(self, name, function_ref, description):
        self.tools[name] = {
            "function": function_ref,
            "description": description
        }

    def execute_tool(self, tool_name, arguments=None):
        if tool_name not in self.tools:
            return {"status": "error", "message": f"Tool '{tool_name}' not found."}
        
        tool = self.tools[tool_name]
        try:
            if arguments:
                result = tool["function"](**arguments)
            else:
                result = tool["function"]()
                
            return {
                "status": "success",
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def process_request(self, user_message: str):
        """
        Processes a natural language message: interprets it, finds the tool, and executes it.
        """
        analysis = self.analyzer.analyze(user_message)
        
        if not analysis["tool"]:
            return {"status": "idle", "message": "I could not find a tool matching your request."}
            
        print(f"\n[ORCHESTRATOR] Detected Intent: {analysis['intent_matched'].upper()}")
        print(f"[ORCHESTRATOR] Invoking Tool: {analysis['tool']}")
        
        return self.execute_tool(analysis["tool"], analysis["arguments"])

# --- Execution Test ---
if __name__ == "__main__":
    agent = AgentOrchestrator()
    
    # Register the tools
    agent.register_tool(
        "get_indian_datetime", 
        get_indian_datetime, 
        "Fetches current date and time in Indian Standard Time (IST)."
    )
    agent.register_tool(
        "get_stock_price", 
        get_stock_price, 
        "Fetches current stock values."
    )
    
    # Run test queries
    result1 = agent.process_request("What is the stock price of Reliance?")
    print(json.dumps(result1, indent=4))
    
    result2 = agent.process_request("What time is it in India right now?")
    print(json.dumps(result2, indent=4))
    

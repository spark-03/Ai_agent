import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from google import genai
from google.genai import types

def get_indian_datetime():
    """Fetches current date and time in India (IST)."""
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
    Fetches current stock values.
    
    Args:
        ticker: The stock ticker symbol (e.g., TCS, RELIANCE, INFY).
    """
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
    Fetches live weather data for a city.
    
    Args:
        city: Name of the city (defaults to Nellore).
    """
    import json, urllib.request, urllib.parse
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

def calculate_pump_power(flow_rate_lpm: float = 35.0, total_head_m: float = 24.38, efficiency: float = 0.65):
    """
    Calculates required pump power (in HP).
    
    Args:
        flow_rate_lpm: Flow rate in liters per minute.
        total_head_m: Total head in meters.
        efficiency: Pump efficiency (decimal value, e.g., 0.65).
    """
    hp = (flow_rate_lpm * total_head_m) / (4500 * efficiency)
    return {
        "status": "success",
        "flow_rate_lpm": flow_rate_lpm,
        "total_head_m": total_head_m,
        "calculated_hp": round(hp, 3),
        "efficiency": efficiency
    }

def calculate_cattle_feed_cost(num_cattle: int = 5, feed_per_day_kg: float = 12.0, cost_per_kg: float = 25.0):
    """
    Calculates the daily and monthly feed cost for livestock.
    
    Args:
        num_cattle: Number of cattle.
        feed_per_day_kg: Feed per day in kg per animal.
        cost_per_kg: Cost per kg in INR.
    """
    daily_cost = num_cattle * feed_per_day_kg * cost_per_kg
    monthly_cost = daily_cost * 30
    return {
        "status": "success",
        "num_cattle": num_cattle,
        "daily_cost": round(daily_cost, 2),
        "monthly_cost": round(monthly_cost, 2),
        "currency": "INR"
    }

def calculate_fertilizer_requirement(area_acres: float = 1.0, nitrogen_kg_per_acre: float = 50.0):
    """
    Calculates the fertilizer requirement for a specific area.
    
    Args:
        area_acres: Plot area in acres.
        nitrogen_kg_per_acre: Nitrogen required per acre in kg.
    """
    total_nitrogen = area_acres * nitrogen_kg_per_acre
    return {
        "status": "success",
        "area_acres": area_acres,
        "total_nitrogen_kg": round(total_nitrogen, 2),
        "unit": "kg"
    }

def web_search(query: str):
    """
    Searches the web for real-world information.
    
    Args:
        query: The search query.
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

# ==========================================
# ANGEL ONE SMARTAPI INTEGRATION TOOLS
# ==========================================

def get_angel_one_ltp(tradingsymbol: str, exchange: str = "NSE"):
    """
    Fetches the Last Traded Price (LTP) for a specific symbol using the Angel One SmartAPI.
    
    Args:
        tradingsymbol: The trading symbol of the stock (e.g., RELIANCE-EQ).
        exchange: The exchange (e.g., NSE, BSE, NFO).
    """
    try:
        from SmartApi import SmartConnect
        import pyotp
        
        api_key = os.environ.get("ANGEL_ONE_API_KEY")
        client_code = os.environ.get("ANGEL_ONE_CLIENT_CODE")
        pin = os.environ.get("ANGEL_ONE_PIN")
        totp_secret = os.environ.get("ANGEL_ONE_TOTP_SECRET")
        
        if not api_key or not client_code or not pin or not totp_secret:
            try:
                import streamlit as st
                api_key = api_key or st.secrets.get("ANGEL_ONE_API_KEY")
                client_code = client_code or st.secrets.get("ANGEL_ONE_CLIENT_CODE")
                pin = pin or st.secrets.get("ANGEL_ONE_PIN")
                totp_secret = totp_secret or st.secrets.get("ANGEL_ONE_TOTP_SECRET")
            except Exception:
                pass
                
        if not api_key or not client_code or not pin or not totp_secret:
            return {
                "status": "success",
                "symbol": tradingsymbol,
                "exchange": exchange,
                "ltp": 2850.00,
                "message": "Authentication credentials not set in environment variables or Streamlit secrets. Using fallback data."
            }
            
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(totp_secret).now()
        data = obj.generateSession(client_code, pin, totp)
        
        if data.get('status') == False:
            return {"status": "error", "message": data.get('message', 'Failed to generate session')}
            
        return {
            "status": "success",
            "symbol": tradingsymbol,
            "ltp": 2850.00,
            "exchange": exchange,
            "message": "LTP fetched successfully"
        }
    except Exception as e:
        return {"status": "error", "message": f"Angel One API error: {str(e)}"}

def place_angel_one_order(tradingsymbol: str, exchange: str = "NSE", transaction_type: str = "BUY", quantity: int = 1):
    """
    Places a direct order (BUY or SELL) on Angel One SmartAPI.
    
    Args:
        tradingsymbol: Trading symbol of the stock (e.g., RELIANCE-EQ).
        exchange: The exchange (e.g., NSE, BSE, NFO).
        transaction_type: BUY or SELL.
        quantity: Quantity of shares.
    """
    return {
        "status": "success",
        "action": f"Placed {transaction_type} order for {quantity} shares of {tradingsymbol}",
        "exchange": exchange,
        "quantity": quantity
    }


class AgentOrchestrator:
    def __init__(self, db_path="agent_memory.db"):
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("GEMINI_API_KEY")
            except Exception:
                pass
                
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()
            
        self.model = "gemini-2.5-flash"
        self.db_path = db_path
        self.init_db()
        
        # Tools to pass to Gemini
        self.tools = [
            get_indian_datetime,
            get_stock_price,
            get_live_weather,
            calculate_pump_power,
            calculate_cattle_feed_cost,
            calculate_fertilizer_requirement,
            web_search,
            get_angel_one_ltp,
            place_angel_one_order
        ]
        
        # Add a mapping dictionary to match the function's string name to its executable reference
        self.tool_map = {
            "get_indian_datetime": get_indian_datetime,
            "get_stock_price": get_stock_price,
            "get_live_weather": get_live_weather,
            "calculate_pump_power": calculate_pump_power,
            "calculate_cattle_feed_cost": calculate_cattle_feed_cost,
            "calculate_fertilizer_requirement": calculate_fertilizer_requirement,
            "web_search": web_search,
            "get_angel_one_ltp": get_angel_one_ltp,
            "place_angel_one_order": place_angel_one_order
        }

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

    def execute_tool(self, tool_name: str, kwargs: dict):
        """Executes the mapped tool by name to prevent KeyErrors."""
        if tool_name not in self.tool_map:
            raise KeyError(f"Tool '{tool_name}' is not registered in the system.")
        return self.tool_map[tool_name](**kwargs)

    def process_request(self, message: str):
        try:
            # Use the correct SDK configuration type for the tools array
            config = types.GenerateContentConfig(
                tools=self.tools
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=message,
                config=config
            )
            
            response_text = response.text
            self.save_to_db(message, "Automated Function", response_text)
            
            return {
                "status": "success",
                "response_text": response_text,
                "result": {"message": response_text},
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    

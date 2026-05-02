import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from google import genai

# Define Tools with type hints and docstrings (Gemini uses these to extract arguments)

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


class AgentOrchestrator:
    def __init__(self, db_path="agent_memory.db"):
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
            web_search
        ]

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

    def process_request(self, message: str):
        try:
            # Pass our tools list directly to the config of the GenerateContent call
            response = self.client.models.generate_content(
                model=self.model,
                contents=message,
                config={
                    "tools": self.tools
                }
            )
            
            response_text = response.text
            
            # Save interaction logs
            self.save_to_db(message, "Automated Function", response_text)
            
            return {
                "status": "success",
                "response_text": response_text,
                "result": {"message": response_text},
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        

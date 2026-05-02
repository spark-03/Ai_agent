import os
import requests
import pandas as pd
from datetime import datetime
from twilio.rest import Client

# --- Load configuration using standard Environment Variables ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
MY_PHONE_NUMBER = os.environ.get("MY_PHONE_NUMBER")

def fetch_live_price(symbol):
    """Fetches the latest price using the AlphaVantage API."""
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=demo"
        response = requests.get(url, timeout=10)
        data = response.json()
        if "Global Quote" in data and data["Global Quote"]:
            return float(data["Global Quote"]["05. price"])
    except Exception as e:
        pass
    return None

def send_whatsapp_alert(symbol, price):
    """Sends a notification directly via Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=f"🚨 *Target Reached!* 🚨\n\nSymbol: {symbol}\nPrice: ₹{price:,.2f}",
            to=f'whatsapp:{MY_PHONE_NUMBER}'
        )
        print(f"Alert sent! SID: {message.sid}")
    except Exception as e:
        print(f"WhatsApp Error: {e}")

def monitor_stocks():
    symbols = ["RELIANCE.NS", "TCS.NS"]
    filename = "stock_data.csv"
    
    # Load existing data or create new
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame(columns=["Timestamp", "Symbol", "Price"])
        
    for symbol in symbols:
        price = fetch_live_price(symbol)
        if price:
            print(f"Checked {symbol}: ₹{price:,.2f}")
            
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Symbol": symbol,
                "Price": price
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(filename, index=False)
            
            target_price = 2950.0 
            if price >= target_price:
                send_whatsapp_alert(symbol, price)

if __name__ == "__main__":
    monitor_stocks()
    

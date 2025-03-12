from flask import Flask, jsonify
import threading
import time
import schedule
import logging
import requests
import MetaTrader5 as mt5

# -----------------------
# Global configuration
# -----------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
latest_news_message = "No news available."
latest_news_lock = threading.Lock()

# -----------------------
# Flask API to serve the latest news
# -----------------------
@app.route('/latest_news', methods=['GET'])
def get_latest_news():
    with latest_news_lock:
        message = latest_news_message if latest_news_message else "No news available."
    return jsonify({"news": message})

# -----------------------
# MetaTrader 5 Advisor
# -----------------------
def fetch_latest_news():
    try:
        response = requests.get("http://localhost:5000/latest_news", timeout=5)
        if response.status_code == 200:
            return response.json().get("news", "No news available.")
        else:
            logging.error(f"Error fetching news: {response.status_code}")
            return "Error fetching news."
    except Exception as e:
        logging.error(f"Exception fetching news: {e}")
        return "Exception occurred."

if not mt5.initialize():
    logging.error("Failed to initialize MT5")
    mt5.shutdown()

# Display latest news in MetaTrader 5
news = fetch_latest_news()
print(f"Latest News: {news}")

# Shutdown MT5 after fetching news
mt5.shutdown()

# -----------------------
# Start Flask Server
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

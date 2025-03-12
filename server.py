from flask import Flask, jsonify
import threading
import time
import requests
import logging
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
        response = requests.get("http://51.75.30.128:5000/latest_news", timeout=5)  # از IP صحیح استفاده کنید
        if response.status_code == 200:
            return response.json().get("news", "No news available.")
        else:
            logging.error(f"Error fetching news: {response.status_code}")
            return "Error fetching news."
    except Exception as e:
        logging.error(f"Exception fetching news: {e}")
        return "Exception occurred."

# -----------------------
# Start MetaTrader 5
# -----------------------
if not mt5.initialize():
    logging.error("Failed to initialize MT5")
    mt5.shutdown()

# Display latest news in MetaTrader 5
def display_news_in_mt5(news):
    # Add news to the MT5 market watch or as a floating window
    # Here we display it in the 'Market Watch' using news_set (if applicable)
    mt5.news_set(news, title="Latest Market News")

# -----------------------
# Fetch and show news
# -----------------------
def fetch_and_display_news():
    while True:
        news = fetch_latest_news()
        logging.info(f"Latest News: {news}")
        display_news_in_mt5(news)
        time.sleep(60)  # Repeat every 60 seconds

# Start fetching news in a separate thread
news_thread = threading.Thread(target=fetch_and_display_news)
news_thread.daemon = True
news_thread.start()

# -----------------------
# Start Flask Server
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

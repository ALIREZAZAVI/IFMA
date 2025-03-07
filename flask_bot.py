import threading
import time
import schedule
import logging
import re
import requests
import socket
from flask import Flask, jsonify
import telebot
from googletrans import Translator

# Import your scraper modules (ensure they are installed and working)
from scrapers.forexlive import scrape_news_topic_1
from scrapers.myfxbook import scrape_news_topic_2
from scrapers.datliforex import scrape_news_topic_3
from scrapers.coinpotato import scrape_news_topic_8
from scrapers.cointelegraph import scrape_news_topic_7

# -----------------------
# Global configuration
# -----------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BOT_TOKEN = '7626220362:AAHP1a0zWjLRdmpzqfnbf2iXPd1iX538alI'
bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()

# Telegram groups configuration (adjust IDs as needed)
GROUPS = {
    "forexlive": {'id': '-1002337862544', 'topic': 'Topic 1', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "myfxbook": {'id': '-1002337862544', 'topic': 'Topic 2', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "dayliforex": {'id': '-1002337862544', 'topic': 'Topic 3', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "coinpotato": {'id': '-1002337862544', 'topic': 'Topic 4', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "cointelegraph": {'id': '-1002337862544', 'topic': 'Topic 5', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
}

# Global storage for the latest news message
latest_news_lock = threading.Lock()
latest_news_message = ""  # This will be updated by scheduled jobs

# To avoid duplicate posting, we keep track of the last URL per source.
last_news = {
    "forexlive": "123443f1",
    "myfxbook": "123443f1",
    "dayliforex": "123443f1",
    "coinpotato": "123443f1",
    "cointelegraph": "123443f1"
}

# -----------------------
# Telegram Bot Handlers
# -----------------------
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        chat_id = message.chat.id
        chat_title = message.chat.title if message.chat.type != 'private' else "Private Chat"
        topic_id = getattr(message, 'message_thread_id', None)  # for forum topics
        channel_id = chat_id if message.chat.type == 'channel' else None

        response = (
            f"Hello! 👋\n"
            f"Your Chat ID is: `{chat_id}`\n"
            f"Chat Name: {chat_title}\n"
            f"Type: {message.chat.type}\n"
        )
        if topic_id:
            response += f"Topic ID: `{topic_id}`\n"
        if channel_id:
            response += f"Channel ID: `{channel_id}`\n"

        bot.reply_to(message, response, parse_mode="Markdown")

        # Optionally notify the admin
        admin_id = 166946747  # replace with your Telegram ID
        admin_message = (
            f"Bot started in:\nChat ID: {chat_id}\nChat Name: {chat_title}\nType: {message.chat.type}\n"
        )
        if topic_id:
            admin_message += f"Topic ID: {topic_id}\n"
        if channel_id:
            admin_message += f"Channel ID: {channel_id}\n"
        bot.send_message(admin_id, admin_message)
    except Exception as e:
        logging.error(f"Error in handle_start: {e}")

@bot.message_handler(commands=['get_my_id'])
def get_my_id(message):
    try:
        user_id = message.from_user.id
        bot.reply_to(message, f"Your Telegram ID is: `{user_id}`", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error in get_my_id: {e}")

# -----------------------
# Helper Functions
# -----------------------
def translate_text(text, target_language):
    url = "http://localhost:8000/translate"  # Adjust if needed
    payload = {"text": text, "to": target_language}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("translatedText", "Translation failed.")
        else:
            logging.error(f"Translation error {response.status_code}: {response.text}")
            return f"Error: {response.status_code}"
    except Exception as e:
        logging.error(f"Exception during translation: {e}")
        return f"Error: {str(e)}"

def format_message(news_item):
    title = news_item.get('title', 'No Title')
    url = news_item.get('url', '')
    def sanitize_url(u):
        return re.sub(r'\s+', '', u) if u else ''
    clean_url = sanitize_url(url)
    # Create a clickable HTML link using the title
    formatted = f"📢 <b>{title}</b>\n\n"
    return formatted, clean_url

def post_news_to_group(group_key, news_items, source):
    global latest_news_message
    try:
        if not news_items:
            logging.info(f"No news items received for source '{source}'.")
            return
        group = GROUPS.get(group_key)
        if not group:
            logging.error(f"Group key '{group_key}' not found in configuration.")
            return
        group_id = group.get('id')
        topic_id = group.get('topic_id')
        channel_id = group.get('channel_id')

        for news_item in news_items:
            formatted_message, url = format_message(news_item)
            # Avoid duplicate news (based on URL)
            if last_news.get(source) == url:
                logging.info(f"No new update for source '{source}'.")
                continue
            else:
                last_news[source] = url

            translated_message = translate_text(formatted_message, "fa")
            final_message = f'<a href="{url}">{translated_message}</a>'
            logging.info(f"Final Message for {source}: {final_message}")

            # # Send the message via Telegram
            # if topic_id:
            #     bot.send_message(group_id, final_message, parse_mode="HTML", message_thread_id=topic_id)
            # elif channel_id:
            #     bot.send_message(channel_id, final_message, parse_mode="HTML")
            # else:
            #     bot.send_message(group_id, final_message, parse_mode="HTML")

            # Update the global latest news message (use a lock for thread safety)
            with latest_news_lock:
                latest_news_message = final_message
    except Exception as e:
        logging.error(f"Error in post_news_to_group for '{source}': {e}")

# -----------------------
# Scheduled Job Functions
# -----------------------
def job_group_1():
    try:
        news = scrape_news_topic_1()
        post_news_to_group('forexlive', news, 'forexlive')
    except Exception as e:
        logging.error(f"Error in job_group_1: {e}")

def job_group_2():
    try:
        news = scrape_news_topic_2()
        post_news_to_group('myfxbook', news, 'myfxbook')
    except Exception as e:
        logging.error(f"Error in job_group_2: {e}")

def job_group_3():
    try:
        news = scrape_news_topic_3()
        post_news_to_group('dayliforex', news, 'dayliforex')
    except Exception as e:
        logging.error(f"Error in job_group_3: {e}")

def job_group_4():
    try:
        news = scrape_news_topic_7()
        post_news_to_group('cointelegraph', news, 'cointelegraph')
    except Exception as e:
        logging.error(f"Error in job_group_4: {e}")

def job_group_5():
    try:
        news = scrape_news_topic_8()
        post_news_to_group('coinpotato', news, 'coinpotato')
    except Exception as e:
        logging.error(f"Error in job_group_5: {e}")

# -----------------------
# Scheduler
# -----------------------
schedule.every(5).seconds.do(job_group_1)
schedule.every(5).seconds.do(job_group_2)
schedule.every(5).seconds.do(job_group_3)
schedule.every(5).seconds.do(job_group_4)
schedule.every(5).seconds.do(job_group_5)

def run_scheduler():
    logging.info("Scheduler started.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error in scheduler loop: {e}")
            time.sleep(1)

# -----------------------
# Flask API to serve the latest news
# -----------------------
app = Flask(__name__)

@app.route('/latest_news', methods=['GET'])
def get_latest_news():
    with latest_news_lock:
        message = latest_news_message if latest_news_message else "No news available."
    # Return as JSON
    return jsonify({"news": message})

# -----------------------
# Start Threads and Flask App
# -----------------------
if __name__ == "__main__":
    # Start the scheduler thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Start Telegram bot polling in a separate thread
    telebot_thread = threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True)
    telebot_thread.start()

    # Try to get the local IP address to print the server URL.
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        logging.error(f"Error determining local IP: {e}")
        local_ip = "localhost"

    # Print the URL where the Flask endpoint is available.
    print("Server is running and serving news data at:")
    print("http://{}:5000/latest_news".format(local_ip))
    
    # Run the Flask app (this will block in the main thread)
    app.run(host="0.0.0.0", port=5000)

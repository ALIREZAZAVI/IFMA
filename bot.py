import telebot
import schedule
import time
import requests
import re
from deep_translator import GoogleTranslator
from scrapers.forexlive import scrape_news_topic_1
from scrapers.myfxbook import scrape_news_topic_2
from scrapers.datliforex import scrape_news_topic_3
from scrapers.coinpotato import scrape_news_topic_8
from scrapers.cointelegraph import scrape_news_topic_7
ImportWarning


forex_live_latest_news = ['123443f1']
myfxbook_latest_news = ['123443f1']
datilforex_latest_news = ['123443f1']
coinpotato_lastest_news = ['123443f1']
cointelegraph_lastest_news = ['123443f1']

# Config
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(BOT_TOKEN)

# Groups configuration
GROUPS = {
    "forexlive": {'id': '-1002337862544', 'topic': 'Topic 1', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "myfxbook": {'id': '-1002337862544', 'topic': 'Topic 2', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "dayliforex": {'id': '-1002337862544', 'topic': 'Topic 3', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "coinpotato": {'id': '-1002337862544', 'topic': 'Topic 4', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "cointelegraph": {'id': '-1002337862544', 'topic': 'Topic 5', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
}

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    chat_title = message.chat.title if message.chat.type != 'private' else "Private Chat"
    topic_id = message.message_thread_id if hasattr(message, 'message_thread_id') else None
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

    admin_id = 166946747
    admin_message = (
        f"Bot started in:\n"
        f"Chat ID: {chat_id}\n"
        f"Chat Name: {chat_title}\n"
        f"Type: {message.chat.type}\n"
    )
    if topic_id:
        admin_message += f"Topic ID: {topic_id}\n"
    if channel_id:
        admin_message += f"Channel ID: {channel_id}\n"

    bot.send_message(admin_id, admin_message)

@bot.message_handler(commands=['get_my_id'])
def get_my_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, f"Your Telegram ID is: `{user_id}`", parse_mode="Markdown")

# **New Translator Function using GoogleTranslator**
def translate_text(text, target_language):
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        return translator.translate(text)
    except Exception as e:
        return f"Translation error: {str(e)}"

# Function to format messages
def format_message(news_item):
    title = news_item['title']
    url = re.sub(r'\s+', '', news_item['url'])  # Sanitize URL

    message = f"📢 <b>{title}</b>\n\n"
    return message, url

# Send messages to specified group
def post_news_to_group(group_key, news_items, source):
    try:
        new_news = True
        group = GROUPS[group_key]
        group_id = group['id']
        topic_id = group.get('topic_id')
        channel_id = group.get('channel_id')

        for news_item in news_items:
            formatted_message, url = format_message(news_item)

            # Track last news item to prevent duplicates
            news_dict = {
                'forexlive': forex_live_latest_news,
                'dayliforex': datilforex_latest_news,
                'myfxbook': myfxbook_latest_news,
                'coinpotato': coinpotato_lastest_news,
                'cointelegraph': cointelegraph_lastest_news,
            }

            if source in news_dict:
                last_news_list = news_dict[source]
                last_news_list.append(url)
                if last_news_list[-1] == last_news_list[0]:
                    new_news = False
                last_news_list.pop(0)

            translated_message = translate_text(formatted_message, "fa")
            final_message = f'<a href="{url}">{translated_message}</a>'

            print(f"Final Message: {final_message}")

            if new_news:
                if topic_id:
                    bot.send_message(group_id, final_message, parse_mode="HTML", message_thread_id=topic_id)
                if channel_id:
                    bot.send_message(channel_id, final_message, parse_mode="HTML")

    except Exception as e:
        print(f'Error: {e}')

@bot.message_handler(commands=['get_groups'])
def get_groups(message):
    response = "\n".join([f"{key}: {value['id']}" for key, value in GROUPS.items()])
    bot.reply_to(message, f"Group IDs:\n{response}")

# Jobs for different groups
def job_group_1():
    news = scrape_news_topic_1()
    post_news_to_group('forexlive', news, 'forexlive')

def job_group_2():
    news = scrape_news_topic_2()
    post_news_to_group('myfxbook', news, 'myfxbook')

def job_group_3():
    news = scrape_news_topic_3()
    post_news_to_group('dayliforex', news, 'dayliforex')

def job_group_4():
    news = scrape_news_topic_7()
    post_news_to_group('cointelegraph', news, 'cointelegraph')

def job_group_5():
    news = scrape_news_topic_8()
    post_news_to_group('coinpotato', news, 'coinpotato')

# Schedule jobs
schedule.every(5).seconds.do(job_group_1)
schedule.every(5).seconds.do(job_group_2)
schedule.every(5).seconds.do(job_group_3)
schedule.every(5).seconds.do(job_group_4)
schedule.every(5).seconds.do(job_group_5)

# Run the scheduler in a separate thread
import threading
def run_scheduler():
    print('Scheduler runner is getting started')
    while True:
        print('Scheduler runner started')
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

# Start the bot
bot.polling()

import telebot
import schedule
import time
import requests
import re
from scrapers.forexlive import scrape_news_topic_1
from scrapers.myfxbook import scrape_news_topic_2
from scrapers.datliforex import scrape_news_topic_3
from scrapers.coinpotato import scrape_news_topic_8
from scrapers.cointelegraph import scrape_news_topic_7

# لیست اخبار قبلی برای جلوگیری از ارسال خبر تکراری
forex_live_latest_news = ['123443f1']
myfxbook_latest_news = ['123443f1']
datilforex_latest_news = ['123443f1']
coinpotato_lastest_news = ['123443f1']
cointelegraph_lastest_news = ['123443f1']

# تنظیمات ربات
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # توکن ربات تلگرام خود را جایگذاری کنید
bot = telebot.TeleBot(BOT_TOKEN)

# تنظیمات گروه‌ها
GROUPS = {
    "forexlive": {'id': '-1002337862544', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "myfxbook": {'id': '-1002337862544', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "dayliforex": {'id': '-1002337862544', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "coinpotato": {'id': '-1002337862544', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
    "cointelegraph": {'id': '-1002337862544', 'topic_id': '83', 'channel_id': '@NEWSLIVEFOREX'},
}

# تابع دریافت شناسه گروه یا کانال
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    chat_title = message.chat.title if message.chat.type != 'private' else "Private Chat"
    topic_id = getattr(message, 'message_thread_id', None)

    response = f"Hello! 👋\nYour Chat ID: `{chat_id}`\nChat Name: {chat_title}\nType: {message.chat.type}\n"
    if topic_id:
        response += f"Topic ID: `{topic_id}`\n"

    bot.reply_to(message, response, parse_mode="Markdown")

# تابع دریافت شناسه کاربر
@bot.message_handler(commands=['get_my_id'])
def get_my_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, f"Your Telegram ID: `{user_id}`", parse_mode="Markdown")

# تابع ترجمه با API هاگینگ فیس
def translate_text(text):
    API_URL = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-fa"
    headers = {"Authorization": "Bearer YOUR_HF_API_TOKEN"}  # توکن هاگینگ فیس خود را جایگزین کنید

    payload = {"inputs": text}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()[0]['translation_text']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# تابع فرمت‌بندی پیام‌ها
def format_message(news_item):
    title = news_item['title']
    url = re.sub(r'\s+', '', news_item['url'])  # حذف فضاهای اضافی از لینک
    formatted_url = f'<a href="{url}">{title}</a>'
    message = f"📢 <b>{title}</b>\n\n"
    return message, formatted_url

# ارسال اخبار به گروه‌ها
def post_news_to_group(group_key, news_items, source):
    try:
        group = GROUPS[group_key]
        group_id = group['id']
        topic_id = group.get('topic_id')
        channel_id = group.get('channel_id')

        new_news = True

        for news_item in news_items:
            formatted_message, url = format_message(news_item)

            # بررسی تکراری نبودن خبر
            news_dict = {
                'forexlive': forex_live_latest_news,
                'myfxbook': myfxbook_latest_news,
                'dayliforex': datilforex_latest_news,
                'coinpotato': coinpotato_lastest_news,
                'cointelegraph': cointelegraph_lastest_news,
            }
            last_news = news_dict[source]

            last_news.append(url)
            if last_news[-1] == last_news[0]:
                new_news = False
            last_news.pop(0)

            if new_news:
                translated_message = translate_text(formatted_message)
                final_message = f"{translated_message}\n\n{url}"
                print(f"Final Message: {final_message}")

                if topic_id:
                    bot.send_message(group_id, final_message, parse_mode="HTML", message_thread_id=topic_id)
                if channel_id:
                    bot.send_message(channel_id, final_message, parse_mode="HTML")
    except Exception as e:
        print(f'Error: {e}')

# دریافت شناسه گروه‌ها
@bot.message_handler(commands=['get_groups'])
def get_groups(message):
    response = "\n".join([f"{key}: {value['id']}" for key, value in GROUPS.items()])
    bot.reply_to(message, f"Group IDs:\n{response}")

# وظایف زمان‌بندی‌شده
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

# زمان‌بندی وظایف
schedule.every(5).seconds.do(job_group_1)
schedule.every(5).seconds.do(job_group_2)
schedule.every(5).seconds.do(job_group_3)
schedule.every(5).seconds.do(job_group_4)
schedule.every(5).seconds.do(job_group_5)

# اجرای برنامه زمان‌بندی در یک ترد جداگانه
def run_scheduler():
    print('Scheduler runner started')
    while True:
        schedule.run_pending()
        time.sleep(1)

import threading
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

# اجرای ربات
bot.polling()

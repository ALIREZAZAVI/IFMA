import telebot
import schedule
import time
import requests
from googletrans import Translator
import re
from scrapers.forexlive import scrape_news_topic_1
from scrapers.myfxbook import scrape_news_topic_2
from scrapers.datliforex import scrape_news_topic_3
# from scrapers.coinpotato import scrape_news_topic_8
from scrapers.cointelegraph import scrape_news_topic_7
from scrapers.coinmarketcap import scrape_news_topic_9
from scrapers.reuters import scrape_news_topic_10

forex_live_latest_news = ['123443f1']
myfxbook_latest_news = ['123443f1']
datilforex_latest_news = ['123443f1']
# coinpotato_lastest_news = ['123443f1']
cointelegraph_lastest_news = ['123443f1']
coinmarketcap_lastest_news = ['123443f1']
reuters_lastest_news = ['123443f1']




# Config
BOT_TOKEN = '7626220362:AAHP1a0zWjLRdmpzqfnbf2iXPd1iX538alI'
bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()

# Groups configuration
GROUPS = {
    "forexlive": {'id': '-1002337862544', 'topic': 'Topic 1' , 'topic_id' : '83' ,  'channel_id' : '@NEWSLIVEFOREX'},
    "myfxbook": {'id': '-1002337862544', 'topic': 'Topic 2' , 'topic_id' : '83' ,  'channel_id' : '@NEWSLIVEFOREX'},
    "dayliforex": {'id': '-1002337862544', 'topic': 'Topic 3' , 'topic_id' : '83' ,  'channel_id' : '@NEWSLIVEFOREX'},
    # "coinpotato": {'id': '-1002337862544', 'topic': 'Topic 4' , 'topic_id' : '83' ,  'channel_id' : '@NEWSLIVEFOREX'},
    "cointelegraph": {'id': '-1002337862544', 'topic': 'Topic 5' , 'topic_id' : '83' ,  'channel_id' : '@NEWSLIVEFOREX'},
    "coinmarketcap": {'id': '-1002337862544', 'topic': 'Topic 5' , 'topic_id' : '83' ,  'channel_id' : '@NEWSLIVEFOREX'},
    "reuters": {'id': '-1002337862544', 'topic': 'Topic 5' , 'topic_id' : '83' ,  'channel_id' : '@NEWSLIVEFOREX'},

}



@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id  # Get the chat ID (group, channel, or user)
    chat_title = message.chat.title if message.chat.type != 'private' else "Private Chat"
    topic_id = message.message_thread_id if hasattr(message, 'message_thread_id') else None  # For forum topics

    # Check if the chat type is a channel
    if message.chat.type == 'channel':
        channel_id = chat_id
    else:
        channel_id = None

    # Construct the response message
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

    # Optionally, log or send this information to the bot admin
    admin_id = 166946747  # Replace with your Telegram ID
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


def translate_text(text, target_language):
    url = "http://localhost:8000/translate"
    payload = {
        "text": text,
        "to": target_language
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("translatedText", "Translation failed.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


# Function to format messages
# Function to format messages with HTML parsing
def format_message(news_item):
    title = news_item['title']
    description = news_item['description']
    tag = news_item['tag']
    summary = news_item['summary']
    url = news_item['url']

    # Function to sanitize the URL
    def sanitize_url(url):
        return re.sub(r'\s+', '', url)  # Remove extra spaces

    clean_url = sanitize_url(url)

    # Create a clickable link in HTML format
    formatted_url = f'<a href="{clean_url}">{news_item["title"]}</a>'

    # Prepare the formatted message
    message = (
        # f"📢 <b>{title}</b>\n\n"
        # f"📝 {description}\n\n"
        # f"🏷️ Tag: {tag}\n\n"
        f"📢 <b>{title}</b>\n\n"

    )

    # Return the message and the formatted link separately
    return message, clean_url

# Send messages to specified group
def post_news_to_group(group_key, news_items , source):

    try:
    
        
        new_news =True
        
        group = GROUPS[group_key]
        group_id = group['id']
        topic_id = group.get('topic_id')  # Retrieve the topic ID if present
        channel_id = group.get('channel_id')  # Retrieve the channel ID if present

        for news_item in news_items:
            # Format the message and get the URL separately
            formatted_message, url = format_message(news_item)

            if (source == 'forexlive'):

                print(forex_live_latest_news[-1])
                print(forex_live_latest_news[0])


                forex_live_latest_news.append(url)
                if (forex_live_latest_news[-1] == forex_live_latest_news[0]):
                    new_news = False
                
                forex_live_latest_news.pop(0)
                print(new_news)



            if (source == 'dayliforex'):

                print(datilforex_latest_news[-1])
                print(datilforex_latest_news[0])


                datilforex_latest_news.append(url)
                if (datilforex_latest_news[-1] == datilforex_latest_news[0]):
                    new_news = False
                
                datilforex_latest_news.pop(0)
                print(new_news)


            if (source == 'myfxbook'):

                print(myfxbook_latest_news[-1])
                print(myfxbook_latest_news[0])


                myfxbook_latest_news.append(url)
                if (myfxbook_latest_news[-1] == myfxbook_latest_news[0]):
                    new_news = False
                
                myfxbook_latest_news.pop(0)
                print(new_news)


            # if (source == 'coinpotato'):

            #     print(coinpotato_lastest_news[-1])
            #     print(coinpotato_lastest_news[0])


            #     coinpotato_lastest_news.append(url)
            #     if (coinpotato_lastest_news[-1] == coinpotato_lastest_news[0]):
            #         new_news = False
                
            #     coinpotato_lastest_news.pop(0)
            #     print(new_news)

            if (source == 'cointelegraph'):

                print(cointelegraph_lastest_news[-1])
                print(cointelegraph_lastest_news[0])


                cointelegraph_lastest_news.append(url)
                if (cointelegraph_lastest_news[-1] == cointelegraph_lastest_news[0]):
                    new_news = False
                
                cointelegraph_lastest_news.pop(0)
                print(new_news)        


            if (source == 'coinmarketcap'):

                print(coinmarketcap_lastest_news[-1])
                print(coinmarketcap_lastest_news[0])


                coinmarketcap_lastest_news.append(url)
                if (coinmarketcap_lastest_news[-1] == coinmarketcap_lastest_news[0]):
                    new_news = False
                
                coinmarketcap_lastest_news.pop(0)
                print(new_news)

            if (source == 'reuters'):

                print(reuters_lastest_news[-1])
                print(reuters_lastest_news[0])


                reuters_lastest_news.append(url)
                if (reuters_lastest_news[-1] == reuters_lastest_news[0]):
                    new_news = False
                
                reuters_lastest_news.pop(0)
                print(new_news)


            
            # Translate the message text (excluding the URL)
            translated_message = translate_text(formatted_message, "fa")
            
            # Add the URL at the end of the translated message
            url = f'<a href="{url}">{translated_message}</a>'

            # final_message = f"{translated_message}\n\n{url}"
            final_message = f"{url}"

            
            print(f"Final Message: {url}")
            
            if (new_news) :

                
                # Determine the target destination
                if topic_id:
                    bot.send_message(group_id, final_message,parse_mode="HTML", message_thread_id=topic_id)
                if channel_id:
                    bot.send_message(channel_id, final_message, parse_mode="HTML")
                # else:
                #     bot.send_message(group_id, final_message, parse_mode='Markdown')
    except:
        print('error')

# Command to get group IDs
@bot.message_handler(commands=['get_groups'])
def get_groups(message):
    response = "\n".join([f"{key}: {value['id']}" for key, value in GROUPS.items()])
    bot.reply_to(message, f"Group IDs:\n{response}")

# Jobs for different groups
def job_group_1():
    news = scrape_news_topic_1()
    post_news_to_group('forexlive', news , 'forexlive')

def job_group_2():
    news = scrape_news_topic_2()
    post_news_to_group('myfxbook', news ,'myfxbook')

def job_group_3():
    news = scrape_news_topic_3()
    post_news_to_group('dayliforex', news ,'dayliforex')

def job_group_4():
     news = scrape_news_topic_7()
     post_news_to_group('cointelegraph', news , 'cointelegraph')    

# def job_group_5():
#      news = scrape_news_topic_8()
#      post_news_to_group('coinpotato', news , 'coinpotato')

def job_group_6():
     news = scrape_news_topic_9()
     post_news_to_group('coinmarketcap', news , 'coinmarketcap')     

def job_group_7():
     news = scrape_news_topic_10()
     post_news_to_group('reuters', news , 'reuters')

# Schedule jobs
# schedule.every(1).hour.do(job_group_1)  # Every hour
# schedule.every(5).minutes.do(job_group_1) 
schedule.every(5).seconds.do(job_group_1) 
schedule.every(5).seconds.do(job_group_2) 
schedule.every(5).seconds.do(job_group_3) 
schedule.every(5).seconds.do(job_group_4) 
# schedule.every(5).seconds.do(job_group_5) 
schedule.every(5).seconds.do(job_group_6) 
schedule.every(5).seconds.do(job_group_7) 





# Run the scheduler in a separate thread
def run_scheduler():
    print('Scheduler runner is getting started')
    while True:
        print('Scheduler runner started')
        schedule.run_pending()
        time.sleep(1)

# Start scheduler thread
import threading
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

# Start the bot
bot.polling()

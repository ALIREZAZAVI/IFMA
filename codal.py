import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Bot

# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN = "7876883134:AAHcBp0BuHXGz_HdVuSl0PWMcUlFaEtq84A"
CHAT_ID = "@codalprice"  # آیدی کانال تلگرام

# تابع ارسال پیام به تلگرام
def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

# تنظیمات Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ذخیره آخرین ردیف
last_row_text = None

while True:
    try:
        driver.get("https://www.codal.ir/")  # لینک سایت
        
        # پیدا کردن اولین ردیف
        first_row = driver.find_element(By.XPATH, "//tr[@class='table__row ng-scope']")
        columns = first_row.find_elements(By.TAG_NAME, "td")
        
        if len(columns) >= 7:
            namad = columns[0].text.strip()
            company = columns[1].text.strip()
            title = columns[3].text.strip()
            code = columns[4].text.strip()
            send_time = columns[5].text.strip()
            publish_time = columns[6].text.strip()
            
            try:
                link_element = first_row.find_element(By.XPATH, ".//a[contains(@class, 'icon-file-eye')]")
                link = link_element.get_attribute("href")
            except:
                link = "لینکی یافت نشد"
            
            row_text = f"نماد: {namad}\nشرکت: {company}\nعنوان: {title}\nکد: {code}\nزمان ارسال: {send_time}\nزمان انتشار: {publish_time}"
            
            # اگر ردیف جدید بود، ارسال شود
            if row_text != last_row_text:
                full_message = f"{row_text}\n🔗 مشاهده اطلاعیه: {link}"
                send_telegram_message(full_message)
                last_row_text = row_text

    except Exception as e:
        print("خطا:", e)
    
    time.sleep(60)  # هر ۶۰ ثانیه بررسی شود
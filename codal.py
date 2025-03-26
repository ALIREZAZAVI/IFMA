import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import logging
import os

# تنظیمات لاگ‌گیری
logging.basicConfig(filename="codal_scraper.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN = "7876883134:AAHcBp0BuHXGz_HdVuSl0PWMcUlFaEtq84A"
CHAT_ID = "@codalprice"  # آیدی کانال تلگرام

# تابع ارسال پیام به تلگرام
def send_telegram_message(message):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=message)
        logging.info("✅ پیام جدید ارسال شد.")
    except Exception as e:
        logging.error(f"🚨 خطا در ارسال پیام تلگرام: {e}")

# ذخیره و بازیابی آخرین ردیف
LAST_ROW_FILE = "last_codal_row.txt"

def load_last_row():
    if os.path.exists(LAST_ROW_FILE):
        with open(LAST_ROW_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    return None

def save_last_row(row_text):
    with open(LAST_ROW_FILE, "w", encoding="utf-8") as file:
        file.write(row_text)

# مقدار اولیه آخرین ردیف
last_row_text = load_last_row()

# استفاده از Session برای بهینه‌سازی درخواست‌ها
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

while True:
    try:
        # دریافت صفحه
        response = session.get("https://www.codal.ir/", headers=headers, timeout=30)
        response.raise_for_status()  # در صورت خطای HTTP متوقف شود

        # پردازش HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # پیدا کردن اولین ردیف
        first_row = soup.select_one("tr.table__row.ng-scope")
        if not first_row:
            logging.warning("⚠️ هیچ ردیفی در صفحه پیدا نشد.")
            time.sleep(60)
            continue

        columns = first_row.find_all("td")
        if len(columns) >= 7:
            namad = columns[0].get_text(strip=True)
            company = columns[1].get_text(strip=True)
            title = columns[3].get_text(strip=True)
            code = columns[4].get_text(strip=True)
            send_time = columns[5].get_text(strip=True)
            publish_time = columns[6].get_text(strip=True)

            # استخراج لینک اطلاعیه
            link_element = first_row.select_one("a.icon-file-eye")
            link = "https://www.codal.ir" + link_element["href"] if link_element else "لینکی یافت نشد"

            row_text = f"نماد: {namad}\nشرکت: {company}\nعنوان: {title}\nکد: {code}\nزمان ارسال: {send_time}\nزمان انتشار: {publish_time}"

            # بررسی تغییرات
            if row_text != last_row_text:
                full_message = f"{row_text}\n🔗 مشاهده اطلاعیه: {link}"
                send_telegram_message(full_message)
                save_last_row(row_text)
                last_row_text = row_text
                logging.info("✅ پیام جدید ارسال شد.")

    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 خطا در درخواست به Codal: {e}")
    except Exception as e:
        logging.error(f"🚨 خطای غیرمنتظره: {e}")

    time.sleep(60)  # بررسی هر ۶۰ ثانیه

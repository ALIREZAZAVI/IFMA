import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# تنظیمات تلگرام
TELEGRAM_BOT_TOKEN = "7876883134:AAHcBp0BuHXGz_HdVuSl0PWMcUlFaEtq84A"
CHAT_ID = "@codalprice"  # آیدی کانال تلگرام

# تابع ارسال پیام به تلگرام
def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

# ذخیره آخرین ردیف
last_row_text = None

while True:
    try:
        # دریافت صفحه
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        response = requests.get("https://www.codal.ir/", headers=headers, timeout=10)
        response.raise_for_status()  # اگر خطای HTTP باشد، متوقف شود
        
        # پردازش HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # پیدا کردن اولین ردیف
        first_row = soup.select_one("tr.table__row.ng-scope")
        if not first_row:
            print("⚠️ ردیفی پیدا نشد")
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

            # استخراج لینک
            link_element = first_row.select_one("a.icon-file-eye")
            link = link_element["href"] if link_element else "لینکی یافت نشد"

            row_text = f"نماد: {namad}\nشرکت: {company}\nعنوان: {title}\nکد: {code}\nزمان ارسال: {send_time}\nزمان انتشار: {publish_time}"

            # اگر ردیف جدید بود، ارسال شود
            if row_text != last_row_text:
                full_message = f"{row_text}\n🔗 مشاهده اطلاعیه: {link}"
                send_telegram_message(full_message)
                last_row_text = row_text
                print("✅ پیام جدید ارسال شد")

    except Exception as e:
        print("🚨 خطا:", e)

    time.sleep(60)  # هر ۶۰ ثانیه بررسی شود

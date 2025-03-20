import asyncio
import websockets
import json
import requests

# اطلاعات WebSocket نوبیتکس
NOBITEX_WS_URL = "wss://ws.nobitex.ir/"
# اطلاعات تلگرام
TELEGRAM_BOT_TOKEN = "7876883134:AAHcBp0BuHXGz_HdVuSl0PWMcUlFaEtq84A"
TELEGRAM_CHAT_ID = "@NEWSLIVEFOREX"

# لیست ارزها
symbols = [
    {"symbol": "USDTIRT", "title": "تتر", "unit": "تومان"},
    {"symbol": "BTCIRT", "title": "بیتکوین", "unit": "تومان"},
    {"symbol": "SHIBIRT", "title": "شیبا", "unit": "تومان"},
    {"symbol": "LTCIRT", "title": "لایت کوین", "unit": "تومان"},
    {"symbol": "XRPIRT", "title": "ریپل", "unit": "تومان"},
    {"symbol": "BCHIRT", "title": "بیتکوین کش", "unit": "تومان"},
    {"symbol": "BNBIRT", "title": "بایننس کوین", "unit": "تومان"},
    {"symbol": "TRXIRT", "title": "ترون", "unit": "تومان"},
    {"symbol": "DOGEIRT", "title": "دوج کوین", "unit": "تومان"},
    {"symbol": "ADAIRT", "title": "کاردانو", "unit": "تومان"},
    {"symbol": "MKRIRT", "title": "میکر", "unit": "تومان"},
    {"symbol": "AVAXIRT", "title": "آوالانچ", "unit": "تومان"},
    {"symbol": "DOTIRT", "title": "پولکادات", "unit": "تومان"},
]

async def send_message_to_telegram(text):
    """ارسال پیام به تلگرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=payload)
        result = response.json()
        print("✅ پیام به تلگرام ارسال شد:", result)
    except Exception as e:
        print("❌ خطای ارسال پیام به تلگرام:", e)

async def connect_to_nobitex():
    """اتصال به وب‌سوکت نوبیتکس و دریافت قیمت ارزها"""
    while True:
        try:
            async with websockets.connect(NOBITEX_WS_URL) as ws:
                print("✅ WebSocket متصل شد!")

                # ارسال احراز هویت (در صورتی که API نیاز داشته باشد)
                auth_message = {"method": "login", "params": {"api_token": API_TOKEN}}
                await ws.send(json.dumps(auth_message))

                # ارسال درخواست اشتراک به کانال‌های قیمتی
                subscribe_message = {
                    "method": "subscribe",
                    "params": {
                        "channels": [f"ticker.{s['symbol']}" for s in symbols]
                    },
                }
                await ws.send(json.dumps(subscribe_message))

                # ارسال پینگ هر 30 ثانیه برای زنده نگه‌داشتن اتصال
                async def ping():
                    while True:
                        await asyncio.sleep(30)
                        await ws.send(json.dumps({"method": "ping"}))
                        print("📡 Ping ارسال شد.")

                asyncio.create_task(ping())

                # پردازش پیام‌های دریافت‌شده
                async for message in ws:
                    data = json.loads(message)

                    if "data" not in data:
                        continue

                    text_message = "📢 *قیمت لحظه‌ای ارزها:*\n"
                    for s in symbols:
                        price_data = data["data"].get(s["symbol"])
                        if price_data:
                            text_message += f"⚡ *{s['title']}:* {price_data['last']} {s['unit']}\n"

                    # ارسال پیام به تلگرام
                    await send_message_to_telegram(text_message)

        except Exception as e:
            print(f"❌ خطای WebSocket: {e}")
            print("⏳ تلاش مجدد در 5 ثانیه...")
            await asyncio.sleep(5)  # تلاش مجدد پس از 5 ثانیه

if __name__ == "__main__":
    asyncio.run(connect_to_nobitex())

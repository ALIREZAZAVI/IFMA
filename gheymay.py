import asyncio
import websockets
import json
import requests

# اطلاعات اتصال
WS_URL = "wss://wss.nobitex.ir/connection/websocket"
TELEGRAM_BOT_TOKEN = "7876883134:AAHcBp0BuHXGz_HdVuSl0PWMcUlFaEtq84A"
TELEGRAM_CHAT_ID = "@NEWSLIVEFOREX"  # مقدار صحیح برای ارسال به کانال تلگرام
RECONNECT_DELAY = 5  # مدت زمان انتظار قبل از تلاش مجدد
PING_INTERVAL = 30  # فاصله زمانی برای ارسال پینگ

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

# تابع ارسال پیام به تلگرام
def send_message_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        print("✅ پیام به تلگرام ارسال شد:", result)
    except Exception as e:
        print("❌ خطای ارسال پیام به تلگرام:", e)

# تابع اصلی WebSocket
async def connect_websocket():
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                print("✅ WebSocket متصل شد!")

                # ارسال درخواست اشتراک (subscribe)
                subscribe_message = {
                    "method": "subscribe",
                    "params": {
                        "channels": [f"ticker.{s['symbol']}" for s in symbols],
                    },
                }
                await ws.send(json.dumps(subscribe_message))

                # ارسال پینگ به صورت متناوب
                async def send_ping():
                    while True:
                        try:
                            await asyncio.sleep(PING_INTERVAL)
                            await ws.send(json.dumps({"method": "ping"}))
                            print("📡 Ping ارسال شد.")
                        except:
                            break  # در صورت قطع ارتباط، حلقه متوقف می‌شود

                asyncio.create_task(send_ping())

                # دریافت و پردازش پیام‌ها
                async for message in ws:
                    try:
                        data = json.loads(message)
                        if not data or "data" not in data:
                            continue

                        message_text = "📢 *قیمت لحظه‌ای ارزها:*\n"
                        for s in symbols:
                            price_data = data["data"].get(s["symbol"])
                            if price_data:
                                message_text += f". *{s['title']}:* {price_data['last']} {s['unit']}\n"

                        send_message_to_telegram(message_text)

                    except Exception as e:
                        print("⚠️ خطا در پردازش پیام:", e)

        except Exception as e:
            print(f"❌ خطای WebSocket: {e}")
            print(f"⏳ تلاش مجدد در {RECONNECT_DELAY} ثانیه...")
            await asyncio.sleep(RECONNECT_DELAY)

# اجرای WebSocket به صورت async
async def main():
    await connect_websocket()

if __name__ == "__main__":
    asyncio.run(main())

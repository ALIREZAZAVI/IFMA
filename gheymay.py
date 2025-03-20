export default {
  async fetch(request, env) {
    return new Promise((resolve, reject) => {
      const wsUrl = "wss://wss.nobitex.ir/connection/websocket";
      const telegramBotToken = "7876883134:AAHcBp0BuHXGz_HdVuSl0PWMcUlFaEtq84A";
      const telegramChatID = "@NEWSLIVEFOREX"; // مقدار صحیح برای ارسال به کانال تلگرام
      let ws;
      let reconnectAttempts = 0;
      const maxReconnectAttempts = 10;
      const reconnectInterval = 5000;

      const symbols = [
        { symbol: "USDTIRT", title: "تتر", unit: "تومان" },
        { symbol: "BTCIRT", title: "بیتکوین", unit: "تومان" },
        { symbol: "SHIBIRT", title: "شیبا", unit: "تومان" },
        { symbol: "LTCIRT", title: "لایت کوین", unit: "تومان" },
        { symbol: "XRPIRT", title: "ریپل", unit: "تومان" },
        { symbol: "BCHIRT", title: "بیتکوین کش", unit: "تومان" },
        { symbol: "BNBIRT", title: "بایننس کوین", unit: "تومان" },
        { symbol: "TRXIRT", title: "ترون", unit: "تومان" },
        { symbol: "DOGEIRT", title: "دوج کوین", unit: "تومان" },
        { symbol: "ADAIRT", title: "کاردانو", unit: "تومان" },
        { symbol: "MKRIRT", title: "میکر", unit: "تومان" },
        { symbol: "AVAXIRT", title: "آوالانچ", unit: "تومان" },
        { symbol: "DOTIRT", title: "پولکادات", unit: "تومان" },
      ];

      function connectWebSocket() {
        if (reconnectAttempts >= maxReconnectAttempts) {
          console.error("❌ حداکثر تلاش برای اتصال مجدد انجام شد. متوقف شد.");
          return;
        }

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log("✅ WebSocket متصل شد!");
          reconnectAttempts = 0; // ریست شمارش تلاش‌ها

          // ارسال درخواست subscribe
          const subscribeMessage = {
            method: "subscribe",
            params: {
              channels: symbols.map((s) => `ticker.${s.symbol}`),
            },
          };
          ws.send(JSON.stringify(subscribeMessage));

          // ارسال Ping برای جلوگیری از قطع اتصال
          setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ method: "ping" }));
              console.log("📡 Ping ارسال شد.");
            }
          }, 30000);
        };

        ws.onmessage = async (event) => {
          try {
            const data = JSON.parse(event.data);
            if (!data || !data.data) return;

            let message = "📢 *قیمت لحظه‌ای ارزها:*\n";
            for (const s of symbols) {
              const priceData = data.data[s.symbol];
              if (priceData) {
                message += `🔹 *${s.title}:* ${priceData.last} ${s.unit}\n`;
              }
            }

            await sendMessageToTelegram(message);
          } catch (error) {
            console.error("⚠️ خطا در پردازش پیام:", error);
          }
        };

        ws.onerror = (error) => {
          console.error("❌ خطای WebSocket:", error);
        };

        ws.onclose = (event) => {
          console.warn(`⚠️ WebSocket قطع شد (کد: ${event.code}، دلیل: ${event.reason})`);
          reconnectAttempts++;
          setTimeout(connectWebSocket, reconnectInterval);
        };
      }

      async function sendMessageToTelegram(text) {
        const url = `https://api.telegram.org/bot${telegramBotToken}/sendMessage`;
        const payload = {
          chat_id: telegramChatID,
          text: text,
          parse_mode: "Markdown",
        };

        try {
          const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });

          const result = await response.json();
          console.log("✅ پیام به تلگرام ارسال شد:", result);
        } catch (error) {
          console.error("❌ خطای ارسال پیام به تلگرام:", error);
        }
      }

      connectWebSocket();

      // Cloudflare Worker باید یک Response معتبر برگرداند
      resolve(new Response("WebSocket worker is running..."));
    });
  },
};

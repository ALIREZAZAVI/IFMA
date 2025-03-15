import http from 'http';
import fetch from 'node-fetch';

const telegramAuthToken = `7626220362:AAHP1a0zWjLRdmpzqfnbf2iXPd1iX538alI`;
const webhookEndpoint = "/endpoint";
const channelId = "-1002337862544";

const server = http.createServer(async (req, res) => {
  let url = new URL(req.url, `http://${req.headers.host}`);
  let path = url.pathname;
  let method = req.method;
  let workerUrl = `http://${req.headers.host}`;

  if (method === "POST" && path === webhookEndpoint) {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
    });

    req.on('end', async () => {
      try {
        const update = JSON.parse(body);
        await processUpdate(update);
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end("Ok");
      } catch (error) {
        console.error("Error processing update:", error);
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end("Error");
      }
    });

  } else if (method === "GET" && path === "/set") {
    try {
      const url = `https://api.telegram.org/bot${telegramAuthToken}/setWebhook?url=${workerUrl}${webhookEndpoint}`;
      const response = await fetch(url);

      if (response.ok) {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end("Webhook set successfully");
      } else {
        res.writeHead(response.status);
        res.end("Failed to set webhook");
      }
    } catch (error) {
      console.error("Error setting webhook:", error);
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end("Internal Server Error");
    }

  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end("Not found");
  }
});

server.listen(3000, () => {
  console.log('Server is running on port 3000');
});

async function processUpdate(update) {
  if ("message" in update) {
    const userText = update.message.text;

    if (userText === "/start") {
      try {
        let apiResponse = await fetch("https://brsapi.ir/FreeTsetmcBourseApi/Api_Free_Gold_Currency.json");

        if (!apiResponse.ok) {
          throw new Error(`Error fetching data: ${apiResponse.statusText}`);
        }

        const data = await apiResponse.json();

        let responseText = "*📊 قیمت طلا، ارز و رمزارزها:*\n\n";
        
        if (data.gold && data.gold.length > 0) {
          responseText += "*💰 قیمت طلا:*\n";
          data.gold.forEach(item => {
            responseText += `- *${item.name}*: ${item.price.toLocaleString()} تومان\n`;
          });
        }

        if (data.currency && data.currency.length > 0) {
          responseText += "\n*💵 نرخ ارز:*\n";
          data.currency.forEach(item => {
            responseText += `- *${item.name}*: ${item.price.toLocaleString()} تومان\n`;
          });
        }

        if (data.cryptocurrency && data.cryptocurrency.length > 0) {
          responseText += "\n*₿ قیمت رمزارزها:*\n";
          data.cryptocurrency.forEach(item => {
            responseText += `- *${item.name}*: ${item.price.toLocaleString()} دلار\n`;
          });
        }

        const encodedResponseText = encodeURIComponent(responseText);

        const telegramUrl = `https://api.telegram.org/bot${telegramAuthToken}/sendMessage?chat_id=${channelId}&text=${encodedResponseText}&parse_mode=Markdown`;
        const telegramResponse = await fetch(telegramUrl);

        if (!telegramResponse.ok) {
          throw new Error(`Error sending message: ${telegramResponse.statusText}`);
        }
      } catch (error) {
        console.error("Error fetching and sending data:", error);
      }
    }
  }
}

const telegramAuthToken = `7626220362:AAHP1a0zWjLRdmpzqfnbf2iXPd1iX538alI`;
const webhookEndpoint = "/endpoint";
const channelId = "-1002337862544";

addEventListener("fetch", event => {
  event.respondWith(handleIncomingRequest(event));
});

async function handleIncomingRequest(event) {
  let url = new URL(event.request.url);
  let path = url.pathname;
  let method = event.request.method;
  let workerUrl = `${url.protocol}//${url.host}`;

  if (method === "POST" && path === webhookEndpoint) {
    const update = await event.request.json();
    event.waitUntil(processUpdate(update));
    return new Response("Ok");
  } else if (method === "GET" && path === "/set") {
    const url = `https://api.telegram.org/bot${telegramAuthToken}/setWebhook?url=${workerUrl}${webhookEndpoint}`;

    const response = await fetch(url);

    if (response.ok) {
      return new Response("Webhook set successfully", { status: 200 });
    } else {
      return new Response("Failed to set webhook", { status: response.status });
    }
  } else {
    return new Response("Not found", { status: 404 });
  }
}

async function processUpdate(update) {
  if ("message" in update) {
    const userText = update.message.text;

    if (userText === "/start") {
      let apiResponse = await fetch("https://brsapi.ir/FreeTsetmcBourseApi/Api_Free_Gold_Currency.json");

      if (!apiResponse.ok) {
        throw new Error(`Error fetching data: ${apiResponse.statusText}`);
      }

      const data = await apiResponse.json();

      let responseText = "*Gold Prices:*\n";
      data.gold.forEach(item => {
        responseText += `- *${item.name}*: ${item.price.toLocaleString()} T\n`;
      });

      responseText += "\n*Currency Exchange Rates:*\n";
      data.currency.forEach(item => {
        responseText += `- *${item.name}*: ${item.price.toLocaleString()} T\n`;
      });

      responseText += "\n*Cryptocurrency Prices:*\n";
      data.cryptocurrency.forEach(item => {
        responseText += `- *${item.name}*: ${item.price.toLocaleString()} USD\n`;
      });

      const encodedResponseText = encodeURIComponent(responseText);

      const telegramUrl = `https://api.telegram.org/bot${telegramAuthToken}/sendMessage?chat_id=${channelId}&text=${encodedResponseText}&parse_mode=Markdown`;
      const telegramResponse = await fetch(telegramUrl);

      if (!telegramResponse.ok) {
        throw new Error(`Error sending message: ${telegramResponse.statusText}`);
      }
    }
  }
}

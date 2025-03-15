import http from 'http';
import fetch from 'node-fetch';

const telegramAuthToken = '7626220362:AAHP1a0zWjLRdmpzqfnbf2iXPd1iX538alI';
const webhookEndpoint = "/endpoint";
const channelId = "-1002337862544";
const PORT = 3000;

function findAvailablePort(port) {
    return new Promise((resolve) => {
        const server = http.createServer();
        server.listen(port, () => {
            server.close(() => resolve(port));
        });
        server.on("error", () => {
            resolve(null);
        });
    });
}

async function startServer() {
    let availablePort = await findAvailablePort(PORT);
    if (!availablePort) {
        availablePort = Math.floor(3000 + Math.random() * 1000); // پورت تصادفی
        console.log(`⚠️ Port ${PORT} is in use. Using port ${availablePort} instead.`);
    }

    const server = http.createServer(async (req, res) => {
        let url = new URL(req.url, `http://${req.headers.host}`);
        let path = url.pathname;
        let method = req.method;

        if (method === "POST" && path === webhookEndpoint) {
            let body = '';
            req.on('data', chunk => { body += chunk; });

            req.on('end', async () => {
                try {
                    const update = JSON.parse(body);
                    await processUpdate(update);
                    res.writeHead(200, { 'Content-Type': 'text/plain' });
                    res.end("Ok");
                } catch (error) {
                    console.error("Error processing update:", error);
                    res.writeHead(500);
                    res.end("Internal Server Error");
                }
            });
        } else if (method === "GET" && path === "/set") {
            try {
                let workerUrl = `http://${req.headers.host}`;
                const url = `https://api.telegram.org/bot${telegramAuthToken}/setWebhook?url=${workerUrl}${webhookEndpoint}`;
                const response = await fetch(url);

                if (response.ok) {
                    res.writeHead(200, { 'Content-Type': 'text/plain' });
                    res.end("Webhook set successfully");
                } else {
                    throw new Error(`Failed to set webhook: ${response.statusText}`);
                }
            } catch (error) {
                console.error("Error setting webhook:", error);
                res.writeHead(500);
                res.end("Internal Server Error");
            }
        } else {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end("Not found");
        }
    });

    server.listen(availablePort, () => {
        console.log(`🚀 Server is running on port ${availablePort}`);
    });
}

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

                let responseText = "*📊 Gold Prices:*\n";
                data.gold.forEach(item => {
                    responseText += `- *${item.name}*: ${item.price.toLocaleString()} T\n`;
                });

                responseText += "\n*💱 Currency Exchange Rates:*\n";
                data.currency.forEach(item => {
                    responseText += `- *${item.name}*: ${item.price.toLocaleString()} T\n`;
                });

                responseText += "\n*₿ Cryptocurrency Prices:*\n";
                data.cryptocurrency.forEach(item => {
                    responseText += `- *${item.name}*: ${item.price.toLocaleString()} USD\n`;
                });

                const encodedResponseText = encodeURIComponent(responseText);
                const telegramUrl = `https://api.telegram.org/bot${telegramAuthToken}/sendMessage?chat_id=${channelId}&text=${encodedResponseText}&parse_mode=Markdown`;

                const telegramResponse = await fetch(telegramUrl);

                if (!telegramResponse.ok) {
                    throw new Error(`Error sending message: ${telegramResponse.statusText}`);
                }

            } catch (error) {
                console.error("Error processing update:", error);
            }
        }
    }
}

startServer();

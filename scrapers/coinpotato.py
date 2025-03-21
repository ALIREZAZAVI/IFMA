import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from itertools import cycle
import time

def scrape_news_topic_8():
    # --- Configuration ---

    # Advanced headers mimicking a real browser
    HEADERS = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/115.0.0.0 Safari/537.36'),
        'Accept': ('text/html,application/xhtml+xml,application/xml;'
                   'q=0.9,image/webp,*/*;q=0.8'),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive'
    }

    # Free proxies taken from free-proxy-list.net (example list)
    PROXIES_LIST = [
        "http://65.108.159.129:8080",
        "http://13.36.104.85:80",
        "http://13.36.87.105:3128",
        "http://3.126.147.182:80",
        "http://43.202.154.212:80",
        "http://35.76.62.196:80",
        "http://104.225.220.233:80",   # US, elite proxy
        "http://18.223.25.15:80",       # US, elite proxy
        "http://44.219.175.186:80",      # US, elite proxy
        "http://3.129.184.210:80",       # US, elite proxy
        "http://3.141.217.225:80",       # US, elite proxy
        "http://47.254.36.213:8443"      # US, elite proxy
        # Add more proxies as needed
    ]

    # Create a cycle iterator for the proxy list
    proxies_cycle = cycle(PROXIES_LIST) if PROXIES_LIST else None

    # URL to fetch
    base_url = "https://cryptopotato.com"
    url = f"{base_url}/crypto-news"

    # Retry configuration
    MAX_RETRIES = 5
    DELAY_SECONDS = 2

    # Create a persistent session with custom headers
    session = requests.Session()
    session.headers.update(HEADERS)

    page_content = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # If proxies are available, use the next proxy from the cycle
            if proxies_cycle:
                current_proxy = next(proxies_cycle)
                session.proxies.update({
                    'http': current_proxy,
                    'https': current_proxy,
                })
                print(f"Attempt {attempt}: Using proxy {current_proxy}")
            else:
                print(f"Attempt {attempt}: No proxy in use.")

            # Make the GET request with a timeout
            response = session.get(url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
            print(f"Success on attempt {attempt}!")
            page_content = response.text
            break  # exit the loop if request is successful
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed with error: {e}")
            time.sleep(DELAY_SECONDS)

    if page_content is None:
        print("All attempts failed. Could not fetch the page.")
        return None

    # Parse the main news page
    soup = BeautifulSoup(page_content, 'html.parser')

    # Find the first news article
    first_news = soup.select_one("h3.rpwe-title a")
    if not first_news:
        print("No news link found.")
        return None

    # Extract the link and fix it if relative
    link = first_news['href']
    article_url = link if link.startswith("http") else urljoin(base_url, link)

    # Fetch the specific news article page
    try:
        news_response = session.get(article_url, timeout=10)
        news_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch news article page: {e}")
        return None

    news_soup = BeautifulSoup(news_response.text, 'html.parser')

    # Extract title
    title_element = news_soup.select_one("div.page-title h1")
    title = title_element.text.strip() if title_element else "Title not found"

    # Extract all <p> tags as descriptions
    p_tags = news_soup.find_all("p")
    descriptions = [p.text.strip() for p in p_tags]

    crypto_tag = [
        "#کریپتو", "#ارز_دیجیتال", "#بیت_کوین", "#اتریوم", "#سرمایه_گذاری",
        "#رمزارز", "#ترید", "#ماینینگ", "#تحلیل_بازار", "#بلاکچین",
        "#کریپتوکارنسی", "#ارزهای_دیجیتال", "#بازار_مالی", "#پول_دیجیتال",
        "#معاملات_ارز_دیجیتال", "#سرمایه_گذاری_آنلاین", "#اخبار_جهانی", "#سرمایه_گذاری_آنلاین"
    ]

    # Prepare the news object
    news = [{
        "title": title,
        "description": descriptions,
        "tag": 'crypto_tag',
        "source": "CryptoPotato",
        "link": "article_url"
    }]

    print(news)
    return news

# Example usage
if __name__ == "__main__":
    news = scrape_news_topic_8()
    if news:
        print(news)

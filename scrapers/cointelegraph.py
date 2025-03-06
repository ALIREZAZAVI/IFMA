import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests


def scrape_news_topic_7():
   
    base_url = "https://cointelegraph.com/markets"
    markets_url = base_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://cointelegraph.com/markets',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        # Fetch the markets page directly
        scraper = cloudscraper.create_scraper()
        response = scraper.get(markets_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first news article link (directly from <a> tag)
        first_news = soup.select_one("a.post-card-inline__title-link")
        if not first_news:
            print("No news link found.")
            return None

        # Safely extract the link from the <a> tag
        link = first_news.get('href')
        if not link:
            print("No href attribute found.")
            return None

        article_url = link if link.startswith("http") else urljoin(base_url, link)

        # Fetch the specific news article page
        news_response = scraper.get(article_url, headers=headers)
        news_response.raise_for_status()
        news_soup = BeautifulSoup(news_response.text, 'html.parser')

        # Extract title
        title_element = news_soup.select_one("h1.post__title")
        title = title_element.text.strip() if title_element else "Title not found"

        # Extract all paragraphs (combine all <p> tags)
        description_elements = news_soup.select("p")
        if description_elements:
            description = " ".join([element.text.strip() for element in description_elements])
        else:
            description = "Description not available"
        
        crypto_tag = [
            "#کریپتو", "#ارز_دیجیتال", "#بیت_کوین", "#اتریوم", "#سرمایه_گذاری",
            "#رمزارز", "#ترید", "#ماینینگ", "#تحلیل_بازار", "#بلاکچین",
            "#کریپتوکارنسی", "#ارزهای_دیجیتال", "#بازار_مالی", "#پول_دیجیتال",
            "#معاملات_ارز_دیجیتال", "#سرمایه_گذاری_آنلاین", "#اخبار_جهانی", "#سرمایه_گذاری_آنلاین"
        ]

        # Prepare the news object
        news = [{
            "title": title,
            "description": description,
            "tag": "crypto_tag",
            "source": "CoinTelegraph",
            "link": article_url,
            'summary': 'i have Diarrhea',
             'url' :article_url,
       
        }]
        print(news)

        return news

        # Print the news
        for article in news:
            print(f"Title: {article['title']}")
            print(f"Description: {article['description']}")
            print(f"Source: {article['source']}")
            print(f"Tags: {', '.join(article['tag'])}")
            print(f"Link: {article['link']}")

    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    scrape_news_topic_7()
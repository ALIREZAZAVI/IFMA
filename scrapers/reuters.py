import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrape_news_topic_10():
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    base_url = "https://www.reuters.com/markets/cryptocurrency"

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        first_news = soup.select_one("a[data-testid='TitleLink']")
        if not first_news:
            print("No news link found.")
            return []

        link = first_news.get('href')
        article_url = urljoin(base_url, link) if link else None
        if not article_url:
            print("No valid article URL found.")
            return []

        news_response = requests.get(article_url, headers=headers)
        news_response.raise_for_status()
        news_soup = BeautifulSoup(news_response.content, 'html.parser')

        title_element = news_soup.select_one("h1")
        title = title_element.text.strip() if title_element else "Title not found"

        return [{
            "title": title,
            "description": "",
            "tag": "Reuters",
            "summary": "",
            "url": article_url
        }]

    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP request error: {e}")
        return []
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return []

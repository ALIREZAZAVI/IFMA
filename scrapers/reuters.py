import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_news_topic_9():
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    base_url = "https://www.reuters.com/markets/cryptocurrency"

    try:
        # دریافت صفحه اصلی اخبار
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # پیدا کردن اولین لینک خبر با استفاده از data-testid
        first_news = soup.select_one("a[data-testid='TitleLink']")
        if not first_news:
            print("No news link found.")
            return None

        # استخراج لینک
        link = first_news.get('href')
        article_url = urljoin(base_url, link) if link else None
        if not article_url:
            print("No valid article URL found.")
            return None

        # دریافت صفحه خبر
        news_response = requests.get(article_url, headers=headers)
        news_response.raise_for_status()
        news_soup = BeautifulSoup(news_response.content, 'html.parser')

        # استخراج عنوان خبر
        title_element = news_soup.select_one("h1")
        title = title_element.text.strip() if title_element else "Title not found"

        # تلاش برای پیدا کردن article
        article_div = news_soup.select_one("article")
        if not article_div:
            print("No article div found. Check the HTML structure!")
            return None

        # نمایش اطلاعات خبر
        print(f"🔹 Title: {title}\n")
        print(f"🔗 Link: {article_url}")

        
   


        return {
         
            "description": 'description',
            "tag": "tag",
            "summary": 'summary',
            'url' :article_url,
            "source": 'reuters',
            "title": title,
            "link": article_url
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP request error: {e}")
        return None
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None

# اجرای تابع
if __name__ == "__main__":
    scrape_news_topic_9()
